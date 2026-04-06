# VISIONZ Backend

FastAPI-based backend for video defect detection system using YOLO v8.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
```

3. Run locally:
```bash
python run.py
```

Or with uvicorn:
```bash
uvicorn app.main:app --reload
```

## Project Structure

- `app/` - Main FastAPI application
  - `main.py` - Entry point
  - `config.py` - Configuration
  - `database.py` - Database setup
  - `security.py` - Authentication/security
  - `routes/` - API endpoints
  - `services/` - Business logic
  - `middleware/` - Request/response middleware
  - `models/` - Pydantic schemas
- `index.py` - Vercel serverless function entry point
- `requirements.txt` - Python dependencies

## API Endpoints

- `/api/auth/` - Authentication routes
- `/api/users/` - User management
- `/api/detections/` - Video defect detection
- `/api/video/` - Video processing
- `/api/reports/` - Analytics and reports
- `/api/analytics/` - System analytics
- `/api/ai/` - AI service routes

## Environment Variables

See `.env.example` for all required variables.
