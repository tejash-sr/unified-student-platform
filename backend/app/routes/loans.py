"""
Loan eligibility, calculation, and application management routes.
Core conversion funnel for the platform.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core import get_db, verify_token
from app.models import User, LoanApplication, LoanProduct
from app.schemas import (
    LoanEligibilityRequest,
    LoanEligibilityResponse,
    EMICalculationRequest,
    EMICalculationResponse,
    LoanApplicationCreate,
    LoanApplicationResponse,
    LoanOfferResponse,
)
from app.utils import financial, eligibility as eligibility_scorer
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


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
# ELIGIBILITY & PRE-QUALIFICATION
# ============================================================================

@router.post(
    "/eligibility-check",
    response_model=LoanEligibilityResponse,
    summary="Check loan eligibility",
    tags=["Eligibility"],
)
async def check_eligibility(
    request: LoanEligibilityRequest,
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Quick eligibility assessment based on user profile and loan amount.
    
    Returns:
    - Eligibility score (0-100)
    - Category (approved, conditional, rejected)
    - Potential offer details
    - Required documents
    """
    user = get_current_user_from_header(authorization, db)
    
    # Use provided income or user's current income
    annual_income = request.annual_income or user.annual_income or 500000
    employment_years = user.work_experience_years or 0
    
    # Academic score (convert CGPA to 0-100 scale or use GRE percentile)
    if user.current_cgpa:
        academic_score = (user.current_cgpa / 4.0) * 100
    elif user.gre_score:
        academic_score = ((user.gre_score - 260) / (340 - 260)) * 100
    else:
        academic_score = 50  # Default for fresh graduates
    
    # Score user
    score, category, reasons = eligibility_scorer.score_user(
        annual_income=annual_income,
        employment_years=employment_years,
        gpa_or_gre=academic_score,
        academic_excellence=academic_score / 100,
    )
    
    # Determine approved amount (conservative: 1.5x annual income cap)
    max_approved = min(
        request.requested_amount_inr,
        annual_income * 1.5
    )
    
    # Interest rate based on score (8-12% range)
    if score >= 75:
        interest_rate = 8.5
    elif score >= 60:
        interest_rate = 9.5
    else:
        interest_rate = 11.0
    
    # Calculate sample EMI
    potential_emi = financial.calculate_emi(
        max_approved,
        interest_rate,
        180  # 15 years
    )
    
    # Required documents
    required_docs = [
        "Government ID",
        "Educational Certificates",
        "Income Proof",
        "Employment Letter",
        "Bank Statements (6 months)",
        "Offer Letter from University",
    ]
    
    if score < 60:
        required_docs.extend([
            "Co-applicant Documents",
            "Collateral Details",
        ])
    
    return LoanEligibilityResponse(
        eligibility_score=score,
        eligibility_category=category,
        eligibility_reasons=reasons,
        potential_approved_amount=max_approved,
        potential_interest_rate=interest_rate,
        potential_monthly_emi=round(potential_emi, 2),
        required_documents=required_docs,
    )


# ============================================================================
# EMI CALCULATOR
# ============================================================================

@router.post(
    "/calculate-emi",
    response_model=EMICalculationResponse,
    summary="Calculate EMI and amortization schedule",
    tags=["Calculator"],
)
async def calculate_emi(request: EMICalculationRequest):
    """
    Calculate monthly EMI and generate full amortization schedule.
    
    No authentication required (public tool).
    """
    # Validate inputs
    if request.principal_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Principal amount must be positive",
        )
    
    if request.tenure_months <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenure must be positive",
        )
    
    # Calculate EMI
    monthly_emi = financial.calculate_emi(
        request.principal_amount,
        request.interest_rate_annual,
        request.tenure_months
    )
    
    total_amount = monthly_emi * request.tenure_months
    total_interest = total_amount - request.principal_amount
    
    # Generate amortization schedule
    schedule = financial.generate_amortization_schedule(
        request.principal_amount,
        request.interest_rate_annual,
        request.tenure_months
    )
    
    return EMICalculationResponse(
        monthly_emi=round(monthly_emi, 2),
        total_amount=round(total_amount, 2),
        total_interest=round(total_interest, 2),
        amortization_schedule=schedule,
    )


# ============================================================================
# LOAN APPLICATION
# ============================================================================

@router.post(
    "/apply",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create loan application",
    tags=["Application"],
)
async def create_loan_application(
    request: LoanApplicationCreate,
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Initiate a new loan application.
    
    Returns application ID and initial status.
    """
    user = get_current_user_from_header(authorization, db)
    
    # Validation
    if request.requested_amount_inr < 100000:  # Min 1 lakh
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum loan amount is 100,000 INR",
        )
    
    if request.requested_amount_inr > 5000000:  # Max 50 lakhs
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum loan amount is 5,000,000 INR",
        )
    
    # Create application
    loan_app = LoanApplication(
        user_id=user.id,
        status="inquiry",
        application_type="education-specific",
        requested_amount_inr=request.requested_amount_inr,
        tenure_months=request.tenure_months,
        started_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(loan_app)
    db.commit()
    db.refresh(loan_app)
    
    logger.info(f"✅ Loan application created: ID={loan_app.id}, User={user.email}")
    
    return LoanApplicationResponse.model_validate(loan_app)


@router.get(
    "/{loan_id}",
    response_model=LoanApplicationResponse,
    summary="Get loan application details",
    tags=["Application"],
)
async def get_loan_application(
    loan_id: int,
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve loan application details.
    """
    user = get_current_user_from_header(authorization, db)
    
    loan_app = db.query(LoanApplication).filter(
        LoanApplication.id == loan_id,
        LoanApplication.user_id == user.id
    ).first()
    
    if not loan_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan application not found",
        )
    
    return LoanApplicationResponse.model_validate(loan_app)


@router.get(
    "",
    response_model=list,
    summary="Get user's loan applications",
    tags=["Application"],
)
async def get_user_loans(
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    List all loan applications for current user.
    """
    user = get_current_user_from_header(authorization, db)
    
    loans = db.query(LoanApplication).filter(
        LoanApplication.user_id == user.id
    ).order_by(LoanApplication.created_at.desc()).all()
    
    return [LoanApplicationResponse.model_validate(loan) for loan in loans]


# ============================================================================
# LOAN OFFER & DECISION
# ============================================================================

@router.post(
    "/{loan_id}/pre-qualify",
    response_model=LoanOfferResponse,
    summary="Pre-qualification: generate offer",
    tags=["Offer"],
)
async def pre_qualify_application(
    loan_id: int,
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Pre-qualify application and generate dynamic loan offer.
    
    This is where eligibility is converted to actual offer.
    """
    user = get_current_user_from_header(authorization, db)
    
    loan_app = db.query(LoanApplication).filter(
        LoanApplication.id == loan_id,
        LoanApplication.user_id == user.id
    ).first()
    
    if not loan_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan application not found",
        )
    
    # Score user
    annual_income = user.annual_income or 500000
    employment_years = user.work_experience_years or 0
    academic_score = (user.current_cgpa / 4.0 * 100) if user.current_cgpa else 50
    
    score, category, _ = eligibility_scorer.score_user(
        annual_income=annual_income,
        employment_years=employment_years,
        gpa_or_gre=academic_score,
    )
    
    # Store score
    loan_app.eligibility_score = score
    loan_app.eligibility_category = category
    
    if category == "rejected":
        loan_app.status = "rejected"
        loan_app.decision_status = "rejected"
        loan_app.rejection_reason = "Eligibility score below threshold"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application rejected due to eligibility criteria",
        )
    
    # Calculate offer
    approved_amount = min(
        loan_app.requested_amount_inr,
        annual_income * 1.5
    )
    
    # Interest rate based on score
    interest_rate = 8.5 if score >= 75 else 9.5 if score >= 60 else 11.0
    
    # Calculate EMI
    monthly_emi = financial.calculate_emi(approved_amount, interest_rate, 180)
    total_interest = financial.calculate_total_interest(approved_amount, interest_rate, 180)
    
    # Processing fee
    processing_fee = approved_amount * 0.01  # 1%
    
    # Update application
    loan_app.status = "pre-qualified"
    loan_app.approved_amount_inr = approved_amount
    loan_app.interest_rate_annual_percent = interest_rate
    loan_app.monthly_emi_inr = monthly_emi
    loan_app.total_interest_inr = total_interest
    loan_app.approval_offer_json = {
        "approved_amount": float(approved_amount),
        "interest_rate": float(interest_rate),
        "monthly_emi": float(monthly_emi),
        "tenure_months": 180,
        "processing_fee": float(processing_fee),
        "moratorium_months": 6,
        "prepayment_allowed": True,
    }
    
    db.commit()
    db.refresh(loan_app)
    
    logger.info(f"✅ Loan pre-qualified: ID={loan_id}, Amount={approved_amount}, Rate={interest_rate}%")
    
    return LoanOfferResponse(
        loan_application_id=loan_app.id,
        approved_amount=approved_amount,
        interest_rate=interest_rate,
        tenure_months=180,
        monthly_emi=monthly_emi,
        total_interest=total_interest,
        processing_fee=processing_fee,
        moratorium_months=6,
        prepayment_allowed=True,
    )


@router.post(
    "/{loan_id}/submit",
    response_model=LoanApplicationResponse,
    summary="Submit full application",
    tags=["Application"],
)
async def submit_full_application(
    loan_id: int,
    authorization: str = None,
    db: Session = Depends(get_db),
):
    """
    Submit full loan application with all documents.
    """
    user = get_current_user_from_header(authorization, db)
    
    loan_app = db.query(LoanApplication).filter(
        LoanApplication.id == loan_id,
        LoanApplication.user_id == user.id
    ).first()
    
    if not loan_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan application not found",
        )
    
    if loan_app.status != "pre-qualified":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application must be pre-qualified before submission",
        )
    
    # Update status
    loan_app.status = "applied"
    loan_app.submitted_at = datetime.now(timezone.utc)
    
    # In real scenario, documents would be verified by agents
    # For now, mark as under review
    
    db.commit()
    db.refresh(loan_app)
    
    logger.info(f"✅ Loan application submitted: ID={loan_id}")
    
    return LoanApplicationResponse.model_validate(loan_app)


# ============================================================================
# LOAN PRODUCTS
# ============================================================================

@router.get(
    "/products",
    response_model=list,
    summary="Get available loan products",
    tags=["Products"],
)
async def get_loan_products(
    db: Session = Depends(get_db),
    limit: int = Query(10, le=100),
):
    """
    Get list of available education loan products.
    
    Public endpoint (no auth required).
    """
    products = db.query(LoanProduct).filter(
        LoanProduct.is_active == True
    ).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "provider": p.provider,
            "base_interest_rate": p.base_interest_rate,
            "min_amount": p.min_amount_inr,
            "max_amount": p.max_amount_inr,
            "processing_fee_percent": p.processing_fee_percent,
        }
        for p in products
    ]
