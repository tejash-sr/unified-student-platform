# Deployment Guide

## Backend Deployment Options

### Option 1: Railway (Recommended - Easiest)

**Advantages:**
- One-click deployment
- Automatic SSL
- Environment variables UI
- PostgreSQL integrated
- Free tier: 500 hours/month

**Steps:**
1. Push to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Select `unified-student-platform`
6. Railway auto-detects `requirements.txt`
7. Add environment variables via UI:
   - `DATABASE_URL` (Railway creates PostgreSQL)
   - `GROQ_API_KEY`
   - `SENDGRID_API_KEY`
   - `SECRET_KEY` (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
8. Deploy

**That's it!** Your API is live at `https://unified-student-platform-production.up.railway.app`

### Option 2: AWS EC2

**Setup:**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance.com

# Install dependencies
sudo apt update && sudo apt install python3.11 python3-pip postgresql

# Clone repo
git clone https://github.com/tejash-sr/unified-student-platform.git
cd unified-student-platform/backend

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup .env file
nano .env
# Add all environment variables

# Run with Gunicorn
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Setup systemd service
sudo nano /etc/systemd/system/unified-student-platform.service
```

### Option 3: Docker

```bash
# From project root
docker build -t unified-student-platform .
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e GROQ_API_KEY="..." \
  unified-student-platform
```

## Frontend Deployment Options

### Option 1: Vercel (Recommended)

**Advantages:**
- Optimized for Next.js
- Automatic deployments on push
- Edge functions
- Analytics built-in
- Free tier: Unlimited

**Steps:**
1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Select your GitHub repo
4. Select `./frontend` as root directory
5. Add environment variables:
   - `NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api`
6. Click Deploy

**Done!** Frontend is live at `https://unified-student-platform.vercel.app`

### Option 2: Netlify

```bash
cd frontend
npm run build
# Drag and drop `out/` folder to Netlify
```

## Mobile Deployment

### iOS (App Store)

1. Install Xcode
2. Create Apple Developer account
3. Generate certificate
4. Run: `expo build:ios --release-channel production`
5. Upload to App Store Connect

### Android (Google Play)

1. Generate keystore: `expo build:android --keystore-path ./app.jks`
2. Run: `expo build:android --release-channel production`
3. Upload to Google Play Console

## Database Setup

### PostgreSQL (Local Development)

```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt install postgresql

# Create database
createdb student_platform

# Set connection string in .env
DATABASE_URL="postgresql://user:password@localhost:5432/student_platform"

# Run migrations/seed
cd backend
python seed_database.py
```

### PostgreSQL (Railway)

Railway creates PostgreSQL automatically. Copy connection string from Dashboard:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### PostgreSQL (AWS RDS)

1. Create RDS instance
2. Configure security group
3. Get endpoint: `your-db.xxxx.us-east-1.rds.amazonaws.com`
4. Set `DATABASE_URL`:
   ```
   postgresql://admin:password@your-db.xxxx.us-east-1.rds.amazonaws.com:5432/student_platform
   ```

## Environment Variables Checklist

### Backend (`.env`)
- `DATABASE_URL` ✓
- `GROQ_API_KEY` ✓
- `SENDGRID_API_KEY` ✓
- `SECRET_KEY` ✓
- `ENVIRONMENT=production` ✓
- `DEBUG=false` ✓

### Frontend (`.env.local`)
- `NEXT_PUBLIC_API_URL` ✓

### Mobile (`.env`)
- `API_URL` ✓

## Production Checklist

- [ ] Database backed up
- [ ] Environment variables set (no secrets in code)
- [ ] SSL certificates installed
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Monitoring/logging configured
- [ ] Health checks passing
- [ ] Database indexes created
- [ ] Error tracking (Sentry) configured
- [ ] Analytics configured

## Post-Deployment Testing

```bash
# Health check
curl https://your-backend.com/health

# API docs
https://your-backend.com/api/docs

# Test signup
curl -X POST https://your-backend.com/api/users/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123","first_name":"Test"}'

# Test growth engine
curl -X POST https://your-backend.com/api/growth/analyze \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Monitoring

### Sentry (Error Tracking)

```python
import sentry_sdk
sentry_sdk.init("your-sentry-dsn", traces_sample_rate=1.0)
```

### Datadog (Performance)

```python
from datadog import initialize, api
initialize(api_key="your-key", app_key="your-app-key")
```

## Scaling Tips

1. **Database:**
   - Add read replicas for reporting
   - Archive old logs
   - Increase connection pool

2. **Backend:**
   - Use load balancer (Railway does this)
   - Cache frequently accessed data (Redis)
   - Queue long tasks (Celery + RabbitMQ)

3. **Frontend:**
   - Enable CDN caching
   - Optimize images
   - Code splitting enabled by default in Next.js

4. **Mobile:**
   - Implement service worker for offline
   - Lazy load screens
   - Optimize bundle size

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker logs container-id

# Verify .env file exists
cat .env

# Check database connection
psql $DATABASE_URL -c "SELECT 1"
```

### Frontend not connecting to API
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS is enabled on backend
- Check browser console for errors

### Database connection timeout
- Verify connection string
- Check security group/firewall rules
- Ensure database is running
- Check connection pool limits

---

**Happy deploying!** 🚀
