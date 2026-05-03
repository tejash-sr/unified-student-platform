# Unified Student Platform - Backend API

**Production-grade FastAPI backend** for AI-first student engagement and education loan platform.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis (optional, for caching)

### Installation

```bash
# 1. Clone repository
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 5. Initialize database
python -m app.core.database

# 6. Run server
uvicorn app.main:app --reload
```

Server will be available at: `http://localhost:8000`

- **API Docs**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

---

## 📊 Architecture

### Core Layers

```
┌─────────────────────────────────────────────┐
│          FastAPI Application                │
│  - Routes (Users, Loans, Courses, etc.)    │
│  - Request/Response validation              │
│  - Authentication & Authorization           │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│         Business Logic Services             │
│  - Recommendation Engine                    │
│  - Loan Eligibility Scoring                 │
│  - ROI Calculation                          │
│  - Timeline Generation                      │
│  - Engagement Scoring                       │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│         Data & AI Infrastructure            │
│  - SQLAlchemy ORM (PostgreSQL)             │
│  - ChromaDB (Vector Similarity)             │
│  - Sentence Transformers (Embeddings)       │
│  - Implicit (Recommendations)               │
└─────────────────────────────────────────────┘
```

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── core/
│   │   ├── config.py          # Settings management
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── security.py        # JWT & hashing
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py        # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── __init__.py        # Pydantic validation schemas
│   ├── routes/
│   │   ├── users.py           # User auth & profile
│   │   ├── loans.py           # Loan eligibility & application
│   │   ├── courses.py         # Course discovery (TBD)
│   │   ├── recommendations.py # Recommendations & ROI (TBD)
│   │   └── __init__.py
│   ├── services/
│   │   ├── recommendation.py  # Recommendation engine (TBD)
│   │   ├── eligibility.py     # Loan scoring (TBD)
│   │   └── __init__.py
│   ├── agents/
│   │   ├── growth.py          # CrewAI growth loops (TBD)
│   │   ├── chatbot.py         # LLM integration (TBD)
│   │   └── __init__.py
│   └── utils/
│       ├── calculations.py    # Financial & ML math
│       ├── embeddings.py      # Vector DB & semantic search
│       └── __init__.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/users/signup` - Register new student
- `POST /api/users/login` - Login with email/password
- `POST /api/users/refresh` - Refresh access token
- `POST /api/users/logout` - Logout

### Profile
- `GET /api/users/profile` - Get current user profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/profile/engagement` - Get engagement metrics

### Loans
- `POST /api/loans/eligibility-check` - Check eligibility
- `POST /api/loans/calculate-emi` - Calculate EMI
- `POST /api/loans/apply` - Create loan application
- `POST /api/loans/{loan_id}/pre-qualify` - Generate offer
- `POST /api/loans/{loan_id}/submit` - Submit full application
- `GET /api/loans/{loan_id}` - Get application details
- `GET /api/loans` - List user's applications
- `GET /api/loans/products` - Available loan products

### System
- `GET /health` - Health check
- `GET /info` - API information

---

## 🤖 Key Services

### 1. Financial Calculator
```python
from app.utils import financial

# Calculate monthly EMI
emi = financial.calculate_emi(
    principal=1000000,      # 10 lakh INR
    annual_rate=8.5,        # 8.5% per year
    tenure_months=180       # 15 years
)
# Returns: 9627.09

# Generate amortization schedule
schedule = financial.generate_amortization_schedule(...)
# Returns: List of month-by-month payments

# Calculate payback period
payback, cost, confidence = financial.calculate_payback_period(
    loan_amount=1000000,
    annual_interest_rate=8.5,
    annual_salary=1200000
)
# Returns: (months_to_payback, total_cost, confidence_score)
```

### 2. Eligibility Scorer
```python
from app.utils import eligibility

# Score user for loan eligibility
score, category, reasons = eligibility.score_user(
    annual_income=750000,
    employment_years=2,
    gpa_or_gre=75,
    academic_excellence=0.75
)
# Returns: (75.5, "approved", ["✓ Strong income", ...])
```

### 3. ROI Calculator
```python
from app.utils import roi

# Calculate ROI for education
result = roi.calculate_roi(
    total_cost=2500000,
    expected_salary_year1=1000000,
    expected_salary_year5=1800000,
    loan_amount=1000000,
    loan_interest_rate=8.5
)
# Returns: {
#   'roi_percent_5yr': 45.2,
#   'breakeven_months': 120,
#   ...
# }
```

### 4. Embeddings & Semantic Search
```python
from app.utils import get_vector_db, get_embedding_service

# Semantic search
vector_db = get_vector_db()
results = vector_db.search(
    query="Best MS Computer Science programs in USA",
    n_results=5
)
# Returns: List of matching courses with similarity scores

# Calculate similarity
embeddings = get_embedding_service()
score = embeddings.similarity(
    "MS Data Science in US",
    "Master's in Data Science, United States"
)
# Returns: 0.92 (cosine similarity)
```

### 5. Engagement Scorer
```python
from app.utils import engagement

# Calculate engagement & assign segment
score = engagement.calculate_engagement_score(
    interactions_count=50,
    applications_count=3,
    days_since_signup=45,
    profile_completeness=0.85
)
# Returns: 72.4

segment = engagement.assign_segment(score, applications_count=3)
# Returns: "applications" or "decision"
```

---

## 🔐 Authentication

All protected endpoints require JWT token in `Authorization` header:

```bash
Authorization: Bearer eyJhbGc...
```

**Token Flow:**
1. Signup/Login → Returns `access_token` and `refresh_token`
2. Use `access_token` for API calls (30-minute expiry)
3. When expired, use `refresh_token` to get new `access_token` (7-day expiry)

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/users/profile
```

---

## 📊 Database Schema

### Key Tables

| Table | Purpose |
|-------|---------|
| `users` | Student profiles with education/financial data |
| `universities` | University metadata (rankings, costs, outcomes) |
| `courses` | Program information (requirements, salaries) |
| `applications` | Student application tracking |
| `timeline_events` | Milestone tracking for applications |
| `loan_applications` | Loan eligibility & decisions |
| `user_interactions` | Event logging for recommendations |
| `recommendations` | ML-generated suggestions |
| `loan_products` | Available education loan products |

### Vector Search (ChromaDB)
- Documents: Course descriptions, university profiles, application guides
- Collections: `student_knowledge_base` (for RAG chatbot)
- Embeddings: 384-dimensional (all-MiniLM-L6-v2 model)

---

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t student-platform-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e GROQ_API_KEY=... \
  student-platform-backend
```

### Railway / Render / AWS

1. Push to Git repository
2. Connect to Railway/Render/AWS
3. Set environment variables
4. Deploy

Example Railway URL: `https://app-name-production.up.railway.app`

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_loans.py -v
```

---

## 📝 Logging

Logs are configured to show:
- API requests/responses
- Database operations
- AI service calls (LLM, embeddings)
- User actions (signup, application submit)

Check logs in console or configure file logging in `app/main.py`.

---

## 🔗 Integration Points

### Groq API (LLM)
- Used by chatbot for conversational guidance
- Free tier: Sufficient for competition prototype

### SendGrid
- Email notifications for loan offers
- Application deadline reminders
- Engagement campaigns (via N8N)

### ChromaDB
- Vector database for RAG chatbot
- Semantic course/university matching
- Local deployment (no external dependency)

### N8N (Automation)
- User onboarding workflows
- Loan eligibility → offer emails
- Engagement loop triggers
- Webhooks: `POST /webhook/student-events`

---

## ⚡ Performance Optimization

### Database
- Connection pooling: 10 connections
- Indexed queries on frequently filtered fields
- Query logging in debug mode

### Caching
- Redis for session data (optional)
- ChromaDB in-memory embeddings cache

### Async
- FastAPI native async/await
- Non-blocking LLM API calls
- Background task support (Celery optional)

---

## 🐛 Troubleshooting

### Database Connection Error
```
ERROR: could not translate host name "localhost" to address
```
**Solution**: Check PostgreSQL is running, verify `DATABASE_URL` in `.env`

### Missing Dependencies
```bash
# Reinstall requirements
pip install --no-cache-dir -r requirements.txt
```

### Token Expiry
```
"Invalid or expired token"
```
**Solution**: Use refresh token endpoint to get new access token

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --port 8001
```

---

## 📚 Next Steps

1. **Integrate CrewAI Growth Agents** (`app/agents/growth.py`)
2. **Build Recommendation Engine** (`app/services/recommendation.py`)
3. **Setup Flowise Chatbot** (`app/agents/chatbot.py`)
4. **Create Course/University Routes** (`app/routes/courses.py`)
5. **Add N8N Workflow Triggers**
6. **Implement Analytics Events**

---

## 📄 License

This project is part of the TensorFlow 2026 Competition.

---

## 💬 Support

For issues or questions:
1. Check `/health` endpoint
2. Review logs in console
3. Check `.env` configuration
4. Verify database connectivity

---

**Built with ❤️ for student success**
