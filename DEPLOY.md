# Render.com Deployment Guide

## Quick Deploy Instructions

### 1. Render Dashboard Settings:
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Root Directory**: `backend`

### 2. Environment Variables:
```
JWT_SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key
LLM_PROVIDER=groq
FLASK_ENV=production
DATABASE_URL=sqlite:///instance/journal.db
PYTHON_VERSION=3.11.9
```

### 3. Manual Steps if Auto-deploy Fails:
1. Use Python 3.11 (not 3.13)
2. Install requirements one by one if needed
3. Check logs for specific package conflicts

### 4. Test Endpoints After Deploy:
- GET /api/entries
- POST /api/ai/search
- GET /api/ai/search/test
