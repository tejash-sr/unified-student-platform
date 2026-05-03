"""
Pydantic schemas for request/response validation.
Enables type safety and automatic API documentation.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserProfileBase(BaseModel):
    """Base user profile fields."""
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, max_length=20)
    
    # Educational
    current_degree: Optional[str] = Field(None, max_length=100)
    current_cgpa: Optional[float] = Field(None, ge=0, le=4.0)
    university_name: Optional[str] = None
    graduation_year: Optional[int] = None
    
    # Test scores
    gmat_score: Optional[int] = Field(None, ge=200, le=800)
    gre_score: Optional[int] = Field(None, ge=260, le=340)
    ielts_score: Optional[float] = Field(None, ge=0, le=9)
    toefl_score: Optional[int] = Field(None, ge=0, le=120)
    
    # Professional
    work_experience_years: Optional[float] = Field(default=0, ge=0)
    current_job_title: Optional[str] = None
    current_company: Optional[str] = None
    annual_income: Optional[float] = Field(None, ge=0)
    
    # Preferences
    preferred_countries: List[str] = Field(default=["US", "UK", "Canada"])
    preferred_fields: List[str] = Field(default=[])
    study_mode: Optional[str] = None
    preferred_start_term: Optional[str] = None
    budget_range_min: Optional[float] = None
    budget_range_max: Optional[float] = None


class UserSignup(UserProfileBase):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator("password")
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        return v


class UserResponse(UserProfileBase):
    """User response model."""
    id: int
    email: str
    user_segment: str
    engagement_score: float
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Partial user update."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    current_cgpa: Optional[float] = None
    annual_income: Optional[float] = None
    preferred_countries: Optional[List[str]] = None
    preferred_fields: Optional[List[str]] = None
    budget_range_min: Optional[float] = None
    budget_range_max: Optional[float] = None


# ============================================================================
# UNIVERSITY & COURSE SCHEMAS
# ============================================================================

class UniversityBase(BaseModel):
    """Base university fields."""
    name: str
    country: str
    city: Optional[str] = None
    qs_world_rank: Optional[int] = None
    acceptance_rate: Optional[float] = None
    annual_tuition_usd: Optional[float] = None
    annual_living_cost_usd: Optional[float] = None
    avg_salary_after_graduation_usd: Optional[float] = None
    placement_rate: Optional[float] = None
    description: Optional[str] = None
    url: Optional[str] = None


class UniversityResponse(UniversityBase):
    """University response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    """Base course fields."""
    name: str
    degree_type: str  # MS, MBA, PhD
    field: str  # CS, Finance, Engineering
    specialization: Optional[str] = None
    duration_months: Optional[int] = None
    min_gpa_required: Optional[float] = None
    gre_required: Optional[bool] = False
    gmat_required: Optional[bool] = False
    avg_salary_usd: Optional[float] = None
    description: Optional[str] = None


class CourseResponse(CourseBase):
    """Course response."""
    id: int
    university_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# APPLICATION & TIMELINE SCHEMAS
# ============================================================================

class TimelineEventCreate(BaseModel):
    """Create timeline event."""
    event_type: str
    title: str
    description: Optional[str] = None
    scheduled_date: datetime
    priority: str = "medium"
    metadata: Optional[Dict[str, Any]] = None


class TimelineEventResponse(BaseModel):
    """Timeline event response."""
    id: int
    event_type: str
    title: str
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    is_completed: bool
    priority: str
    
    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    """Create application."""
    university_id: int
    course_id: int


class ApplicationResponse(BaseModel):
    """Application response."""
    id: int
    user_id: int
    university_id: int
    course_id: int
    status: str
    predicted_acceptance_probability: Optional[float] = None
    submitted_at: Optional[datetime] = None
    decision_date: Optional[datetime] = None
    decision_status: Optional[str] = None
    created_at: datetime
    timeline_events: List[TimelineEventResponse] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# LOAN SCHEMAS
# ============================================================================

class LoanEligibilityRequest(BaseModel):
    """Request loan eligibility check."""
    requested_amount_inr: float = Field(..., gt=0)
    
    # Override for specific calculation
    annual_income: Optional[float] = None
    employment_years: Optional[float] = None


class LoanEligibilityResponse(BaseModel):
    """Eligibility assessment result."""
    eligibility_score: float  # 0-100
    eligibility_category: str  # approved, conditional, rejected
    eligibility_reasons: List[str]
    
    # Pre-computed offer
    potential_approved_amount: float
    potential_interest_rate: float
    potential_monthly_emi: float
    required_documents: List[str]
    
    class Config:
        from_attributes = True


class EMICalculationRequest(BaseModel):
    """Calculate EMI."""
    principal_amount: float = Field(..., gt=0)
    interest_rate_annual: float = Field(..., ge=0)
    tenure_months: int = Field(..., gt=0)


class EMICalculationResponse(BaseModel):
    """EMI calculation result."""
    monthly_emi: float
    total_amount: float
    total_interest: float
    amortization_schedule: List[Dict[str, Any]]  # [month, emi, principal, interest, balance, ...]


class LoanApplicationCreate(BaseModel):
    """Create loan application."""
    requested_amount_inr: float = Field(..., gt=0)
    tenure_months: int = Field(default=180, gt=0)


class LoanApplicationResponse(BaseModel):
    """Loan application response."""
    id: int
    user_id: int
    status: str
    eligibility_score: Optional[float] = None
    eligibility_category: Optional[str] = None
    requested_amount_inr: float
    approved_amount_inr: Optional[float] = None
    interest_rate_annual_percent: Optional[float] = None
    monthly_emi_inr: Optional[float] = None
    decision_date: Optional[datetime] = None
    decision_status: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoanOfferResponse(BaseModel):
    """Detailed loan offer."""
    loan_application_id: int
    approved_amount: float
    interest_rate: float
    tenure_months: int
    monthly_emi: float
    total_interest: float
    processing_fee: float
    insurance_premium: Optional[float] = None
    moratorium_months: int
    prepayment_allowed: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# RECOMMENDATION SCHEMAS
# ============================================================================

class RecommendationResponse(BaseModel):
    """Recommendation result."""
    id: int
    recommendation_type: str
    score: float  # 0-100
    course_id: Optional[int] = None
    university_id: Optional[int] = None
    factors: Dict[str, float]  # Factor breakdown
    
    # Embedded course/university details
    course_name: Optional[str] = None
    university_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class CareerNavigatorRequest(BaseModel):
    """Career navigator request."""
    # Use user's profile if not provided
    target_countries: Optional[List[str]] = None
    target_fields: Optional[List[str]] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    min_acceptance_probability: Optional[float] = Field(default=0.3, ge=0, le=1)


class CareerNavigatorResponse(BaseModel):
    """Career navigator suggestions."""
    recommendations: List[RecommendationResponse]
    explanation: str  # AI-generated explanation of matches
    match_summary: Dict[str, Any]  # Overall match analysis


class ROICalculationRequest(BaseModel):
    """ROI calculation request."""
    course_id: int
    university_id: int
    loan_amount: float
    loan_interest_rate: float
    loan_tenure_months: int = 180


class ROICalculationResponse(BaseModel):
    """ROI calculation result."""
    total_cost: float  # Tuition + living
    expected_salary_year1: float
    expected_salary_year5: float
    payback_period_months: float
    net_benefit_5yr: float
    roi_percentage: float
    confidence_score: float


# ============================================================================
# INTERACTION & ANALYTICS SCHEMAS
# ============================================================================

class InteractionCreate(BaseModel):
    """Log user interaction."""
    interaction_type: str
    entity_type: str
    entity_id: str
    source: Optional[str] = None
    duration_seconds: Optional[int] = None
    query: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class InteractionResponse(BaseModel):
    """Interaction log entry."""
    id: int
    user_id: int
    interaction_type: str
    entity_type: str
    entity_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsMetricResponse(BaseModel):
    """Analytics metric."""
    metric_name: str
    value: float
    timestamp: datetime
    breakdown: Optional[Dict[str, Any]] = None


# ============================================================================
# AUTH SCHEMAS
# ============================================================================

class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ============================================================================
# GENERIC SCHEMAS
# ============================================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    total: int
    page: int
    page_size: int
    items: List[Any]


class ErrorResponse(BaseModel):
    """Error response."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
