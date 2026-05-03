"""
Utility functions for calculations, embeddings, and data processing.
"""

import math
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# FINANCIAL CALCULATIONS
# ============================================================================

class FinancialCalculator:
    """Financial calculations for loan products."""
    
    @staticmethod
    def calculate_emi(
        principal: float,
        annual_rate: float,
        tenure_months: int
    ) -> float:
        """
        Calculate monthly EMI (Equated Monthly Installment).
        
        Formula: EMI = [P × r × (1+r)^n] / [(1+r)^n - 1]
        Where:
        P = Principal
        r = Monthly interest rate (annual rate / 12 / 100)
        n = Number of months
        """
        if annual_rate == 0:
            return principal / tenure_months
        
        monthly_rate = annual_rate / 12 / 100
        numerator = principal * monthly_rate * (1 + monthly_rate) ** tenure_months
        denominator = (1 + monthly_rate) ** tenure_months - 1
        
        return numerator / denominator
    
    @staticmethod
    def generate_amortization_schedule(
        principal: float,
        annual_rate: float,
        tenure_months: int
    ) -> List[Dict[str, Any]]:
        """Generate month-by-month amortization schedule."""
        emi = FinancialCalculator.calculate_emi(principal, annual_rate, tenure_months)
        monthly_rate = annual_rate / 12 / 100
        balance = principal
        
        schedule = []
        for month in range(1, tenure_months + 1):
            interest_payment = balance * monthly_rate
            principal_payment = emi - interest_payment
            balance -= principal_payment
            
            # Ensure balance doesn't go negative due to rounding
            if balance < 0:
                principal_payment += balance
                balance = 0
            
            schedule.append({
                "month": month,
                "emi": round(emi, 2),
                "principal": round(principal_payment, 2),
                "interest": round(interest_payment, 2),
                "balance": round(max(0, balance), 2),
            })
        
        return schedule
    
    @staticmethod
    def calculate_total_interest(
        principal: float,
        annual_rate: float,
        tenure_months: int
    ) -> float:
        """Calculate total interest to be paid."""
        emi = FinancialCalculator.calculate_emi(principal, annual_rate, tenure_months)
        return (emi * tenure_months) - principal
    
    @staticmethod
    def calculate_payback_period(
        loan_amount: float,
        annual_interest_rate: float,
        annual_salary: float,
        salary_growth_annual_percent: float = 0.05
    ) -> Tuple[float, float, float]:
        """
        Calculate payback period for education loan.
        
        Returns: (payback_months, total_cost, confidence_score)
        """
        monthly_rate = annual_interest_rate / 12 / 100
        monthly_salary = annual_salary / 12
        
        balance = loan_amount
        months = 0
        max_months = 360  # 30 years max
        
        while balance > 0 and months < max_months:
            months += 1
            
            # EMI grows with salary
            if months % 12 == 0:
                monthly_salary *= (1 + salary_growth_annual_percent)
            
            # Assume 30% of monthly salary goes to loan repayment
            available_for_emi = monthly_salary * 0.30
            emi = FinancialCalculator.calculate_emi(balance, annual_interest_rate, 360 - months)
            
            actual_payment = min(available_for_emi, emi)
            interest = balance * monthly_rate
            
            if actual_payment <= interest:
                # Can't repay, mark as risky
                return (None, None, 0.2)
            
            principal_payment = actual_payment - interest
            balance -= principal_payment
        
        if balance > 0:
            return (None, None, 0.3)  # Couldn't repay within 30 years
        
        total_cost = loan_amount + FinancialCalculator.calculate_total_interest(
            loan_amount, annual_interest_rate, months
        )
        confidence = min(0.95, 0.5 + (1 - (months / max_months)) * 0.45)
        
        return (months, total_cost, confidence)


# ============================================================================
# ELIGIBILITY SCORING
# ============================================================================

class EligibilityScorer:
    """Loan eligibility scoring engine."""
    
    @staticmethod
    def score_user(
        annual_income: float,
        employment_years: float,
        gpa_or_gre: float,  # CGPA (0-4.0) or GRE score percentile (0-100)
        academic_excellence: float,  # 0-1.0
        debt_to_income_ratio: float = 0.0,  # 0-1.0
        collateral_value: float = 0.0,
    ) -> Tuple[float, str, List[str]]:
        """
        Comprehensive eligibility scoring.
        
        Returns: (score, category, reasons)
        """
        score = 0
        reasons = []
        
        # Income score (40%)
        income_score = min(100, (annual_income / 750000) * 100)  # Base: 7.5 LPA
        score += income_score * 0.40
        if income_score >= 70:
            reasons.append("✓ Strong annual income")
        else:
            reasons.append("⚠ Moderate income; may require co-applicant")
        
        # Employment stability (25%)
        stability_score = min(100, (employment_years / 5) * 100)
        score += stability_score * 0.25
        if employment_years >= 2:
            reasons.append("✓ Good employment stability")
        elif employment_years >= 1:
            reasons.append("⚠ Recent graduate; limited work history")
        else:
            reasons.append("! Fresher; may require co-applicant")
        
        # Academic excellence (20%)
        academic_score = gpa_or_gre  # Assume 0-100
        score += academic_score * 0.20
        if gpa_or_gre >= 75:
            reasons.append("✓ Strong academic profile")
        elif gpa_or_gre >= 60:
            reasons.append("⚠ Average academic profile")
        else:
            reasons.append("! Weak academic profile")
        
        # Debt-to-income ratio (10%)
        if debt_to_income_ratio < 0.2:
            debt_score = 100
            reasons.append("✓ Low existing debt")
        elif debt_to_income_ratio < 0.4:
            debt_score = 70
            reasons.append("⚠ Moderate existing debt")
        else:
            debt_score = 30
            reasons.append("! High existing debt")
        
        score += debt_score * 0.10
        
        # Collateral (5%)
        if collateral_value > loan_amount * 0.5:
            collateral_score = 100
        elif collateral_value > 0:
            collateral_score = 60
        else:
            collateral_score = 30
        
        score += collateral_score * 0.05
        
        # Categorize
        if score >= 75:
            category = "approved"
        elif score >= 60:
            category = "conditional"
        else:
            category = "rejected"
        
        return (score, category, reasons)


# ============================================================================
# ROI CALCULATIONS
# ============================================================================

class ROICalculator:
    """Calculate return on investment for education."""
    
    @staticmethod
    def calculate_roi(
        total_cost: float,  # Tuition + living
        expected_salary_year1: float,
        expected_salary_year5: float,
        loan_amount: float,
        loan_interest_rate: float,
        tenure_months: int = 180,
    ) -> Dict[str, Any]:
        """Calculate comprehensive ROI metrics."""
        
        # Total cost including interest
        total_loan_cost = loan_amount + FinancialCalculator.calculate_total_interest(
            loan_amount, loan_interest_rate, tenure_months
        )
        
        # Gross benefit (salary over 5 years, assuming 5% annual growth)
        year1_salary = expected_salary_year1
        salary_growth = 0.05
        
        gross_benefit = 0
        for year in range(1, 6):
            salary = year1_salary * (1 + salary_growth) ** (year - 1)
            # Assume 70% of salary is discretionary (30% goes to essentials)
            discretionary = salary * 0.70
            gross_benefit += discretionary
        
        # Net benefit
        net_benefit = gross_benefit - total_loan_cost
        
        # ROI percentage
        roi_percent = (net_benefit / total_cost) * 100 if total_cost > 0 else 0
        
        # Break-even analysis
        cumulative_salary = 0
        breakeven_month = None
        monthly_salary = expected_salary_year1 / 12
        emi = FinancialCalculator.calculate_emi(loan_amount, loan_interest_rate, tenure_months)
        
        for month in range(1, 361):
            # Adjust salary annually
            if month % 12 == 0:
                monthly_salary *= (1 + salary_growth)
            
            net_monthly = monthly_salary * 0.70 - emi
            cumulative_salary += net_monthly
            
            if cumulative_salary >= total_loan_cost and breakeven_month is None:
                breakeven_month = month
        
        return {
            "total_cost": round(total_cost, 2),
            "total_loan_cost": round(total_loan_cost, 2),
            "gross_benefit_5yr": round(gross_benefit, 2),
            "net_benefit_5yr": round(net_benefit, 2),
            "roi_percent_5yr": round(roi_percent, 2),
            "breakeven_months": breakeven_month,
            "expected_salary_year1": round(expected_salary_year1, 2),
            "expected_salary_year5": round(expected_salary_year5, 2),
        }


# ============================================================================
# ENGAGEMENT SCORING
# ============================================================================

class EngagementScorer:
    """Calculate user engagement and segment scores."""
    
    @staticmethod
    def calculate_engagement_score(
        interactions_count: int,
        applications_count: int,
        days_since_signup: int,
        profile_completeness: float,  # 0-1.0
    ) -> float:
        """Calculate overall engagement score (0-100)."""
        
        score = 0
        
        # Interaction frequency (30%)
        interaction_score = min(100, (interactions_count / 50) * 100)
        score += interaction_score * 0.30
        
        # Application progress (35%)
        application_score = min(100, (applications_count / 5) * 100)
        score += application_score * 0.35
        
        # Retention (25%)
        retention_score = min(100, (days_since_signup / 90) * 100)
        score += retention_score * 0.25
        
        # Profile completeness (10%)
        score += profile_completeness * 100 * 0.10
        
        return score
    
    @staticmethod
    def assign_segment(engagement_score: float, applications_count: int) -> str:
        """Assign user segment based on engagement."""
        
        if applications_count >= 3 and engagement_score >= 60:
            return "decision"
        elif applications_count >= 1 or engagement_score >= 40:
            return "applications"
        else:
            return "exploration"


# ============================================================================
# TIMELINE GENERATION
# ============================================================================

class TimelineGenerator:
    """Generate application timeline."""
    
    DEFAULT_TIMELINE_TEMPLATE = {
        "Test Preparation": {"duration_days": 120, "relative_to": "start"},
        "University Research": {"duration_days": 60, "relative_to": "start"},
        "Essays & SOP": {"duration_days": 45, "relative_to": "test_end"},
        "Recommendation Letters": {"duration_days": 30, "relative_to": "essays_start"},
        "Application Submission": {"duration_days": 1, "relative_to": "letters_end"},
        "Interview Prep (if needed)": {"duration_days": 30, "relative_to": "submission"},
        "Decision": {"duration_days": 1, "relative_to": "decision_date"},
    }
    
    @staticmethod
    def generate_timeline(
        start_date: datetime,
        deadline_date: datetime,
        custom_events: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Generate timeline from now to deadline."""
        
        events = []
        current_date = datetime.utcnow()
        days_available = (deadline_date - current_date).days
        
        # Adjust timeline based on available days
        for event_name, event_config in TimelineGenerator.DEFAULT_TIMELINE_TEMPLATE.items():
            duration = event_config["duration_days"]
            
            # Don't create past events
            event_start = start_date + timedelta(days=event_config.get("start_offset", 0))
            if event_start < current_date:
                event_start = current_date
            
            events.append({
                "event_type": event_name.lower().replace(" ", "_"),
                "title": event_name,
                "scheduled_date": event_start,
                "estimated_duration_days": duration,
                "priority": "high" if event_name in ["Essays & SOP", "Application Submission"] else "medium",
            })
        
        return events


# Convenience exports
financial = FinancialCalculator()
eligibility = EligibilityScorer()
roi = ROICalculator()
engagement = EngagementScorer()
timeline = TimelineGenerator()
