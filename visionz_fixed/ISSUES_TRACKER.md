# VISIONZ - ISSUES & FIXES TRACKER

## CRITICAL ISSUES (Must Fix Before Production)

### ❌ Issue #1: No Environment Configuration System
**Severity:** CRITICAL (Blocks Deployment)  
**Component:** System-Wide  
**Status:** 🔴 NOT STARTED

**Description:**
Project has no .env or configuration system. All settings are hardcoded or have fallback defaults. Makes it impossible to:
- Change API port without code edit
- Set production API keys securely
- Deploy to different environments
- Store secrets safely
- Change database location

**Current State:**
```python
# Hardcoded defaults scattered throughout codebase:
CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "visionz.db")
```

**Required Files:**
- [ ] `.env.example` (template)
- [ ] `.env` (actual values)
- [ ] `config.py` (centralized configuration)

**Implementation Checklist:**
- [ ] Add `python-dotenv` to requirements.txt
- [ ] Create `.env.example` with all variables
- [ ] Create `.env` (gitignored)
- [ ] Create `app/config.py` with Settings class (Pydantic)
- [ ] Update `main.py` to load config on startup
- [ ] Add config validation with helpful error messages
- [ ] Remove hardcoded values from all modules
- [ ] Update documentation with setup instructions

**Time Estimate:** 2 hours  
**Difficulty:** Easy

**Tests:**
```bash
# Test 1: Run without .env (should fail obviously or use fallbacks)
# Test 2: Run with .env (should load values)
# Test 3: Change .env values (should apply without restart... or with restart if needed)
# Test 4: Invalid .env (should show helpful error message)
```

---

### ❌ Issue #2: YOLOv6 Video Detection Pipeline Incomplete
**Severity:** CRITICAL (Main Feature)  
**Component:** `backend/app/services/yolo_service.py`  
**File/Line:** yolo_service.py, method `detect_video()`  
**Status:** 🔴 50% WRITTEN, NOT FUNCTIONAL

**Description:**
YOLOv6 video detection endpoint exists but the core video processing loop is completely missing. Users can call the endpoint but get incomplete/empty results.

**Current Implementation:**
```python
def detect_video(self, video_path, max_frames=None, skip_frames=1):
    # Validates file exists ✅
    # Returns early if unavailable ✅
    # ❌ COMPLETELY MISSING: Everything else
```

**What Needs Implementation:**
1. [ ] Video codec reading with `cv2.VideoCapture(video_path)`
2. [ ] Frame extraction loop with `cap.read()`
3. [ ] Use `skip_frames` parameter to skip N frames between processing
4. [ ] Enforce `max_frames` limit to prevent infinite processing
5. [ ] Call `detect_frame()` for each frame
6. [ ] Aggregate detections across all frames
7. [ ] Return formatted results with frame count, detection count, etc.
8. [ ] Handle corrupted/unplayable videos with error response
9. [ ] Add progress tracking/logging
10. [ ] Memory management for long videos (don't load all frames at once)

**Pseudo-code for Implementation:**
```python
def detect_video(self, video_path, max_frames=None, skip_frames=1):
    # 1. Open video file
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # 2. Process frames
    frame_count = 0
    detections_all = []
    
    while cap.isOpened() and (max_frames is None or frame_count < max_frames):
        ret, frame = cap.read()
        if not ret: break
        
        # Skip frames if requested
        if frame_count % skip_frames != 0:
            frame_count += 1
            continue
        
        # Run detection
        annotated, detections = self.detect_frame(frame)
        detections_all.extend(detections)
        frame_count += 1
    
    cap.release()
    
    # 3. Return results
    return {
        "success": True,
        "video_path": video_path,
        "total_frames": total_frames,
        "frames_processed": frame_count,
        "detections_found": len(detections_all),
        "detections": [d.to_dict() for d in detections_all]
    }
```

**Time Estimate:** 8-10 hours  
**Difficulty:** Medium

**Tests:**
```bash
# Test 1: Small 5-frame video
curl -X POST http://localhost:8000/api/ai/detect/video?video_path=uploads/test.mp4

# Test 2: Use skip_frames (should skip frames)
curl -X POST http://localhost:8000/api/ai/detect/video?video_path=uploads/test.mp4&skip_frames=5

# Test 3: Use max_frames (should stop after N frames)
curl -X POST http://localhost:8000/api/ai/detect/video?video_path=uploads/test.mp4&max_frames=10

# Test 4: Non-existent file (should error gracefully)
curl -X POST http://localhost:8000/api/ai/detect/video?video_path=uploads/nonexistent.mp4
```

---

### ❌ Issue #3: Detection Endpoint Silent Failures
**Severity:** CRITICAL (Data Loss)  
**Component:** `backend/app/routes/detections.py`  
**File/Line:** detections.py, method `save_detection()`, lines 24-35  
**Status:** 🔴 NEEDS FIX

**Current Code:**
```python
try:
    cur.execute("""INSERT INTO detections...""")
    detection_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": detection_id, "message": "Detection saved."}
except Exception as e:
    conn.close()
    return {"id": None, "message": "Saved locally only."}  # ❌ HIDES ERROR
```

**Problem:**
- Returns success response even when database insert fails
- Frontend can't tell if save succeeded or failed
- Data is silently lost
- No error logging for debugging

**Fix Required:**
```python
try:
    cur.execute("""INSERT INTO detections...""")
    detection_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": detection_id, "message": "Detection saved."}
except sqlite3.IntegrityError as e:
    conn.close()
    print(f"[Detections] Integrity error: {e}")
    raise HTTPException(status_code=400, detail=f"Invalid detection data: {str(e)}")
except sqlite3.OperationalError as e:
    conn.close()
    print(f"[Detections] Database error: {e}")
    raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
except Exception as e:
    conn.close()
    print(f"[Detections] Unexpected error: {e}")
    raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
```

**Time Estimate:** 1 hour  
**Difficulty:** Easy

---

### ❌ Issue #4: Weak Password Security (SHA256 No Salt)
**Severity:** CRITICAL (Security)  
**Component:** `backend/app/database.py`  
**File/Line:** database.py, lines 23-24  
**Status:** 🔴 NEEDS FIX

**Current Code:**
```python
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
```

**Problems:**
1. SHA256 was designed for checksums, not password hashing
2. No salt means rainbow tables can crack it
3. No key stretching (should use PBKDF2/bcrypt)
4. All passwords vulnerable to attack

**Fix Required:**
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash.encode())
```

**Update Dependencies:**
```
# requirements.txt - add:
bcrypt==4.1.2
```

**Files to Update:**
- [ ] `backend/requirements.txt` - Add bcrypt
- [ ] `backend/app/database.py` - Replace hash_password()
- [ ] `backend/app/routes/auth.py` - Update verification logic

**Migration:**
- [ ] Existing hashes will no longer work
- [ ] Ask users to reset password or manually update
- [ ] Keep old hash_password for verification during transition

**Time Estimate:** 2 hours (including testing)  
**Difficulty:** Easy

---

### ❌ Issue #5: No Rate Limiting
**Severity:** CRITICAL (Security/Abuse)  
**Component:** System-Wide  
**Status:** 🔴 NOT STARTED

**Description:**
API has no rate limiting. Same user can make unlimited requests:
- Brute force login attempts
- Hammer video upload (disk full)
- DDoS-like behavior
- Expensive API calls (Claude)

**Implementation Checklist:**
- [ ] Add `slowapi==0.1.9` to requirements.txt
- [ ] Import: `from slowapi import Limiter` and `from slowapi.util import get_remote_address`
- [ ] In main.py:
  ```python
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
  ```
- [ ] Apply limits to routes:
  ```python
  @router.post("/login")
  @limiter.limit("5/minute")  # 5 attempts per minute
  def login(request: Request, body: LoginRequest):
  ```
- [ ] Different limits for different endpoints:
  - Login: 5/minute
  - Upload: 10/hour per user
  - Analysis: 20/hour per user (expensive)
  - General API: 100/minute per user

**Time Estimate:** 3-4 hours (including configuration)  
**Difficulty:** Medium

---

## HIGH PRIORITY ISSUES

### 🟡 Issue #6: CORS Allows All Origins
**Severity:** HIGH (Security)  
**Component:** `backend/app/main.py`  
**File/Line:** main.py, lines 33-39  
**Status:** 🟡 NEEDS FIX

**Current Code:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ ALLOWS EVERYTHING
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Problem:**
- Any website can make requests to your API
- Can bypass frontend logic
- Enables CSRF attacks
- Not suitable for production

**Fix:**
```python
# From environment or hardcoded for known domains
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5500",
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Time Estimate:** 1 hour  
**Difficulty:** Easy

---

### 🟡 Issue #7: Video Metadata Not Extracted
**Severity:** HIGH (Feature)  
**Component:** `backend/app/routes/video.py`  
**File/Line:** video.py, `upload_video()` method  
**Status:** 🟡 IMPORTANT

**Current State:**
- Video uploaded successfully ✅
- file_size stored ✅
- duration = NULL ❌
- resolution = NULL ❌
- fps = NULL ❌

**Implementation:**
```python
import cv2

# After saving video file:
cap = cv2.VideoCapture(save_path)
if cap.isOpened():
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    resolution = f"{width}x{height}"
    cap.release()
    
    # Update database:
    cur.execute("""UPDATE videos SET duration=?, resolution=? WHERE id=?""",
                (duration, resolution, video_id))
```

**Time Estimate:** 3 hours  
**Difficulty:** Easy

---

### 🟡 Issue #8: No Session Timeout
**Severity:** HIGH (Security)  
**Component:** `backend/app/database.py` and `backend/app/middleware/auth_middleware.py`  
**Status:** 🟡 NEEDS IMPLEMENTATION

**Current State:**
- Sessions never expire
- Lost phone/laptop = permanent access for finder
- Employee leaves = account still active forever

**Fix:**
```sql
-- Add to sessions table:
expire_at TIMESTAMP DEFAULT (datetime('now', '+24 hours'))

-- Check in middleware:
SELECT * FROM sessions WHERE token=? AND is_active=1 AND datetime('now') < expire_at
```

**Time Estimate:** 2 hours  
**Difficulty:** Easy

---

### 🟡 Issue #9: Activity Logging Empty
**Severity:** HIGH (Usability)  
**Component:** `frontend/profile.html` and backend  
**Status:** 🟡 NOT STARTED

**Current State:**
- UI shows "Logged in to dashboard" etc.
- All hardcoded/placeholder

**Required Implementation:**
1. [ ] Create audit_log table in database
2. [ ] Log user actions (login, upload, analysis, etc.)
3. [ ] Backend endpoint GET /api/users/activity
4. [ ] Frontend fetch and display

**Time Estimate:** 4 hours  
**Difficulty:** Medium

---

## MEDIUM PRIORITY ISSUES

### 🟠 Issue #10: Analytics Filter Logic Missing
**Severity:** MEDIUM (Usability)  
**Component:** `frontend/analytics.html`  
**Status:** 🟠 NOT STARTED

**Current State:**
- Filter buttons visible
- setFilter() function undefined
- No filtering actually happens

**Implementation:**
- [ ] Implement setFilter() function
- [ ] Add filter state to page
- [ ] Send filter params to API
- [ ] Update chart data based on filter

**Time Estimate:** 3 hours  
**Difficulty:** Easy

---

### 🟠 Issue #11: Frontend Initial Load States
**Severity:** MEDIUM (UX)  
**Components:** `reports.html`, `analytics.html`  
**Status:** 🟠 INCONSISTENT

**Issues:**
- reports.html shows "—" for pass rate on load
- analytics.html empty charts on load
- No loading skeleton screens
- Users confused during initial fetch

**Fix:** Add loading states before data fetch

**Time Estimate:** 2-3 hours  
**Difficulty:** Easy

---

### 🟠 Issue #12: Particle Animation Missing
**Severity:** LOW (Polish)  
**Component:** `frontend/index.html`  
**Status:** 🔴 NOT IMPLEMENTED

**Current State:**
```html
<!-- index.html references canvas but no JS file -->
<canvas id="canvas"></canvas>
<!-- Need js/particles.js file -->
```

**Implementation:**
- [ ] Create `frontend/js/particles.js`
- [ ] Implement particle animation using canvas
- [ ] Reference in index.html

**Time Estimate:** 2 hours  
**Difficulty:** Easy-Medium

---

### 🟠 Issue #13: CSV Export Missing
**Severity:** MEDIUM (Feature)  
**Component:** `frontend/reports.html`  
**Status:** 🟠 NOT STARTED

**Current:** Only PDF export  
**Needed:** CSV export for data analysis

**Implementation:** Add CSV generation endpoint

**Time Estimate:** 2 hours  
**Difficulty:** Easy

---

## TRACKING & UPDATES

### How to Use This Document

1. **Assign Issues** - Assign each issue to a team member with estimated hours
2. **Create Tasks** - Break each issue into subtasks
3. **Track Progress** - Mark [ ] as [x] as you complete items
4. **Update Status** - Change 🔴 → 🟡 → 🟢 as progress happens
5. **Document Changes** - Add notes about what was fixed

### Status Legend
- 🔴 NOT STARTED
- 🟡 IN PROGRESS  
- 🟢 COMPLETE/TESTING
- ✅ VERIFIED/CLOSED

### Time Tracking

**Total Critical Issues:** 5 issues × average 5 hours = 25 hours
**Total High Priority:** 4 issues × average 3 hours = 12 hours
**Total Medium Priority:** 4 issues × average 2.5 hours = 10 hours

**Total Effort:** ~47 hours ≈ 1 week full-time with one developer

### Recommended Sprint Schedule

**Sprint 1 (Critical Only):** 
- Issue #1: Configuration (2h)
- Issue #2: YOLOv6 (8h)
- Issue #3: Detection errors (1h)
- Issue #4: Passwords (2h)
- Issue #5: Rate limiting (4h)
- **Subtotal: 17 hours (2-3 days)**

**Sprint 2 (High Priority):**
- Issue #6: CORS (1h)
- Issue #7: Video metadata (3h)
- Issue #8: Session timeout (2h)
- Issue #9: Activity logging (4h)
- **Subtotal: 10 hours (1.5 days)**

**Sprint 3 (Polish):**
- Issue #10: Filter logic (3h)
- Issue #11: Load states (2h)
- Issue #12: Particles (2h)
- Issue #13: CSV export (2h)
- **Subtotal: 9 hours (1 day)**

---

## NOTES & COMMENTS

### Team Communication

**When Assigning:**
- "Issue #2 (YOLOv6) is critical - blocks main feature"
- "Start with Issue #1 (Config) - unblocks everything else"
- "Issue #4 (Passwords) must be done before any user signup"

**When Prioritizing:**
- Do Issues #1, #3, #4, #6 first (security/stability)
- Do Issue #2 next (main feature)
- Do the rest after core is solid

**Before Release:**
- All 🔴 RED items must be 🟢 GREEN
- All 🟡 YELLOW items should be 🟢 GREEN
- Testing on all issues completed

---

**Document Version:** 1.0  
**Last Updated:** March 29, 2026  
**Next Review:** After each sprint completion
