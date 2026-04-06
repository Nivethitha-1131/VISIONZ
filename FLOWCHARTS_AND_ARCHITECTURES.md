# VISIONZ QC System — Flowcharts & Architecture

## System Overview

```
Frontend (3000)
    ↓ HTTP + JWT
Backend (8000)
    ↓
Video Service
    ↓
YOLO Model
    ↓
AI Analysis (Claude/Llama/Local)
    ↓
Database (SQLite)
    ↓
Dashboard Display
```

---

## Video Processing Pipeline

```
Upload Video
    ↓
Extract Frames (OpenCV)
    ↓
FOR EACH FRAME:
    - YOLO Detection (50-100ms)
    - Classification (6 classes)
    - Store Results
    ↓
Aggregate Statistics
    ↓
AI Analysis
    ↓
Generate Report
    ↓
Display on Dashboard
```

---

## Data Flow

**Input:** MP4 Video (2 min)  
**↓**  
**Processing:** 3,600 frames extracted & analyzed  
**↓**  
**Output:** Detection results + AI analysis  
**↓**  
**Storage:** SQLite database  
**↓**  
**Display:** Web dashboard  

---

## Database Schema

```
Users
├── id (PK)
├── username
├── password_hash
└── role (admin/supervisor/inspector)

Videos
├── id (PK)
├── filename
├── upload_user_id (FK)
├── status (processing/completed)
└── uploaded_at

Detections
├── id (PK)
├── video_id (FK)
├── frame_number
├── defect_class
├── confidence
└── bbox_coords

Reports
├── id (PK)
├── video_id (FK)
├── verdict (PASS/WARNING/CRITICAL)
├── analysis_text
└── created_at
```

---

## API Architecture

```
Authentication Flow:
POST /api/auth/login
    ↓
Validate Credentials
    ↓
Return JWT Token
    ↓
Include in Headers for Protected Endpoints

Video Processing Flow:
POST /api/video/process
    ↓
Validate & Save
    ↓
Extract Frames
    ↓
Run YOLO Detection
    ↓
Return Results
```

---

## Component Integration

```
Frontend Dashboard
    ↓ (JS API calls)
FastAPI Routes
    ↓ (route handlers)
Services Layer
    ├── Video Processor (OpenCV)
    ├── YOLO Service (Detection)
    ├── Llama Service (Analysis)
    └── Local Analyzer (Fallback)
    ↓
Database Layer (SQLite)
    ↓
External APIs (Claude/Ollama)
```

---

## Security Architecture

```
Request Comes In
    ↓
CORS Validation
    ↓
Rate Limiting Check
    ↓
JWT Token Validation
    ↓
Extract User Context
    ↓
Process Request
    ↓
Return Response
```

---

**Document Version:** 1.0 | Date: April 2026
