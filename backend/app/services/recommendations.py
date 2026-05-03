# Backend Recommendation Engine Service

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User, Course, University, UserInteraction, Recommendation
from app.utils.embeddings import EmbeddingService, SemanticMatcher, ChromaVectorDB
from app.utils.calculations import EngagementScorer
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# RECOMMENDATION ENGINE
# ============================================================================

class RecommendationEngine:
    """AI-powered course and university recommendation system."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.semantic_matcher = SemanticMatcher(self.embedding_service)
        self.vector_db = ChromaVectorDB()
        self.engagement_scorer = EngagementScorer()

    # ========================================================================
    # COURSE RECOMMENDATIONS
    # ========================================================================

    def recommend_courses(
        self,
        user: User,
        db: Session,
        limit: int = 10,
        use_semantic_search: bool = True,
    ) -> List[Dict[str, Any]]:
        """Recommend courses based on user profile using ML + semantic search."""

        logger.info(f"🎓 Generating course recommendations for user {user.id}")

        # 1. Get user profile description for semantic matching
        user_profile_desc = self.semantic_matcher.create_user_profile_description(user)
        logger.debug(f"User profile: {user_profile_desc[:100]}...")

        # 2. Semantic search for similar courses
        if use_semantic_search:
            try:
                similar_courses = self.vector_db.search(user_profile_desc, limit * 3)
                logger.debug(f"Found {len(similar_courses)} semantically similar courses")
            except Exception as e:
                logger.warning(f"Semantic search failed, falling back to basic search: {e}")
                similar_courses = []
        else:
            similar_courses = []

        # 3. Query all courses from DB (fallback + comprehensive)
        all_courses = db.query(Course).limit(limit * 2).all()

        # 4. Score & rank courses
        scored_courses = []
        for course in all_courses:
            # Base score from semantic similarity (if found)
            semantic_score = 0.0
            for sim_course in similar_courses:
                if sim_course.get('metadata', {}).get('course_id') == course.id:
                    semantic_score = sim_course.get('similarity_score', 0.5)
                    break

            # Match score based on user preferences
            match_score = self._calculate_course_match_score(user, course, semantic_score)

            # Eligibility check
            is_eligible = self._check_course_eligibility(user, course)

            scored_courses.append({
                'course_id': course.id,
                'name': course.name,
                'university': course.university.name if course.university else 'Unknown',
                'field': course.field_of_study,
                'country': course.university.country if course.university else 'Unknown',
                'total_cost': course.total_tuition_cost,
                'duration_months': course.duration_months,
                'intake_per_year': course.intake_per_year,
                'required_cgpa': course.min_cgpa_required,
                'match_score': match_score,
                'semantic_score': semantic_score,
                'is_eligible': is_eligible,
                'roi_percent': self._estimate_course_roi(course),
                'salary_year_1': course.avg_salary_year_1,
                'salary_year_5': course.avg_salary_year_5,
            })

        # 5. Sort by match score
        scored_courses.sort(key=lambda x: x['match_score'], reverse=True)

        # 6. Store recommendations in DB
        for idx, scored_course in enumerate(scored_courses[:limit]):
            recommendation = Recommendation(
                user_id=user.id,
                course_id=scored_course['course_id'],
                recommendation_score=int(scored_course['match_score']),
                factors={
                    'semantic_similarity': float(scored_course['semantic_score']),
                    'field_match': 0.2,  # placeholder
                    'country_preference': 0.15,
                    'financial_fit': 0.15,
                    'academic_fit': 0.2,
                    'eligibility_bonus': 0.3 if scored_course['is_eligible'] else 0.0,
                },
                effectiveness_viewed=False,
            )
            db.add(recommendation)

        db.commit()
        logger.info(f"✓ Generated {len(scored_courses[:limit])} recommendations for user {user.id}")

        return scored_courses[:limit]

    def _calculate_course_match_score(self, user: User, course: Course, semantic_similarity: float) -> float:
        """Calculate match score (0-100) between user and course."""

        score = semantic_similarity * 30  # Base 30% from semantic match

        # Field of study match (+25%)
        if user.preferred_fields and course.field_of_study in user.preferred_fields:
            score += 25
        elif course.field_of_study in ['Computer Science', 'Data Science', 'Engineering']:
            score += 10  # Default popular fields

        # Country preference match (+20%)
        if user.preferred_countries and course.university and course.university.country in user.preferred_countries:
            score += 20

        # Academic fit (+15%)
        if course.min_cgpa_required and user.current_cgpa >= course.min_cgpa_required:
            score += 15
        elif user.current_cgpa >= 3.5:
            score += 10

        # Financial fit (+10%)
        max_loan = user.annual_income * 1.5
        if course.total_tuition_cost <= max_loan * 3:
            score += 10

        return min(score, 100)

    def _check_course_eligibility(self, user: User, course: Course) -> bool:
        """Check if user is academically eligible for course."""

        if course.min_cgpa_required and user.current_cgpa < course.min_cgpa_required:
            return False

        if course.min_gre_required and (not user.gre_score or user.gre_score < course.min_gre_required):
            return False

        return True

    def _estimate_course_roi(self, course: Course) -> float:
        """Estimate 5-year ROI for a course."""

        if not course.avg_salary_year_1 or not course.avg_salary_year_5:
            return 0.0

        # Simple ROI: (5-year earnings - cost) / cost * 100
        salary_avg = (course.avg_salary_year_1 + course.avg_salary_year_5) / 2
        cumulative_earnings = salary_avg * 5 * 0.7  # 70% available after living expenses

        roi = ((cumulative_earnings - course.total_tuition_cost) / course.total_tuition_cost) * 100

        return max(0, min(roi, 200))  # Cap between 0-200%

    # ========================================================================
    # UNIVERSITY RECOMMENDATIONS
    # ========================================================================

    def recommend_universities(
        self,
        user: User,
        db: Session,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Recommend universities based on rankings and user preferences."""

        logger.info(f"🎓 Generating university recommendations for user {user.id}")

        universities = db.query(University).limit(limit * 2).all()

        scored_universities = []
        for uni in universities:
            score = 0.0

            # Ranking score (top 100 universities get higher scores)
            if uni.qs_ranking:
                ranking_score = max(0, 100 - uni.qs_ranking / 10)
                score += ranking_score * 0.3
            else:
                score += 30  # Default if no ranking

            # Country preference match (+25%)
            if user.preferred_countries and uni.country in user.preferred_countries:
                score += 25

            # Cost fit (+20%)
            avg_tuition = 5000000  # Default estimate
            if uni.average_tuition and uni.average_tuition <= user.annual_income * 2:
                score += 20

            # Salary outcomes (+25%)
            if uni.avg_graduate_salary:
                salary_score = min(25, (uni.avg_graduate_salary / 1500000) * 10)
                score += salary_score

            scored_universities.append({
                'university_id': uni.id,
                'name': uni.name,
                'country': uni.country,
                'qs_ranking': uni.qs_ranking or 'Unranked',
                'acceptance_rate': uni.acceptance_rate or 'N/A',
                'avg_tuition': uni.average_tuition or 'Variable',
                'avg_salary': uni.avg_graduate_salary or 'N/A',
                'match_score': min(score, 100),
            })

        scored_universities.sort(key=lambda x: x['match_score'], reverse=True)
        logger.info(f"✓ Generated {len(scored_universities[:limit])} university recommendations")

        return scored_universities[:limit]

    # ========================================================================
    # CAREER NAVIGATOR
    # ========================================================================

    def get_career_navigator(
        self,
        user: User,
        selected_field: str,
        selected_country: str,
        db: Session,
    ) -> Dict[str, Any]:
        """Provide career guidance and pathways."""

        logger.info(f"🎯 Generating career navigator for user {user.id} (field={selected_field}, country={selected_country})")

        # Get relevant courses
        relevant_courses = (
            db.query(Course)
            .join(University)
            .filter(
                Course.field_of_study == selected_field,
                University.country == selected_country,
            )
            .limit(5)
            .all()
        )

        pathways = [
            {
                'name': 'Fast Track (1 year)',
                'duration': 12,
                'cost': 2500000,
                'roi': 45,
                'description': 'Intensive postgraduate certificates'
            },
            {
                'name': 'Standard (2 years)',
                'duration': 24,
                'cost': 5000000,
                'roi': 75,
                'description': 'Master\'s degree programs'
            },
            {
                'name': 'Comprehensive (3-4 years)',
                'duration': 48,
                'cost': 8000000,
                'roi': 120,
                'description': 'Bachelors + internships'
            },
        ]

        # Determine best pathway based on user profile
        best_pathway = None
        if user.work_experience_years > 2:
            best_pathway = 'Fast Track (1 year)'
        elif user.current_degree in ['High School', 'BA', 'B.Sc']:
            best_pathway = 'Comprehensive (3-4 years)'
        else:
            best_pathway = 'Standard (2 years)'

        return {
            'selected_field': selected_field,
            'selected_country': selected_country,
            'recommended_pathway': best_pathway,
            'pathways': pathways,
            'relevant_universities': [
                {'name': c.university.name, 'qs_ranking': c.university.qs_ranking}
                for c in relevant_courses
            ],
            'job_market_outlook': f'High demand for {selected_field} professionals in {selected_country}',
            'estimated_salary_range': f'₹50-150L depending on experience',
            'next_steps': [
                f'Research top universities in {selected_country}',
                'Check visa and work permit requirements',
                'Calculate loan eligibility and ROI',
                'Submit course applications',
                'Prepare for standardized tests (GMAT, GRE, IELTS)',
            ],
        }


# Singleton instance
recommendation_engine = RecommendationEngine()
