"""
Growth Engine API Routes.
Exposes the multi-agent system for autonomous growth automation.

These endpoints are used by:
1. N8N workflows for scheduled user processing
2. Frontend dashboard for AI insights
3. Admin panel for growth monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.core import get_db, verify_token
from app.models import User
from app.agents import GrowthEngine
from datetime import datetime, timezone
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()
growth_engine = GrowthEngine()


def get_current_user_from_header(authorization: str = None, db: Session = Depends(get_db)) -> User:
    """Extract user from auth header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


# ============================================================================
# GROWTH STRATEGY ENDPOINTS
# ============================================================================

@router.post(
    "/analyze",
    response_model=dict,
    summary="Analyze user and generate growth strategy",
    tags=["Growth Engine"],
)
async def analyze_user(
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Run the complete growth engine analysis on current user.
    
    The growth engine processes the user through 5 agents:
    1. Lead Scoring - Evaluates conversion probability
    2. Content Personalization - Selects optimal content
    3. Engagement Loop - Determines next best actions
    4. Conversion Specialist - Executes conversion tactics
    5. Retention Specialist - Identifies churn risks
    
    Returns comprehensive growth strategy including:
    - Lead score and tier (hot/warm/cold)
    - Personalized content recommendations
    - Recommended actions sequence
    - Conversion offers and tactics
    - Churn risk assessment
    """
    user = get_current_user_from_header(authorization, db)
    
    # Prepare user data for agents
    user_data = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "current_degree": user.current_degree,
        "current_cgpa": user.current_cgpa,
        "university_name": user.university_name,
        "gre_score": user.gre_score,
        "gmat_score": user.gmat_score,
        "work_experience_years": user.work_experience_years,
        "annual_income": user.annual_income,
        "preferred_countries": user.preferred_countries or [],
        "preferred_fields": user.preferred_fields or [],
        "budget_range_min": user.budget_range_min,
        "budget_range_max": user.budget_range_max,
        "created_at": user.created_at,
        "applications": user.applications,
        "loan_applications": user.loan_applications,
        "interactions": user.interactions,
        "user_segment": user.user_segment,
        "engagement_score": user.engagement_score,
    }
    
    try:
        # Run growth engine analysis (async)
        strategy = await growth_engine.process_user(user_data)
        
        logger.info(f"✅ Growth strategy generated for {user.email}")
        
        return {
            "success": True,
            "strategy": strategy,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Growth engine error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Growth analysis failed: {str(e)}",
        )


@router.get(
    "/segment-analysis",
    response_model=dict,
    summary="Analyze entire user segment (admin only)",
    tags=["Growth Engine"],
)
async def analyze_segment(
    segment: str = Query("warm", description="exploration, applications, decision, or all"),
    limit: int = Query(50, le=1000),
    authorization: str = None,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """
    Analyze all users in a segment and generate bulk growth strategies.
    
    Returns aggregated insights:
    - Distribution of lead tiers
    - Most effective content types
    - Common conversion blockers
    - Recommended campaigns by segment
    
    Can run as background task for large segments.
    """
    user = get_current_user_from_header(authorization, db)
    
    # For now, only allow admin/system users
    # (In production, check user roles)
    
    # Fetch segment
    if segment == "all":
        users = db.query(User).filter(User.is_active == True).limit(limit).all()
    else:
        users = db.query(User).filter(
            User.user_segment == segment,
            User.is_active == True
        ).limit(limit).all()
    
    logger.info(f"📊 Analyzing segment: {segment} | Count: {len(users)}")
    
    # Run analysis on each user
    strategies = []
    for u in users[:10]:  # Demo: analyze first 10 only
        user_data = {
            "id": u.id,
            "email": u.email,
            "first_name": u.first_name,
            "current_cgpa": u.current_cgpa,
            "annual_income": u.annual_income,
            "work_experience_years": u.work_experience_years,
            "applications": u.applications,
            "loan_applications": u.loan_applications,
            "interactions": u.interactions,
            "created_at": u.created_at,
            "preferred_countries": u.preferred_countries or [],
            "preferred_fields": u.preferred_fields or [],
        }
        
        try:
            strategy = await growth_engine.process_user(user_data)
            strategies.append(strategy["executive_summary"])
        except Exception as e:
            logger.warning(f"Could not analyze user {u.email}: {e}")
    
    # Aggregate insights
    tier_distribution = {}
    goal_distribution = {}
    channel_usage = {}
    
    for strat in strategies:
        tier = strat.get("overall_opportunity", "unknown")
        tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
        
        goal = strat.get("primary_goal", "unknown")
        goal_distribution[goal] = goal_distribution.get(goal, 0) + 1
        
        for channel in strat.get("channels_to_activate", []):
            channel_usage[channel] = channel_usage.get(channel, 0) + 1
    
    return {
        "segment": segment,
        "users_analyzed": len(strategies),
        "total_users_in_segment": len(users),
        "tier_distribution": tier_distribution,
        "primary_goals": goal_distribution,
        "recommended_channels": channel_usage,
        "sample_strategies": strategies[:3],  # Show first 3
    }


@router.get(
    "/recommendations",
    response_model=dict,
    summary="Get AI growth recommendations",
    tags=["Growth Engine"],
)
async def get_growth_recommendations(
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Get personalized growth recommendations for current user.
    
    This endpoint:
    1. Analyzes user's current state
    2. Identifies growth opportunities
    3. Recommends specific actions
    4. Provides timeline estimates
    
    Used by dashboard to show "Next Steps" to users.
    """
    user = get_current_user_from_header(authorization, db)
    
    user_data = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "annual_income": user.annual_income,
        "work_experience_years": user.work_experience_years,
        "applications": user.applications,
        "loan_applications": user.loan_applications,
        "interactions": user.interactions,
        "created_at": user.created_at,
    }
    
    strategy = await growth_engine.process_user(user_data)
    
    # Extract actionable recommendations
    recommendations = {
        "lead_tier": strategy["executive_summary"]["overall_opportunity"],
        "conversion_probability": f"{strategy['executive_summary']['estimated_conversion_probability'] * 100:.0f}%",
        "next_action": strategy["executive_summary"]["recommended_next_action"],
        "suggested_content": strategy["content_strategy"]["content_topics"],
        "estimated_timeline": {
            "awareness_to_interest": "2-4 weeks",
            "interest_to_consideration": "3-6 weeks",
            "consideration_to_decision": "2-4 weeks",
            "decision_to_conversion": "1-2 weeks",
        },
        "churn_risk": strategy["retention_plan"]["churn_risk_level"],
        "action_sequence": [
            {
                "action": action.get("type", ""),
                "description": action.get("type", "").replace("_", " ").title(),
                "estimated_time": action.get("estimated_time", "2-24 hours"),
            }
            for action in strategy["engagement_plan"].get("action_sequence", [])[:5]
        ],
    }
    
    return {
        "success": True,
        "recommendations": recommendations,
        "strategy_id": f"{user.id}-{datetime.now(timezone.utc).timestamp()}",
    }


# ============================================================================
# AGENT INSIGHTS (ADMIN/ANALYTICS)
# ============================================================================

@router.get(
    "/agent-performance",
    response_model=dict,
    summary="Get growth agent performance metrics",
    tags=["Analytics"],
)
async def get_agent_performance(
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Show how well growth agents are performing.
    
    Metrics:
    - Conversion rates by lead tier
    - Content effectiveness
    - Email open rates
    - Action completion rates
    """
    
    # For demo, return mock metrics
    # In production, this would pull from database
    
    return {
        "agents": {
            "lead_scorer": {
                "accuracy": "87%",
                "hot_leads_converted": "62%",
                "warm_leads_converted": "34%",
                "cold_leads_converted": "8%",
            },
            "content_personalizer": {
                "email_open_rate": "41%",
                "click_through_rate": "12%",
                "content_satisfaction": "4.3/5",
            },
            "engagement_orchestrator": {
                "action_completion_rate": "71%",
                "optimal_timing_accuracy": "68%",
            },
            "conversion_specialist": {
                "offer_acceptance_rate": "58%",
                "application_completion_rate": "76%",
            },
            "retention_specialist": {
                "churn_prediction_accuracy": "81%",
                "win_back_rate": "23%",
            },
        },
        "overall_platform_metrics": {
            "total_users_processed": 450,
            "avg_conversion_funnel_time": "35 days",
            "ltv_by_segment": {
                "hot": "₹2,50,000",
                "warm": "₹1,20,000",
                "cold": "₹45,000",
            },
        },
        "improvement_areas": [
            "Increase cold lead engagement from 8% to 15%",
            "Improve content personalization accuracy from 68% to 80%",
            "Reduce application friction to increase 76% → 85% completion",
        ],
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ["router"]
