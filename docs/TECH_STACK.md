# VISIONZ QC System — Tools & Tech Stack

**Version:** 3.0.0  
**Last Updated:** April 2026  
**Project Type:** AI-Powered FMCG Quality Control Platform

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Backend Stack](#backend-stack)
3. [Frontend Stack](#frontend-stack)
4. [AI/ML Stack](#aiml-stack)
5. [Database & Storage](#database--storage)
6. [DevOps & Deployment](#devops--deployment)
7. [Development Tools](#development-tools)
8. [Third-Party Services](#third-party-services)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    VISIONZ Architecture                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐         ┌──────────────────────┐      │
│  │   Frontend   │         │   Backend (FastAPI)  │      │
│  │  HTML/JS/CSS │◄────────┤   Python 3.12        │      │
│  │              │         │   Uvicorn Server     │      │
│  │ - Dashboard  │         │   Port: 8000         │      │
│  │ - Analytics  │         │   REST API           │      │
│  │ - Reports    │         └──────────────────────┘      │
│  └──────────────┘                   │                    │
│                                     │                    │
│                    ┌────────────────┼────────────────┐   │
│                    ▼                ▼                ▼    │
│            ┌──────────────┐  ┌──────────────┐  ┌─────┐  │
│            │    SQLite    │  │  YOLOv8 ML   │  │ API │  │
│            │   Database   │  │  (Detection) │  │     │  │
│            │  (Dev/Test)  │  │   CPU/GPU    │  └─────┘  │
│            └──────────────┘  └──────────────┘            │
│                    │                │                     │
│            ┌───────▼─────────┬──────▼──────────┐          │
│            │                 │                  │          │
│            ▼                 ▼                  ▼          │
│        ┌─────────┐   ┌──────────────┐    ┌──────────┐   │
│        │ Uploads │   │ Claude API   │    │ Llama    │   │
│        │ Folder  │   │ (Claude)     │    │ (Ollama) │   │
│        │         │   │ Optional     │    │ Fallback │   │
│        └─────────┘   └──────────────┘    └──────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Backend Stack

### Core Framework
| Tool | Version | Purpose |
|---|---|---|
| **FastAPI** | 0.111.0+ | High-performance async web framework for REST API |
| **Uvicorn** | 0.29.0+ | ASGI server (production-grade application server) |
| **Pydantic** | 2.7.1+ | Data validation, serialization, type hints |
| **Python** | 3.12 | Base language |

### HTTP & Networking
| Tool | Version | Purpose |
|---|---|---|
| **python-multipart** | 0.0.9 | Multipart form data parsing (file uploads) |
| **requests** | 2.31.0 | HTTP client (external API calls) |
| **urllib3** | Built-in | Low-level HTTP client |

### Security & Authentication
| Tool | Version | Purpose |
|---|---|---|
| **bcrypt** | 4.1.2+ | Password hashing (secure storage) |
| **PyJWT** | 2.12.1+ | JWT token generation/validation |
| **python-dotenv** | 1.0.0+ | Environment variable management |

### Rate Limiting & Performance
| Tool | Version | Purpose |
|---|---|---|
| **slowapi** | 0.1.9 | Rate limiting middleware (prevent abuse) |

### File Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Settings management
│   ├── database.py          # DB initialization
│   ├── errors.py            # Custom error handlers
│   ├── security.py          # JWT & auth logic
│   ├── middleware/          # Request/response middleware
│   │   ├── auth_middleware.py
│   │   ├── rate_limit.py
│   │   └── security.py
│   ├── models/              # Data models
│   │   └── schemas.py       # Pydantic schemas
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── detections.py
│   │   ├── analytics.py
│   │   ├── reports.py
│   │   ├── video.py
│   │   └── ai.py
│   ├── services/            # Business logic
│   │   ├── llama_service.py
│   │   ├── yolo_service.py
│   │   ├── video_processor.py
│   │   └── session_manager.py
│   ├── database/            # SQLite data
│   ├── logs/                # Application logs
│   └── uploads/             # User uploaded videos
│
├── requirements.txt         # Python dependencies
├── run.py                   # Server launcher
└── .env                     # Environment configuration
```

---

## Frontend Stack

### Tech Stack
| Technology | Purpose | Files |
|---|---|---|
| **HTML5** | Structure & markup | *.html |
| **JavaScript (Vanilla)** | Client-side interactions | js/*.js |
| **CSS3** | Styling & responsive design | *.html (inline) |
| **Fetch API** | Backend API communication | js/api.js |

### Frontend Pages
| Page | Purpose |
|---|---|
| **index.html** | Main dashboard (real-time video analysis) |
| **analytics.html** | Defect trends, charts, statistics |
| **reports.html** | QC report generation & export |
| **login.html** | User authentication |
| **profile.html** | User settings & preferences |
| **landing.html** | Public info page |

### Frontend Components
```
frontend/
├── index.html           # Main app dashboard
├── login.html           # Authentication page
├── profile.html         # User profile mgmt
├── analytics.html       # Analytics dashboard
├── reports.html         # Report viewer
├── landing.html         # Landing page
├── js/
│   ├── api.js          # Backend API client
│   └── navbar.js       # Navigation logic
└── data/
    └── users.json      # User data (demo)
```

### API Integration
```javascript
// js/api.js provides methods:
- POST /api/video/process       // Upload video for analysis
- GET /api/detections/get       // Retrieve defect data
- POST /api/ai/analyze          // Get AI analysis
- GET /api/analytics/report     // Get analytics data
- POST /api/auth/login          // User authentication
```

---

## AI/ML Stack

### Deep Learning & Computer Vision
| Tool | Version | Purpose |
|---|---|---|
| **PyTorch** | 2.2.0+ | Deep learning framework (backend for YOLO) |
| **TorchVision** | 0.17.0+ | Computer vision utilities |
| **OpenCV (cv2)** | 4.8.1.78+ | Video processing, frame extraction, image manipulation |
| **NumPy** | 1.24.3+ | Numerical computing, array operations |
| **Pillow (PIL)** | 10.0.0+ | Image loading and processing |

### Object Detection
| Tool | Version | Purpose |
|---|---|---|
| **Ultralytics YOLOv8** | 8.2.0+ | Real-time defect detection model |
| **YOLOv8s (Small)** | Pre-trained | Lightweight model (80M parameters, CPU-capable) |

### Language Model Integration
| Tool | Version | Purpose |
|---|---|---|
| **Ollama** | SDK | Local LLM inference (serves Llama2/other models) |
| **Llama2** | Via Ollama | Open-source LLM for QC analysis (optional) |
| **Claude API** | Anthropic SDK | Premium AI analysis (optional, requires API key) |

### AI Service Flow
```
Video Upload
    │
    ▼
Frame Extraction (OpenCV)
    │
    ▼
YOLOv8 Detection (50-100 FPS on CPU)
    │
    ├─→ Per-frame defect bounding boxes
    ├─→ Defect confidence scores
    └─→ Defect classifications
    │
    ▼
Analysis Generation
    │
    ├─→ Option 1: Claude API (premium insights)
    ├─→ Option 2: Llama via Ollama (local)
    └─→ Option 3: Built-in Local Analyzer (always available)
    │
    ▼
QC Report Generation
    └─→ JSON response to frontend
```

---

## Database & Storage

### Current Database
| Component | Technology | Purpose |
|---|---|---|
| **Primary DB** | SQLite | Development/testing (file-based, zero-config) |
| **Production DB** | PostgreSQL (future) | Scalable, multi-user |
| **ORM** | SQLAlchemy (via Pydantic) | Database abstraction layer |

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR,
    email VARCHAR UNIQUE,
    password_hash VARCHAR,
    role ENUM('admin', 'supervisor', 'inspector'),
    created_at TIMESTAMP
);

-- Detections table
CREATE TABLE detections (
    id INT PRIMARY KEY,
    video_id INT,
    frame_number INT,
    defect_class VARCHAR,
    confidence FLOAT,
    bounding_box JSON,
    timestamp TIMESTAMP
);

-- Reports table
CREATE TABLE reports (
    id INT PRIMARY KEY,
    video_id INT,
    defect_count INT,
    defect_rate FLOAT,
    verdict ENUM('PASS', 'WARNING', 'CRITICAL'),
    analysis TEXT,
    generated_by INT,
    created_at TIMESTAMP
);

-- Videos table
CREATE TABLE videos (
    id INT PRIMARY KEY,
    filename VARCHAR,
    upload_path VARCHAR,
    duration FLOAT,
    frame_count INT,
    processed_at TIMESTAMP,
    status ENUM('pending', 'processing', 'completed')
);
```

### File Storage
| Location | Purpose |
|---|---|
| **./uploads/** | User-uploaded video files |
| **./database/** | SQLite database files |
| **./logs/** | Application logs |

---

## DevOps & Deployment

### Current Environment
| Component | Status | Details |
|---|---|---|
| **Containerization** | Planned | Docker setup (not yet implemented) |
| **Orchestration** | Planned | Kubernetes for scaling (future) |
| **CI/CD** | Planned | GitHub Actions (future) |
| **Monitoring** | Basic | Console logs only |

### Environment Management
```bash
# Virtual Environment
Python venv (.venv/)

# Environment Variables (.env)
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
DATABASE_URL=sqlite:///./database.db
CORS_ORIGINS=http://localhost:3000
ANTHROPIC_API_KEY=<your-key>
YOLO_DEVICE=cpu
```

### Deployment Architecture (Future)
```
┌──────────────────────────────────────────┐
│      AWS / On-Premise Server             │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────────┐ │
│  │   Docker Container                 │ │
│  ├────────────────────────────────────┤ │
│  │ FastAPI + Uvicorn                  │ │
│  │ YOLOv8 Detection Engine            │ │
│  │ SQLite / PostgreSQL                │ │
│  └────────────────────────────────────┘ │
│           │                              │
│           ▼                              │
│  ┌────────────────────────────────────┐ │
│  │  Kubernetes Pod (scaling)          │ │
│  │  - Load Balancer (Nginx/HAProxy)   │ │
│  │  - Multiple replicas               │ │
│  └────────────────────────────────────┘ │
│                                          │
└──────────────────────────────────────────┘
```

---

## Development Tools

### Code Editors & IDEs
| Tool | Purpose |
|---|---|
| **VS Code** | Main IDE with Python extension |
| **GitHub Copilot** | AI-assisted code generation |

### Python Development
| Tool | Purpose | Command |
|---|---|---|
| **pip** | Package manager | `pip install -r requirements.txt` |
| **venv** | Virtual environment | `.venv\Scripts\activate` |
| **pytest** | Unit testing (optional) | `pytest tests/` |
| **black** | Code formatting (optional) | `black app/` |
| **pylint** | Linting (optional) | `pylint app/` |

### API Testing & Documentation
| Tool | Purpose | URL |
|---|---|---|
| **Swagger UI** | Interactive API docs | `http://localhost:8000/docs` |
| **ReDoc** | Alternative API docs | `http://localhost:8000/redoc` |
| **Postman** | API testing client | Desktop app |

### Version Control
| Tool | Purpose |
|---|---|
| **Git** | Source code management |
| **GitHub** | Remote repository (optional) |

### Performance & Debugging
| Tool | Purpose |
|---|---|
| **Python Debugger (pdb)** | Step-through debugging |
| **Uvicorn logging** | Server request logs |
| **FastAPI middleware** | Request/response inspection |

---

## Third-Party Services

### AI & Analysis APIs (Optional)
| Service | Purpose | Status | Cost |
|---|---|---|---|
| **Anthropic Claude API** | Premium QC analysis | Optional | $0.003/msg |
| **Ollama (Local)** | LLM inference locally | Optional | Free |

### Hosting & Infrastructure (Future)
| Service | Purpose | Status |
|---|---|---|
| **AWS EC2** | Server hosting | Planned |
| **AWS S3** | Video/data storage | Planned |
| **AWS RDS** | Managed PostgreSQL | Planned |
| **Docker Hub** | Container registry | Planned |

---

## Technology Summary Table

### By Category
```
┌─────────────────────────────────────────────────────────────────┐
│                     TECHNOLOGY SUMMARY                          │
├─────────────────┬──────────────┬──────────┬─────────────────────┤
│ Category        │ Technology   │ Version  │ Purpose             │
├─────────────────┼──────────────┼──────────┼─────────────────────┤
│ Language        │ Python       │ 3.12     │ Core development    │
│ Web Framework   │ FastAPI      │ 0.111.0+ │ REST API            │
│ ASGI Server     │ Uvicorn      │ 0.29.0+  │ App server          │
│ ML Framework    │ PyTorch      │ 2.2.0+   │ Deep learning       │
│ Vision Model    │ YOLOv8       │ 8.2.0+   │ Object detection    │
│ Image Proc      │ OpenCV       │ 4.8.1.78 │ Video processing    │
│ Database        │ SQLite       │ Latest   │ Data persistence    │
│ Auth            │ JWT + bcrypt │ Latest   │ Security            │
│ Rate Limiting   │ slowapi      │ 0.1.9    │ API protection      │
│ Frontend        │ HTML5/JS     │ ES2020   │ User interface      │
│ LLM (Optional)  │ Claude/Llama │ Latest   │ AI analysis         │
└─────────────────┴──────────────┴──────────┴─────────────────────┘
```

---

## System Requirements

### Minimum (Development)
- **CPU:** 2+ cores
- **RAM:** 8GB+
- **Storage:** 10GB+ (for models & videos)
- **GPU:** Optional (CPU mode supported)

### Recommended (Production)
- **CPU:** 8+ cores (Intel Xeon or equivalent)
- **RAM:** 32GB+
- **Storage:** 500GB+ (NVMe SSD recommended)
- **GPU:** NVIDIA (CUDA 11.8+) for real-time processing
- **OS:** Linux (Ubuntu 22.04 LTS) or Windows Server

---

## Quick Start Commands

```bash
# Setup
python -m venv .venv
.\.venv\Scripts\activate          # Windows
source .venv/bin/activate         # Linux/Mac

# Install dependencies
cd visionz_fixed/backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run backend
python run.py

# Run frontend (separate terminal)
cd ../frontend
python -m http.server 3000

# Access
# Backend API:  http://localhost:8000
# Frontend UI:  http://localhost:3000
# API Docs:     http://localhost:8000/docs
```

---

## Dependencies Graph

```
App Requirements
│
├─ Web Stack
│  ├─ fastapi (async HTTP framework)
│  ├─ uvicorn (ASGI server)
│  ├─ pydantic (data validation)
│  ├─ python-multipart (form parsing)
│  └─ slowapi (rate limiting)
│
├─ Security Stack
│  ├─ bcrypt (password hashing)
│  ├─ PyJWT (token handling)
│  └─ python-dotenv (env config)
│
├─ AI/Vision Stack
│  ├─ torch (PyTorch deep learning)
│  ├─ torchvision (CV utilities)
│  ├─ ultralytics (YOLOv8)
│  ├─ opencv-python (video processing)
│  ├─ numpy (numerical ops)
│  └─ pillow (image handling)
│
├─ LLM Stack (Optional)
│  ├─ ollama (local LLM SDK)
│  └─ requests (HTTP for APIs)
│
└─ Data Stack
   └─ SQLite (default DB)
```

---

## Notes & Future Upgrades

### Current Limitations
- SQLite suitable for single-machine deployments only
- No GPU acceleration (works on CPU)
- No distributed processing
- Limited horizontal scaling

### Recommended Upgrades (Phase 2)
1. **PostgreSQL** for multi-user production
2. **Redis** for caching & session management
3. **Celery** for async task processing
4. **Docker** for containerization
5. **Kubernetes** for orchestration
6. **Prometheus + Grafana** for monitoring
7. **ELK Stack** for log aggregation

---

**Document Version:** 1.0  
**Last Updated:** April 2026  
**Maintainer:** VISIONZ Development Team
