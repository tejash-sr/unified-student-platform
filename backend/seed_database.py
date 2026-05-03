#!/usr/bin/env python3
"""
Database Seeding Script - Populate with initial data
Loads universities, courses, and loan products for demo
"""

import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import User, University, Course, LoanProduct, Base
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# SEED DATA
# ============================================================================

UNIVERSITIES = [
    {
        "name": "Stanford University",
        "country": "USA",
        "city": "Stanford",
        "founded_year": 1885,
        "qs_ranking": 5,
        "times_ranking": 5,
        "shanghai_ranking": 4,
        "acceptance_rate": 4.0,
        "avg_admitted_gpa": 3.98,
        "avg_admitted_gre": 330,
        "avg_graduate_salary": 1800000,
        "average_tuition": 8000000,
        "university_description": "Top-tier research university known for innovation and technology programs."
    },
    {
        "name": "MIT",
        "country": "USA",
        "city": "Cambridge",
        "founded_year": 1861,
        "qs_ranking": 1,
        "times_ranking": 1,
        "shanghai_ranking": 2,
        "acceptance_rate": 3.3,
        "avg_admitted_gpa": 3.99,
        "avg_admitted_gre": 332,
        "avg_graduate_salary": 2000000,
        "average_tuition": 9000000,
        "university_description": "Leading engineering and technology institute."
    },
    {
        "name": "University of Oxford",
        "country": "UK",
        "city": "Oxford",
        "founded_year": 1096,
        "qs_ranking": 3,
        "times_ranking": 2,
        "shanghai_ranking": 7,
        "acceptance_rate": 5.0,
        "avg_admitted_gpa": 3.95,
        "avg_admitted_gre": 328,
        "avg_graduate_salary": 1200000,
        "average_tuition": 6000000,
        "university_description": "Oldest English-speaking university with global prestige."
    },
    {
        "name": "National University of Singapore",
        "country": "Singapore",
        "city": "Singapore",
        "founded_year": 1905,
        "qs_ranking": 8,
        "times_ranking": 11,
        "shanghai_ranking": 151,
        "acceptance_rate": 15.0,
        "avg_admitted_gpa": 3.85,
        "avg_admitted_gre": 325,
        "avg_graduate_salary": 1000000,
        "average_tuition": 5000000,
        "university_description": "Asia's leading research university."
    },
    {
        "name": "University of Melbourne",
        "country": "Australia",
        "city": "Melbourne",
        "founded_year": 1853,
        "qs_ranking": 37,
        "times_ranking": 37,
        "shanghai_ranking": 51,
        "acceptance_rate": 30.0,
        "avg_admitted_gpa": 3.8,
        "avg_admitted_gre": 320,
        "avg_graduate_salary": 900000,
        "average_tuition": 4500000,
        "university_description": "Australia's premier research-intensive university."
    },
]

COURSES = [
    {
        "university_index": 0,
        "name": "M.S. Computer Science",
        "field_of_study": "Computer Science",
        "degree_type": "Master's",
        "duration_months": 24,
        "total_tuition_cost": 8000000,
        "min_cgpa_required": 3.5,
        "min_gre_required": 320,
        "min_gmat_required": None,
        "min_ielts_required": 7.0,
        "avg_salary_year_1": 1200000,
        "avg_salary_year_5": 2000000,
        "intake_per_year": 500,
        "application_deadline": "2026-12-15",
        "course_description": "Advanced computer science program covering AI, systems, and software engineering."
    },
    {
        "university_index": 1,
        "name": "M.S. AI/Machine Learning",
        "field_of_study": "Data Science",
        "degree_type": "Master's",
        "duration_months": 24,
        "total_tuition_cost": 9000000,
        "min_cgpa_required": 3.6,
        "min_gre_required": 330,
        "min_gmat_required": None,
        "min_ielts_required": 7.5,
        "avg_salary_year_1": 1500000,
        "avg_salary_year_5": 2500000,
        "intake_per_year": 300,
        "application_deadline": "2026-12-01",
        "course_description": "Intensive program in artificial intelligence and machine learning applications."
    },
    {
        "university_index": 2,
        "name": "M.B.A.",
        "field_of_study": "Business",
        "degree_type": "Master's",
        "duration_months": 24,
        "total_tuition_cost": 6000000,
        "min_cgpa_required": 3.3,
        "min_gre_required": None,
        "min_gmat_required": 650,
        "min_ielts_required": 7.0,
        "avg_salary_year_1": 800000,
        "avg_salary_year_5": 1500000,
        "intake_per_year": 400,
        "application_deadline": "2026-11-30",
        "course_description": "World-class business administration program with global placements."
    },
    {
        "university_index": 3,
        "name": "B.S. Computer Science",
        "field_of_study": "Computer Science",
        "degree_type": "Bachelor's",
        "duration_months": 48,
        "total_tuition_cost": 5000000,
        "min_cgpa_required": 3.2,
        "min_gre_required": None,
        "min_gmat_required": None,
        "min_ielts_required": 6.5,
        "avg_salary_year_1": 600000,
        "avg_salary_year_5": 1200000,
        "intake_per_year": 800,
        "application_deadline": "2026-11-15",
        "course_description": "Comprehensive undergraduate program in computer science and engineering."
    },
    {
        "university_index": 4,
        "name": "M.S. Engineering",
        "field_of_study": "Engineering",
        "degree_type": "Master's",
        "duration_months": 24,
        "total_tuition_cost": 4500000,
        "min_cgpa_required": 3.4,
        "min_gre_required": 315,
        "min_gmat_required": None,
        "min_ielts_required": 6.5,
        "avg_salary_year_1": 900000,
        "avg_salary_year_5": 1600000,
        "intake_per_year": 600,
        "application_deadline": "2026-11-20",
        "course_description": "Advanced engineering program with specializations in multiple fields."
    },
]

LOAN_PRODUCTS = [
    {
        "name": "Standard Education Loan",
        "provider": "StudePath Finance",
        "min_loan_amount": 500000,
        "max_loan_amount": 2000000,
        "base_interest_rate": 8.5,
        "tenure_months": 180,
        "processing_fee_percent": 1.0,
        "moratorium_months": 6,
        "prepayment_allowed": True,
        "target_segment": "warm",
        "eligibility_criteria": {"min_annual_income": 400000}
    },
    {
        "name": "Premium Education Loan",
        "provider": "StudePath Finance",
        "min_loan_amount": 1000000,
        "max_loan_amount": 5000000,
        "base_interest_rate": 7.9,
        "tenure_months": 240,
        "processing_fee_percent": 0.75,
        "moratorium_months": 12,
        "prepayment_allowed": True,
        "target_segment": "hot",
        "eligibility_criteria": {"min_annual_income": 800000, "min_cgpa": 3.5}
    },
    {
        "name": "Starter Education Loan",
        "provider": "StudePath Finance",
        "min_loan_amount": 250000,
        "max_loan_amount": 800000,
        "base_interest_rate": 9.5,
        "tenure_months": 120,
        "processing_fee_percent": 1.5,
        "moratorium_months": 3,
        "prepayment_allowed": True,
        "target_segment": "cold",
        "eligibility_criteria": {"min_annual_income": 200000}
    },
]

# ============================================================================
# SEEDING FUNCTIONS
# ============================================================================

def seed_universities(db: Session):
    """Seed universities into database."""
    logger.info("🏫 Seeding universities...")
    
    for uni_data in UNIVERSITIES:
        existing = db.query(University).filter_by(name=uni_data["name"]).first()
        if existing:
            logger.info(f"  ✓ {uni_data['name']} already exists")
            continue
        
        university = University(**uni_data)
        db.add(university)
    
    db.commit()
    logger.info(f"✓ Seeded {len(UNIVERSITIES)} universities")


def seed_courses(db: Session):
    """Seed courses into database."""
    logger.info("📚 Seeding courses...")
    
    universities = db.query(University).all()
    count = 0
    
    for course_data in COURSES:
        uni = universities[course_data.pop("university_index")]
        
        existing = db.query(Course).filter_by(
            name=course_data["name"],
            university_id=uni.id
        ).first()
        
        if existing:
            logger.info(f"  ✓ {course_data['name']} at {uni.name} already exists")
            continue
        
        course = Course(
            university_id=uni.id,
            **course_data
        )
        db.add(course)
        count += 1
    
    db.commit()
    logger.info(f"✓ Seeded {count} courses")


def seed_loan_products(db: Session):
    """Seed loan products into database."""
    logger.info("💰 Seeding loan products...")
    
    count = 0
    for product_data in LOAN_PRODUCTS:
        existing = db.query(LoanProduct).filter_by(name=product_data["name"]).first()
        if existing:
            logger.info(f"  ✓ {product_data['name']} already exists")
            continue
        
        product = LoanProduct(
            **product_data,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(product)
        count += 1
    
    db.commit()
    logger.info(f"✓ Seeded {count} loan products")


def main():
    """Run all seeding functions."""
    logger.info("=" * 60)
    logger.info("🌱 DATABASE SEEDING STARTED")
    logger.info("=" * 60)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        seed_universities(db)
        seed_courses(db)
        seed_loan_products(db)
        
        # Log summary
        logger.info("=" * 60)
        logger.info("✅ SEEDING COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Universities: {db.query(University).count()}")
        logger.info(f"Courses: {db.query(Course).count()}")
        logger.info(f"Loan Products: {db.query(LoanProduct).count()}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
