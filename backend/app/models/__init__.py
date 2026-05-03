"""
SQLAlchemy models for the unified student platform.
Designed for AI-first engagement with rich metadata for recommendations and personalization.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Table, Index, BigInteger, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
import uuid


# Association table for user-course interactions (for recommendations)
user_course_interactions = Table(
    "user_course_interactions",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("course_id", Integer, ForeignKey("courses.id", ondelete="CASCADE")),
    Column("interaction_type", String, index=True),  # view, click, apply, bookmark, etc.
    Column("timestamp", DateTime, default=lambda: datetime.now(timezone.utc), index=True),
    Column("metadata", JSON),  # Additional interaction data
)

# Association table for user-university interactions
user_university_interactions = Table(
    "user_university_interactions",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("university_id", Integer, ForeignKey("universities.id", ondelete="CASCADE")),
    Column("interaction_type", String, index=True),
    Column("timestamp", DateTime, default=lambda: datetime.now(timezone.utc), index=True),
    Column("metadata", JSON),
)


class User(Base):
    """
    User profile with rich metadata for personalization.
    Tracks educational background, preferences, and engagement state.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Basic info
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    
    # Educational background
    current_degree = Column(String(100))  # B.Tech, BCA, BCom, etc.
    current_cgpa = Column(Float)  # 0-4.0
    university_name = Column(String(255))
    graduation_year = Column(Integer)
    
    # Test scores (standardized)
    gmat_score = Column(Integer)  # 200-800
    gre_score = Column(Integer)  # 260-340
    ielts_score = Column(Float)  # 0-9
    toefl_score = Column(Integer)  # 0-120
    cat_score = Column(Integer)  # CAT (India)
    
    # Professional background
    work_experience_years = Column(Float, default=0)
    current_job_title = Column(String(255))
    current_company = Column(String(255))
    annual_income = Column(Float)  # in INR
    
    # Study preferences (AI-friendly for recommendations)
    preferred_countries = Column(JSON, default=list)  # [US, UK, Canada, etc.]
    preferred_fields = Column(JSON, default=list)  # [CS, Finance, MBA, etc.]
    preferred_universities = Column(JSON, default=list)  # Bookmarked universities
    study_mode = Column(String(50))  # Full-time, Part-time, Online
    preferred_start_term = Column(String(50))  # Fall, Spring, Summer
    budget_range_min = Column(Float)  # in INR
    budget_range_max = Column(Float)
    
    # Engagement tracking
    user_segment = Column(String(50), default="exploration")  # exploration, applications, decision
    engagement_score = Column(Float, default=0.0)  # AI-computed personalization score
    last_login = Column(DateTime, index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    loan_applications = relationship("LoanApplication", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    
    # Many-to-many via association tables
    viewed_courses = relationship(
        "Course",
        secondary=user_course_interactions,
        backref="viewed_by_users"
    )
    viewed_universities = relationship(
        "University",
        secondary=user_university_interactions,
        backref="viewed_by_users"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, segment={self.user_segment})>"


class University(Base):
    """
    University/institution metadata with AI-searchable attributes.
    Supports recommendations and ROI calculations.
    """
    __tablename__ = "universities"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True)  # e.g., QS ranking ID
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    city = Column(String(100))
    state = Column(String(100))
    
    # Rankings & prestige (for matching)
    qs_world_rank = Column(Integer)
    times_rank = Column(Integer)
    shanghai_rank = Column(Integer)
    
    # Admission data
    acceptance_rate = Column(Float)  # 0-100%
    average_gpa = Column(Float)  # 0-4.0
    average_gre_score = Column(Integer)
    average_gmat_score = Column(Integer)
    average_ielts = Column(Float)
    
    # Cost data (for ROI)
    annual_tuition_usd = Column(Float)
    annual_living_cost_usd = Column(Float)
    
    # Career outcomes
    avg_salary_after_graduation_usd = Column(Float)
    placement_rate = Column(Float)  # 0-100%
    
    # Description for RAG/chatbot
    description = Column(Text)
    url = Column(String(255))
    
    # Embeddings metadata
    embedding_id = Column(String(100))  # ChromaDB collection ID
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    courses = relationship("Course", back_populates="university", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="university", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_university_country_rank", "country", "qs_world_rank"),
        Index("idx_university_search", "name", "country"),
    )
    
    def __repr__(self):
        return f"<University(name={self.name}, rank={self.qs_world_rank})>"


class Course(Base):
    """
    Program/course metadata with AI attributes for matching and recommendations.
    """
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    degree_type = Column(String(50))  # MS, MBA, PhD, Postdoc, etc.
    field = Column(String(100), nullable=False, index=True)  # CS, Finance, Engineering, etc.
    specialization = Column(String(255))  # Data Science, ML, etc.
    
    # Metrics
    duration_months = Column(Integer)  # typically 12-24
    total_credits = Column(Integer)
    
    # Academic requirements
    min_gpa_required = Column(Float)
    gre_required = Column(Boolean, default=False)
    gmat_required = Column(Boolean, default=False)
    min_gre_score = Column(Integer)
    min_gmat_score = Column(Integer)
    english_proficiency_required = Column(String(50))  # IELTS, TOEFL, etc.
    
    # Career outcomes (for ROI)
    avg_salary_usd = Column(Float)  # Post-graduation salary
    salary_2yr_usd = Column(Float)
    salary_5yr_usd = Column(Float)
    
    # Application requirements
    requires_gre = Column(Boolean, default=False)
    requires_gmat = Column(Boolean, default=False)
    requires_essays = Column(Boolean, default=False)
    requires_recommendation_letters = Column(Integer, default=3)
    
    # Application deadlines
    early_deadline = Column(DateTime)
    regular_deadline = Column(DateTime)
    
    # Description for RAG
    description = Column(Text)
    curriculum_highlights = Column(JSON)  # List of key courses
    
    # Embedding for semantic search
    embedding_id = Column(String(100))
    
    # Foreign key
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    university = relationship("University", back_populates="courses")
    applications = relationship("Application", back_populates="course", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_course_field_uni", "field", "university_id"),
        Index("idx_course_search", "name", "field"),
    )
    
    def __repr__(self):
        return f"<Course(name={self.name}, field={self.field})>"


class Application(Base):
    """
    User's university application timeline and status.
    Tracks progress through application workflow.
    """
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Application status
    status = Column(String(50), default="draft", index=True)  # draft, submitted, under-review, accepted, rejected, waitlisted
    predicted_acceptance_probability = Column(Float)  # ML prediction score
    
    # Timeline tracking
    started_at = Column(DateTime, index=True)
    submitted_at = Column(DateTime)
    decision_date = Column(DateTime)
    decision_status = Column(String(50))  # accepted, rejected, waitlisted
    
    # Application components
    essays_status = Column(String(50), default="pending")  # pending, drafted, completed
    recommendation_letters_count = Column(Integer, default=0)
    recommendation_letters_status = Column(String(50), default="pending")
    
    # Metadata
    notes = Column(Text)
    tags = Column(JSON, default=list)  # custom-tags for organization
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="applications")
    university = relationship("University", back_populates="applications")
    course = relationship("Course", back_populates="applications")
    timeline_events = relationship("TimelineEvent", back_populates="application", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_application"),
        Index("idx_application_status", "status", "submitted_at"),
    )
    
    def __repr__(self):
        return f"<Application(user_id={self.user_id}, course={self.course_id}, status={self.status})>"


class TimelineEvent(Base):
    """
    Tracks individual milestones in application journey.
    Powers timeline planner and progress tracking.
    """
    __tablename__ = "timeline_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Event details
    event_type = Column(String(100), nullable=False)  # test_prep, essay_draft, submit, decision, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Timing
    scheduled_date = Column(DateTime, nullable=False, index=True)
    completed_date = Column(DateTime)
    is_completed = Column(Boolean, default=False, index=True)
    
    # Metadata
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    application = relationship("Application", back_populates="timeline_events")
    
    __table_args__ = (
        Index("idx_timeline_application_date", "application_id", "scheduled_date"),
    )


class LoanApplication(Base):
    """
    Education loan application and eligibility tracking.
    Supports dynamic offer generation and document management.
    """
    __tablename__ = "loan_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Application flow
    status = Column(String(50), default="inquiry", index=True)  # inquiry, pre-qualified, applied, approved, rejected, disbursed
    application_type = Column(String(50))  # education-specific
    
    # Eligibility & Scoring
    eligibility_score = Column(Float)  # 0-100 computed score
    eligibility_category = Column(String(50))  # approved, conditional, rejected
    
    # Loan details
    requested_amount_inr = Column(Float, nullable=False)
    approved_amount_inr = Column(Float)
    interest_rate_annual_percent = Column(Float)
    tenure_months = Column(Integer, default=180)  # 15 years default
    
    # Computed loan details
    monthly_emi_inr = Column(Float)  # Calculated post-approval
    total_interest_inr = Column(Float)
    
    # Decision
    decision_date = Column(DateTime)
    decision_status = Column(String(50))  # approved, rejected, conditional
    rejection_reason = Column(Text)
    approval_offer_json = Column(JSON)  # Full offer details
    
    # Documents
    required_documents = Column(JSON, default=list)
    uploaded_documents = Column(JSON, default=list)  # {doc_type: filename, ...}
    
    # Timeline
    started_at = Column(DateTime, index=True)
    submitted_at = Column(DateTime)
    
    # Metadata
    notes = Column(Text)
    metadata = Column(JSON)  # Agent-generated insights, recommendations
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="loan_applications")
    
    __table_args__ = (
        Index("idx_loan_status_user", "status", "user_id"),
        Index("idx_loan_eligibility", "eligibility_score"),
    )
    
    def __repr__(self):
        return f"<LoanApplication(user_id={self.user_id}, status={self.status}, amount={self.requested_amount_inr})>"


class UserInteraction(Base):
    """
    Tracks all user interactions with the platform for recommendations and analytics.
    Powers implicit feedback for recommendation engine.
    """
    __tablename__ = "user_interactions"
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Interaction data
    interaction_type = Column(String(100), nullable=False, index=True)  # view, click, search, hover, apply, etc.
    entity_type = Column(String(50), nullable=False)  # course, university, blog, chatbot
    entity_id = Column(String(100), index=True)  # ID of the entity interacted with
    
    # Context
    session_id = Column(String(100), index=True)
    source = Column(String(100))  # recommendation, search, browse, referral, etc.
    
    # Metadata
    duration_seconds = Column(Integer)  # How long spent on entity
    query = Column(String(500))  # Search query if applicable
    metadata = Column(JSON)  # Additional context
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    
    __table_args__ = (
        Index("idx_interaction_user_time", "user_id", "created_at"),
        Index("idx_interaction_entity", "entity_type", "entity_id"),
        Index("idx_interaction_type", "interaction_type"),
    )


class Recommendation(Base):
    """
    ML-generated recommendations for users.
    Stores recommendation results and their effectiveness.
    """
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Recommendation details
    recommendation_type = Column(String(100), nullable=False, index=True)  # career_match, roi, course_similar, etc.
    
    # Recommended items
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"))
    
    # Scoring
    score = Column(Float, nullable=False)  # 0-100
    factors = Column(JSON)  # Explanation of recommendation {factor: weight, ...}
    
    # Effectiveness tracking
    was_viewed = Column(Boolean, default=False, index=True)
    was_clicked = Column(Boolean, default=False)
    was_applied = Column(Boolean, default=False)
    user_feedback = Column(String(20))  # liked, disliked, neutral
    
    # Meta
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    
    __table_args__ = (
        Index("idx_recommendation_user_type", "user_id", "recommendation_type"),
        Index("idx_recommendation_score", "score"),
    )


class LoanProduct(Base):
    """
    Education loan products offered by the platform.
    Used for offer generation and comparison.
    """
    __tablename__ = "loan_products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Product details
    name = Column(String(255), nullable=False)
    provider = Column(String(255))  # NBFC/Bank name
    description = Column(Text)
    
    # Terms
    min_amount_inr = Column(Float)
    max_amount_inr = Column(Float)
    min_tenure_months = Column(Integer)
    max_tenure_months = Column(Integer)
    
    # Pricing
    base_interest_rate = Column(Float)  # Base rate, can be adjusted per user
    processing_fee_percent = Column(Float)
    insurance_required = Column(Boolean, default=False)
    
    # Eligibility
    min_age = Column(Integer)
    max_age = Column(Integer)
    min_annual_income = Column(Float)
    required_collateral = Column(Boolean, default=False)
    
    # Features
    moratorium_period_months = Column(Integer)  # Grace period
    prepayment_allowed = Column(Boolean, default=True)
    prepayment_penalty_percent = Column(Float, default=0)
    
    # Targeting
    target_segments = Column(JSON, default=list)  # Applicable user segments
    
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<LoanProduct(name={self.name}, rate={self.base_interest_rate}%)>"


# Create indexes for performance
Index("idx_user_active_segment", "is_active", "user_segment")
Index("idx_user_engagement", "engagement_score")
