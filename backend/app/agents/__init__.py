"""
CrewAI Multi-Agent System for Autonomous Growth Loops.

INNOVATIVE: Zero-human-intervention agent orchestration
- Lead Scoring Agent: Evaluates user profile strength
- Content Personalization Agent: Selects optimal content
- Engagement Loop Agent: Determines next action
- Conversion Agent: Drives to loan application
- Retention Agent: Prevents churn

This is the SOUL of the platform's growth engine.
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timezone, timedelta
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# AGENT BASE CLASSES
# ============================================================================

class Agent(ABC):
    """Abstract base for all agents."""
    
    def __init__(self, name: str, model: str = "groq"):
        self.name = name
        self.model = model
        self.memory = {}
    
    @abstractmethod
    async def act(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent action."""
        pass
    
    def remember(self, key: str, value: Any):
        """Store in agent memory."""
        self.memory[key] = value
    
    def recall(self, key: str) -> Optional[Any]:
        """Retrieve from agent memory."""
        return self.memory.get(key)


# ============================================================================
# SCORING & EVALUATION AGENTS
# ============================================================================

class LeadScoringAgent(Agent):
    """
    Evaluates user profile strength and assigns quality score.
    Determines how likely a user is to convert to loan applicant.
    """
    
    def __init__(self):
        super().__init__("Lead Scorer")
        self.weights = {
            "profile_completeness": 0.15,
            "academic_strength": 0.25,
            "financial_capacity": 0.25,
            "engagement_level": 0.20,
            "application_progress": 0.15,
        }
    
    async def act(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score user as a high/medium/low quality lead.
        
        Returns:
        - lead_score: 0-100
        - lead_tier: hot, warm, cold
        - key_signals: List of conversion triggers
        - risk_signals: List of churn warnings
        """
        
        # Calculate component scores
        profile_score = self._score_profile_completeness(user_profile)
        academic_score = self._score_academic_strength(user_profile)
        financial_score = self._score_financial_capacity(user_profile)
        engagement_score = self._score_engagement(user_profile)
        application_score = self._score_application_progress(user_profile)
        
        # Weighted composite
        lead_score = (
            profile_score * self.weights["profile_completeness"] +
            academic_score * self.weights["academic_strength"] +
            financial_score * self.weights["financial_capacity"] +
            engagement_score * self.weights["engagement_level"] +
            application_score * self.weights["application_progress"]
        )
        
        # Classify tier
        if lead_score >= 75:
            tier = "hot"  # High conversion probability
        elif lead_score >= 50:
            tier = "warm"  # Medium conversion probability
        else:
            tier = "cold"  # Low conversion probability
        
        # Identify key conversion triggers
        key_signals = []
        if academic_score >= 80:
            key_signals.append("Strong academic profile → Eligible for premium loans")
        if financial_score >= 80:
            key_signals.append("High earning potential → Higher approved loan amount")
        if application_score >= 2:
            key_signals.append("Active in applications → Ready for loan discussion")
        if engagement_score >= 70:
            key_signals.append("Highly engaged → Responsive to personalization")
        
        # Risk signals (churn warnings)
        risk_signals = []
        if engagement_score < 30:
            risk_signals.append("Low engagement → May churn if not re-engaged")
        if application_score == 0 and datetime.now(timezone.utc) - user_profile.get("created_at", datetime.now(timezone.utc)) > timedelta(days=30):
            risk_signals.append("Stale profile → No action in 30+ days")
        if financial_score < 40:
            risk_signals.append("Weak financial profile → May not qualify for large loans")
        
        logger.info(f"🎯 Lead Scored: {user_profile.get('email')} | Score={lead_score:.1f} | Tier={tier}")
        
        return {
            "user_id": user_profile.get("id"),
            "email": user_profile.get("email"),
            "lead_score": round(lead_score, 1),
            "lead_tier": tier,
            "component_scores": {
                "profile": round(profile_score, 1),
                "academic": round(academic_score, 1),
                "financial": round(financial_score, 1),
                "engagement": round(engagement_score, 1),
                "application": round(application_score, 1),
            },
            "key_signals": key_signals,
            "risk_signals": risk_signals,
            "recommended_action": self._recommend_action(tier, key_signals, risk_signals),
        }
    
    def _score_profile_completeness(self, user: Dict) -> float:
        """Score how complete user profile is."""
        required_fields = [
            "first_name", "last_name", "current_degree", 
            "current_cgpa", "university_name", "annual_income"
        ]
        completed = sum(1 for f in required_fields if user.get(f))
        return (completed / len(required_fields)) * 100
    
    def _score_academic_strength(self, user: Dict) -> float:
        """Score academic excellence."""
        cgpa = user.get("current_cgpa", 0)
        gre = user.get("gre_score", 0)
        gmat = user.get("gmat_score", 0)
        
        cgpa_score = (cgpa / 4.0) * 100 if cgpa else 0
        gre_score = ((gre - 260) / (340 - 260)) * 100 if gre else 0
        gmat_score = ((gmat - 200) / (800 - 200)) * 100 if gmat else 0
        
        scores = [s for s in [cgpa_score, gre_score, gmat_score] if s > 0]
        return sum(scores) / len(scores) if scores else 50  # Default for missing data
    
    def _score_financial_capacity(self, user: Dict) -> float:
        """Score ability to repay loans."""
        income = user.get("annual_income", 0)
        experience = user.get("work_experience_years", 0)
        
        # Income scoring (normalize to 7.5 LPA baseline)
        income_score = min(100, (income / 750000) * 100) if income else 30
        
        # Stability scoring
        stability_score = min(100, (experience / 5) * 100) if experience > 0 else 50
        
        # Combined
        return (income_score * 0.6) + (stability_score * 0.4)
    
    def _score_engagement(self, user: Dict) -> float:
        """Score platform engagement."""
        interactions = len(user.get("interactions", []))
        days_active = (datetime.now(timezone.utc) - user.get("created_at", datetime.now(timezone.utc))).days
        
        # Interaction frequency (normalized: 1 interaction per day is excellent)
        interaction_score = min(100, (interactions / max(1, days_active)) * 100)
        
        return interaction_score
    
    def _score_application_progress(self, user: Dict) -> float:
        """Score application pipeline progress."""
        applications = len(user.get("applications", []))
        
        # Applications as proxy for progress (1-3 apps = excellent)
        if applications >= 3:
            return 100
        elif applications >= 1:
            return 70
        else:
            return 20
    
    def _recommend_action(self, tier: str, signals: List[str], risks: List[str]) -> str:
        """Recommend next action for this lead."""
        if tier == "hot":
            if not signals:
                return "Schedule loan eligibility call"
            return "Send personalized loan offer"
        elif tier == "warm":
            if risks:
                return "Re-engagement email campaign"
            return "Send ROI calculator link"
        else:  # cold
            return "Basic education content nurture"


class ContentPersonalizationAgent(Agent):
    """
    Determines optimal content, emails, and messaging for each user.
    Drives engagement by always showing relevant content.
    """
    
    def __init__(self):
        super().__init__("Content Personalizer")
    
    async def act(self, user_profile: Dict[str, Any], lead_score_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select personalized content strategy.
        
        Returns:
        - email_template: Template to send
        - content_topics: Blog posts/resources to recommend
        - cta_text: Call-to-action messaging
        - subject_line: Personalized email subject
        """
        
        tier = lead_score_result.get("lead_tier", "cold")
        key_signals = lead_score_result.get("key_signals", [])
        
        # Content strategy based on tier and signals
        if tier == "hot":
            return self._content_for_hot_lead(user_profile, key_signals)
        elif tier == "warm":
            return self._content_for_warm_lead(user_profile, key_signals)
        else:
            return self._content_for_cold_lead(user_profile)
    
    def _content_for_hot_lead(self, user: Dict, signals: List[str]) -> Dict[str, Any]:
        """High-intent content for hot leads."""
        return {
            "email_template": "loan_offer_personalized",
            "subject_line": f"🎉 Your Exclusive {user.get('first_name', 'Student')}, {user.get('preferred_countries', ['USA'])[0]} Education Loan Offer",
            "content_topics": [
                "education-roi-calculator",
                "loan-approval-success-stories",
                "repayment-options-guide",
            ],
            "cta_text": "Pre-approve my loan in 2 minutes →",
            "cta_link": "/loan/pre-qualify",
            "send_time": "immediate",  # Send right away
            "personalization": {
                "first_name": user.get("first_name"),
                "target_country": user.get("preferred_countries", ["USA"])[0],
                "approved_amount": user.get("annual_income", 500000) * 1.5,
            },
        }
    
    def _content_for_warm_lead(self, user: Dict, signals: List[str]) -> Dict[str, Any]:
        """Education content for warm leads."""
        return {
            "email_template": "education_nurture",
            "subject_line": f"{user.get('first_name', 'Student')}, See Which Course Fits Your Budget",
            "content_topics": [
                "course-comparison-guide",
                "university-rankings-by-country",
                "career-pathways-analysis",
            ],
            "cta_text": "Explore matching courses →",
            "cta_link": "/recommendations",
            "send_time": "next_morning",  # Send next morning for engagement
            "personalization": {
                "preferred_fields": user.get("preferred_fields", []),
                "budget_range": f"{user.get('budget_range_min', 0)} - {user.get('budget_range_max', 5000000)} INR",
            },
        }
    
    def _content_for_cold_lead(self, user: Dict) -> Dict[str, Any]:
        """Awareness content for cold leads."""
        return {
            "email_template": "awareness_campaign",
            "subject_line": f"Study Abroad? {user.get('first_name', 'Student')}, Your Path to Top Universities",
            "content_topics": [
                "study-abroad-101",
                "cost-of-education-by-country",
                "test-prep-resources",
            ],
            "cta_text": "Start my study abroad journey →",
            "cta_link": "/career-navigator",
            "send_time": "next_week",  # Space out for cold leads
            "personalization": {},
        }


class EngagementLoopAgent(Agent):
    """
    Orchestrates the next best action for each user.
    Closes the loop between scoring, content, and conversion.
    """
    
    def __init__(self):
        super().__init__("Engagement Loop Orchestrator")
    
    async def act(
        self,
        user_profile: Dict[str, Any],
        lead_score: Dict[str, Any],
        content_strategy: Dict[str, Any],
        last_action: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Determine next best action and sequence.
        
        Implements the engagement loop:
        Awareness → Interest → Consideration → Decision → Conversion
        """
        
        tier = lead_score.get("lead_tier", "cold")
        recommended_action = lead_score.get("recommended_action", "nurture")
        
        # Determine state in funnel
        applications = len(user_profile.get("applications", []))
        loan_apps = len(user_profile.get("loan_applications", []))
        interactions = len(user_profile.get("interactions", []))
        
        if loan_apps > 0:
            state = "conversion"  # Already converting
        elif applications >= 2:
            state = "decision"  # Making decisions
        elif applications >= 1:
            state = "consideration"  # Considering applications
        elif interactions >= 10:
            state = "interest"  # Showing interest
        else:
            state = "awareness"  # Still learning
        
        # Determine action sequence
        actions = self._generate_action_sequence(
            tier, state, recommended_action, last_action
        )
        
        logger.info(f"📊 Engagement Loop: User={user_profile.get('email')} | State={state} | Tier={tier} | Actions={len(actions)}")
        
        return {
            "user_id": user_profile.get("id"),
            "current_funnel_state": state,
            "lead_tier": tier,
            "action_sequence": actions,
            "next_action": actions[0] if actions else None,
            "urgency": "high" if tier == "hot" else "medium" if tier == "warm" else "low",
        }
    
    def _generate_action_sequence(
        self,
        tier: str,
        state: str,
        recommended: str,
        last_action: Optional[Dict],
    ) -> List[Dict[str, Any]]:
        """Generate sequence of next actions."""
        
        actions = []
        
        # Prevent action fatigue (don't repeat same action)
        if last_action and (datetime.now(timezone.utc) - last_action.get("timestamp", datetime.now(timezone.utc))).total_seconds() < 3600:
            return [{"type": "wait", "duration_minutes": 60, "reason": "Avoid action fatigue"}]
        
        # Hot leads: Accelerate to conversion
        if tier == "hot":
            if state == "interest":
                actions.append({"type": "send_email", "template": "loan_eligibility_check"})
                actions.append({"type": "trigger_chatbot", "intent": "loan_guidance"})
            elif state == "consideration":
                actions.append({"type": "send_email", "template": "personalized_offer"})
                actions.append({"type": "push_notification", "message": "Your exclusive loan offer expires soon"})
            elif state == "decision":
                actions.append({"type": "send_sms", "message": "Complete your loan application for instant approval"})
                actions.append({"type": "trigger_agent_call", "reason": "final_conversion"})
        
        # Warm leads: Nurture and engage
        elif tier == "warm":
            if state == "awareness":
                actions.append({"type": "send_email", "template": "education_content"})
                actions.append({"type": "add_to_segment", "segment": "nurture_email_series"})
            elif state == "interest":
                actions.append({"type": "send_email", "template": "course_recommendations"})
                actions.append({"type": "trigger_chatbot", "intent": "course_discovery"})
            elif state == "consideration":
                actions.append({"type": "send_email", "template": "roi_calculator"})
                actions.append({"type": "show_social_proof", "type": "student_testimonials"})
        
        # Cold leads: Awareness building
        else:
            if state == "awareness":
                actions.append({"type": "send_email", "template": "awareness_campaign"})
                actions.append({"type": "add_to_segment", "segment": "top_of_funnel"})
            else:
                actions.append({"type": "send_email", "template": "re_engagement"})
        
        return actions


class ConversionAgent(Agent):
    """
    Focuses exclusively on converting engaged users to loan applicants.
    Uses friction-free application and instant gratification.
    """
    
    def __init__(self):
        super().__init__("Conversion Specialist")
    
    async def act(self, user_profile: Dict[str, Any], engagement_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute conversion tactics.
        
        Returns:
        - conversion_offers: Array of offers to present
        - friction_reduction: Steps to simplify application
        - incentives: Engagement incentives
        """
        
        tier = engagement_state.get("lead_tier", "cold")
        state = engagement_state.get("current_funnel_state", "awareness")
        
        # Only aggressively convert warm/hot leads in consideration+ state
        if tier == "cold" or state in ["awareness"]:
            return {
                "strategy": "nurture_only",
                "message": "Not ready for direct conversion; focus on nurture",
            }
        
        # Friction reduction tactics
        friction_reduction = {
            "auto_fill_profile": self._get_autofill_fields(user_profile),
            "instant_eligibility": True,  # Show instant eligibility check
            "one_click_apply": True,  # Enable 1-click application
            "progress_indicator": "4 of 5 steps done",
        }
        
        # Create customized offers
        offers = []
        
        annual_income = user_profile.get("annual_income", 500000)
        cgpa = user_profile.get("current_cgpa", 3.5)
        
        # Offer 1: Standard Education Loan
        offers.append({
            "name": "Standard Education Loan",
            "amount_range": (500000, min(2000000, annual_income * 1.5)),
            "interest_rate": 8.5 if cgpa >= 3.5 else 9.5,
            "tenure_months": 180,
            "moratorium_months": 6,
            "approval_probability": "95%",
            "processing_time": "24 hours",
            "highlights": ["Fixed interest rate", "No prepayment penalty", "Flexible EMI options"],
        })
        
        # Offer 2: Premium Loan (for hot leads with strong profile)
        if tier == "hot":
            offers.append({
                "name": "Premium Education Loan",
                "amount_range": (1000000, min(5000000, annual_income * 2)),
                "interest_rate": 7.9 if cgpa >= 3.7 else 8.5,
                "tenure_months": 180,
                "moratorium_months": 12,  # Longer grace period
                "approval_probability": "98%",
                "processing_time": "12 hours",
                "highlights": ["Lower interest rate", "Extended moratorium", "Priority support"],
                "exclusive": True,
            })
        
        logger.info(f"💰 Conversion Strategy: User={user_profile.get('email')} | Offers={len(offers)}")
        
        return {
            "user_id": user_profile.get("id"),
            "conversion_strategy": "instant_offer" if tier == "hot" else "progressive_conversion",
            "offers": offers,
            "friction_reduction": friction_reduction,
            "next_step": "Show instant eligibility popup",
            "estimated_conversion_probability": 0.85 if tier == "hot" else 0.45 if tier == "warm" else 0.10,
        }
    
    def _get_autofill_fields(self, user: Dict) -> Dict[str, Any]:
        """Get fields that can be auto-filled for user."""
        return {
            "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "annual_income": user.get("annual_income"),
            "work_experience": user.get("work_experience_years"),
            "education_level": user.get("current_degree"),
        }


class RetentionAgent(Agent):
    """
    Identifies at-risk users and executes retention campaigns.
    Prevents churn through proactive engagement.
    """
    
    def __init__(self):
        super().__init__("Retention Specialist")
    
    async def act(self, user_profile: Dict[str, Any], lead_score: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify churn risk and recommend retention actions.
        """
        
        risk_signals = lead_score.get("risk_signals", [])
        
        # Churn risk scoring
        churn_risk = len(risk_signals) * 25  # Each signal = 25% risk
        churn_risk = min(100, churn_risk)
        
        if churn_risk < 30:
            risk_level = "low"
        elif churn_risk < 60:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Retention campaigns
        campaigns = self._get_retention_campaigns(risk_level, user_profile, risk_signals)
        
        logger.info(f"⚠️ Retention Alert: User={user_profile.get('email')} | Risk={churn_risk}% | Level={risk_level}")
        
        return {
            "user_id": user_profile.get("id"),
            "churn_risk_score": round(churn_risk, 1),
            "churn_risk_level": risk_level,
            "risk_signals": risk_signals,
            "retention_campaigns": campaigns,
            "recommend_action": campaigns[0]["action"] if campaigns else "continue_monitoring",
        }
    
    def _get_retention_campaigns(self, risk_level: str, user: Dict, signals: List[str]) -> List[Dict[str, Any]]:
        """Get targeted retention campaigns."""
        
        campaigns = []
        
        if risk_level == "high":
            campaigns.extend([
                {
                    "name": "Win-Back Campaign",
                    "action": "send_urgency_email",
                    "subject": f"{user.get('first_name', 'Student')}, don't miss this opportunity!",
                    "incentive": "10% lower interest rate if you apply this week",
                    "timing": "immediate",
                },
                {
                    "name": "Personal Outreach",
                    "action": "trigger_personalized_call",
                    "script": "Address specific pain points from signals",
                    "timing": "next_business_day",
                },
            ])
        
        elif risk_level == "medium":
            campaigns.append({
                "name": "Re-Engagement Campaign",
                "action": "send_educational_content",
                "content": "Latest opportunities for their preferred fields",
                "timing": "next_day",
            })
        
        return campaigns


# ============================================================================
# GROWTH ENGINE ORCHESTRATOR
# ============================================================================

class GrowthEngine:
    """
    Orchestrates all agents in a coordinated growth loop.
    This is the heart of autonomous, AI-driven growth.
    """
    
    def __init__(self):
        self.lead_scorer = LeadScoringAgent()
        self.content_personalizer = ContentPersonalizationAgent()
        self.engagement_orchestrator = EngagementLoopAgent()
        self.conversion_specialist = ConversionAgent()
        self.retention_specialist = RetentionAgent()
    
    async def process_user(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all agents on user profile to generate comprehensive growth strategy.
        
        This is the FULL AUTOMATION loop:
        Analyze → Personalize → Engage → Convert → Retain
        """
        
        logger.info(f"\n🤖 === GROWTH ENGINE PROCESSING: {user_profile.get('email')} ===")
        
        # Step 1: Score the lead
        lead_score = await self.lead_scorer.act(user_profile)
        logger.info(f"✓ Lead Score: {lead_score['lead_score']} ({lead_score['lead_tier']})")
        
        # Step 2: Personalize content
        content_strategy = await self.content_personalizer.act(user_profile, lead_score)
        logger.info(f"✓ Content Strategy: {content_strategy['email_template']}")
        
        # Step 3: Orchestrate engagement loop
        engagement_plan = await self.engagement_orchestrator.act(
            user_profile,
            lead_score,
            content_strategy,
        )
        logger.info(f"✓ Engagement Plan: {engagement_plan['current_funnel_state']} → {len(engagement_plan['action_sequence'])} actions")
        
        # Step 4: Execute conversion tactics
        conversion_plan = await self.conversion_specialist.act(user_profile, engagement_plan)
        logger.info(f"✓ Conversion Plan: {conversion_plan.get('conversion_strategy', 'N/A')}")
        
        # Step 5: Check retention risk
        retention_plan = await self.retention_specialist.act(user_profile, lead_score)
        logger.info(f"✓ Retention Check: {retention_plan['churn_risk_level']} risk")
        
        # Synthesize into ONE comprehensive growth strategy
        growth_strategy = {
            "user_id": user_profile.get("id"),
            "email": user_profile.get("email"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lead_intelligence": lead_score,
            "content_strategy": content_strategy,
            "engagement_plan": engagement_plan,
            "conversion_plan": conversion_plan,
            "retention_plan": retention_plan,
            "executive_summary": {
                "overall_opportunity": lead_score.get("lead_tier"),
                "primary_goal": conversion_plan.get("conversion_strategy", "nurture"),
                "estimated_conversion_probability": conversion_plan.get("estimated_conversion_probability", 0),
                "recommended_next_action": engagement_plan["next_action"],
                "churn_risk": retention_plan["churn_risk_level"],
                "channels_to_activate": self._determine_channels(engagement_plan, conversion_plan),
            },
        }
        
        logger.info(f"🎯 Growth Strategy Complete | Goal: {growth_strategy['executive_summary']['primary_goal']}")
        logger.info(f"🤖 === END GROWTH ENGINE ===\n")
        
        return growth_strategy
    
    def _determine_channels(self, engagement_plan: Dict, conversion_plan: Dict) -> List[str]:
        """Determine which channels to activate."""
        channels = set()
        
        for action in engagement_plan.get("action_sequence", []):
            action_type = action.get("type", "").lower()
            if "email" in action_type:
                channels.add("email")
            elif "sms" in action_type:
                channels.add("sms")
            elif "push" in action_type:
                channels.add("push_notification")
            elif "chatbot" in action_type:
                channels.add("chatbot")
        
        # Always add chatbot if hot lead
        if engagement_plan.get("lead_tier") == "hot":
            channels.add("chatbot")
            channels.add("sms")
        
        return list(channels)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "Agent",
    "LeadScoringAgent",
    "ContentPersonalizationAgent",
    "EngagementLoopAgent",
    "ConversionAgent",
    "RetentionAgent",
    "GrowthEngine",
]
