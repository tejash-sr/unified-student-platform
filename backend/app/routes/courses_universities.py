# Courses and Universities API Routes

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.core.database import get_db
from app.models import Course, University, User
from app.core.security import get_current_user
from app.services.recommendations import recommendation_engine
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# ROUTERS
# ============================================================================

courses_router = APIRouter(prefix="/courses", tags=["Courses"])
universities_router = APIRouter(prefix="/universities", tags=["Universities"])
recommendations_router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

# ============================================================================
# COURSE ENDPOINTS
# ============================================================================

@courses_router.get("/search")
async def search_courses(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search courses by name, university, or field."""
    
    logger.info(f"🔍 Searching courses: query={q}, limit={limit}")
    
    courses = (
        db.query(Course)
        .join(University)
        .filter(
            or_(
                Course.name.ilike(f"%{q}%"),
                Course.field_of_study.ilike(f"%{q}%"),
                University.name.ilike(f"%{q}%"),
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": db.query(func.count(Course.id)).filter(
            or_(
                Course.name.ilike(f"%{q}%"),
                Course.field_of_study.ilike(f"%{q}%"),
                University.name.ilike(f"%{q}%"),
            )
        ).scalar(),
        "courses": [
            {
                "id": c.id,
                "name": c.name,
                "university": c.university.name if c.university else "Unknown",
                "field": c.field_of_study,
                "country": c.university.country if c.university else "Unknown",
                "total_cost": c.total_tuition_cost,
                "duration_months": c.duration_months,
                "roi_percent": (c.avg_salary_year_5 / c.total_tuition_cost * 5 * 100) if c.avg_salary_year_5 and c.total_tuition_cost else 0,
            }
            for c in courses
        ],
    }


@courses_router.get("/discover")
async def discover_courses(
    field: str = Query(None),
    country: str = Query(None),
    min_ranking: int = Query(None, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Discover courses with filters."""
    
    logger.info(f"🔎 Discovering courses: field={field}, country={country}, ranking={min_ranking}")
    
    query = db.query(Course).join(University)

    if field:
        query = query.filter(Course.field_of_study.ilike(f"%{field}%"))

    if country:
        query = query.filter(University.country == country)

    if min_ranking:
        query = query.filter(University.qs_ranking <= min_ranking)

    courses = query.limit(limit).all()

    return {
        "total": query.count(),
        "courses": [
            {
                "id": c.id,
                "name": c.name,
                "university": c.university.name if c.university else "Unknown",
                "field": c.field_of_study,
                "country": c.university.country if c.university else "Unknown",
                "ranking": c.university.qs_ranking if c.university else None,
                "total_cost": c.total_tuition_cost,
                "salary_year_1": c.avg_salary_year_1,
                "salary_year_5": c.avg_salary_year_5,
                "intake_per_year": c.intake_per_year,
                "roi_percent": (c.avg_salary_year_5 / c.total_tuition_cost * 5 * 100) if c.avg_salary_year_5 and c.total_tuition_cost else 0,
            }
            for c in courses
        ],
    }


@courses_router.get("/{course_id}")
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get detailed course information."""
    
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return {
        "id": course.id,
        "name": course.name,
        "university_id": course.university_id,
        "university": course.university.name if course.university else "Unknown",
        "field": course.field_of_study,
        "degree_type": course.degree_type,
        "description": course.course_description,
        "duration_months": course.duration_months,
        "total_cost": course.total_tuition_cost,
        "salary_year_1": course.avg_salary_year_1,
        "salary_year_5": course.avg_salary_year_5,
        "intake_per_year": course.intake_per_year,
        "admission_deadline": course.application_deadline,
        "min_cgpa": course.min_cgpa_required,
        "min_gre": course.min_gre_required,
        "min_gmat": course.min_gmat_required,
        "requirements": {
            "cgpa": course.min_cgpa_required,
            "gre": course.min_gre_required,
            "gmat": course.min_gmat_required,
            "ielts": course.min_ielts_required,
        },
    }

# ============================================================================
# UNIVERSITY ENDPOINTS
# ============================================================================

@universities_router.get("/search")
async def search_universities(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search universities by name or country."""
    
    logger.info(f"🔍 Searching universities: query={q}")
    
    universities = (
        db.query(University)
        .filter(
            or_(
                University.name.ilike(f"%{q}%"),
                University.country.ilike(f"%{q}%"),
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": db.query(func.count(University.id)).filter(
            or_(
                University.name.ilike(f"%{q}%"),
                University.country.ilike(f"%{q}%"),
            )
        ).scalar(),
        "universities": [
            {
                "id": u.id,
                "name": u.name,
                "country": u.country,
                "city": u.city,
                "qs_ranking": u.qs_ranking,
                "acceptance_rate": u.acceptance_rate,
                "avg_salary": u.avg_graduate_salary,
            }
            for u in universities
        ],
    }


@universities_router.get("/{university_id}")
async def get_university(university_id: int, db: Session = Depends(get_db)):
    """Get detailed university information."""
    
    university = db.query(University).filter(University.id == university_id).first()
    
    if not university:
        raise HTTPException(status_code=404, detail="University not found")

    return {
        "id": university.id,
        "name": university.name,
        "country": university.country,
        "city": university.city,
        "founded_year": university.founded_year,
        "qs_ranking": university.qs_ranking,
        "times_ranking": university.times_ranking,
        "shanghai_ranking": university.shanghai_ranking,
        "acceptance_rate": university.acceptance_rate,
        "avg_gpa_admitted": university.avg_admitted_gpa,
        "avg_gre_admitted": university.avg_admitted_gre,
        "avg_salary": university.avg_graduate_salary,
        "description": university.university_description,
        "courses_count": db.query(func.count(Course.id)).filter(Course.university_id == university_id).scalar(),
    }

# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@recommendations_router.get("/courses")
async def get_recommended_courses(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get AI-recommended courses for current user."""
    
    logger.info(f"🎓 Getting recommendations for user {current_user.id}")
    
    recommendations = recommendation_engine.recommend_courses(current_user, db, limit)
    
    return {
        "user_id": current_user.id,
        "total": len(recommendations),
        "courses": recommendations,
    }


@recommendations_router.post("/career-navigator")
async def get_career_navigator(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get career path recommendations."""
    
    selected_field = request.get("selected_field")
    selected_country = request.get("selected_country")
    
    if not selected_field or not selected_country:
        raise HTTPException(status_code=400, detail="Missing field or country")
    
    navigator = recommendation_engine.get_career_navigator(
        current_user, selected_field, selected_country, db
    )
    
    return navigator


@recommendations_router.post("/roi")
async def calculate_roi(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Calculate ROI for a course."""
    
    from app.utils.calculations import ROICalculator
    
    calculator = ROICalculator()
    result = calculator.calculate_roi(
        total_cost=request.get("total_cost", 0),
        salary_year_1=request.get("salary_year_1", 400000),
        salary_year_5=request.get("salary_year_5", 800000),
        loan_amount=request.get("loan_amount", 0),
        interest_rate=request.get("interest_rate", 8.5),
        tenure_months=request.get("tenure_months", 180),
    )
    
    return result
