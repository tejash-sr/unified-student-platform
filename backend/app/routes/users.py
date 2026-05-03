"""
User authentication and profile management routes.
Handles signup, login, profile updates, and token refresh.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core import get_db, create_access_token, create_refresh_token, hash_password, verify_password, verify_token
from app.models import User
from app.schemas import UserSignup, UserResponse, UserUpdate, TokenResponse, RefreshTokenRequest
from app.utils import engagement
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# AUTHENTICATION
# ============================================================================

@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
    tags=["Authentication"],
)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """
    Register a new student.
    
    Returns access token, refresh token, and user info.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        current_degree=user_data.current_degree,
        current_cgpa=user_data.current_cgpa,
        work_experience_years=user_data.work_experience_years or 0,
        annual_income=user_data.annual_income,
        preferred_countries=user_data.preferred_countries,
        preferred_fields=user_data.preferred_fields,
        budget_range_min=user_data.budget_range_min,
        budget_range_max=user_data.budget_range_max,
        user_segment="exploration",
        engagement_score=0.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"✅ New user registered: {user.email}")
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_seconds=30 * 60,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    tags=["Authentication"],
)
async def login(
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    """
    Authenticate user with email and password.
    
    Returns JWT tokens for API access.
    """
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    logger.info(f"✅ User logged in: {user.email}")
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_seconds=30 * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    tags=["Authentication"],
)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh an expired access token using refresh token.
    """
    payload = verify_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Generate new access token
    new_access_token = create_access_token({"sub": str(user_id)})
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=request.refresh_token,  # Refresh token stays the same
        token_type="bearer",
        expires_in_seconds=30 * 60,
    )


# ============================================================================
# PROFILE MANAGEMENT
# ============================================================================

def get_current_user(token: str = None, db: Session = Depends(get_db)) -> User:
    """
    Dependency to extract and verify current user from JWT token.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization token provided",
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get current user profile",
    tags=["Profile"],
)
async def get_profile(
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve current user's profile.
    
    Requires: Bearer token in Authorization header
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    
    return UserResponse.model_validate(user)


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Update user profile",
    tags=["Profile"],
)
async def update_profile(
    update_data: UserUpdate,
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Update user profile fields.
    
    Requires: Bearer token in Authorization header
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    
    # Update only provided fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        if value is not None:
            setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    logger.info(f"✅ Updated profile for user: {user.email}")
    
    return UserResponse.model_validate(user)


@router.get(
    "/profile/engagement",
    response_model=dict,
    summary="Get user engagement metrics",
    tags=["Profile"],
)
async def get_engagement_metrics(
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Get personalized engagement metrics and segment.
    
    Used for AI-driven personalization.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    
    # Calculate engagement score
    days_since_signup = (datetime.now(timezone.utc) - user.created_at).days
    profile_completeness = sum([
        1 for field in [
            user.current_degree,
            user.current_cgpa,
            user.gmat_score or user.gre_score,
            user.annual_income,
        ]
        if field
    ]) / 4.0
    
    engagement_score = engagement.calculate_engagement_score(
        interactions_count=len(user.interactions),
        applications_count=len(user.applications),
        days_since_signup=max(1, days_since_signup),
        profile_completeness=profile_completeness,
    )
    
    segment = engagement.assign_segment(engagement_score, len(user.applications))
    
    # Update in database
    user.engagement_score = engagement_score
    user.user_segment = segment
    db.commit()
    
    return {
        "engagement_score": engagement_score,
        "user_segment": segment,
        "profile_completeness_percent": profile_completeness * 100,
        "days_active": days_since_signup,
        "interactions_count": len(user.interactions),
        "applications_count": len(user.applications),
        "last_login": user.last_login,
    }


@router.post(
    "/logout",
    summary="Logout (token invalidation)",
    tags=["Authentication"],
)
async def logout(
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Logout user (token is invalidated on frontend).
    
    Note: JWT tokens are stateless, so true logout requires
    token blacklisting (optional implementation).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    
    logger.info("✅ User logout requested")
    
    return {"message": "Logged out successfully"}


# ============================================================================
# USER DISCOVERY & RECOMMENDATIONS (FOR AI AGENTS)
# ============================================================================

@router.get(
    "/users/segment",
    response_model=list,
    summary="Get users by segment (admin/agents only)",
    tags=["Analytics"],
)
async def get_users_by_segment(
    segment: str = Query(..., description="exploration, applications, or decision"),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
):
    """
    Get users in a specific engagement segment.
    
    Used by growth agents for targeted campaigns.
    """
    users = db.query(User).filter(
        User.user_segment == segment,
        User.is_active == True
    ).limit(limit).all()
    
    return [UserResponse.model_validate(u) for u in users]
