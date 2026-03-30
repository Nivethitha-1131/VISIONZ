"""
VISIONZ — Pydantic Models (Request & Response schemas)
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ════════════════════════════════
#  AUTH
# ════════════════════════════════

class LoginRequest(BaseModel):
    email:    str
    password: str
    role:     str  # admin | manager | operator


class LoginResponse(BaseModel):
    token:      str
    user_id:    int
    name:       str
    email:      str
    role:       str
    avatar:     str
    department: Optional[str] = None
    login_time: str


class LogoutRequest(BaseModel):
    token: str


# ════════════════════════════════
#  USERS
# ════════════════════════════════

class UserOut(BaseModel):
    id:            int
    name:          str
    email:         str
    role:          str
    avatar:        str
    department:    Optional[str]
    created_at:    Optional[str]
    last_login:    Optional[str]


class UserUpdateRequest(BaseModel):
    name:       Optional[str] = None
    department: Optional[str] = None


class ProfileResponse(BaseModel):
    id:                  int
    name:                str
    email:               str
    role:                str
    avatar:              str
    department:          Optional[str]
    login_time:          Optional[str]
    reports_downloaded:  int
    session_count:       int


# ════════════════════════════════
#  VIDEO
# ════════════════════════════════

class VideoOut(BaseModel):
    id:            int
    filename:      str
    original_name: str
    file_size:     Optional[int]
    duration:      Optional[float]
    resolution:    Optional[str]
    uploaded_at:   str
    status:        str


# ════════════════════════════════
#  DETECTIONS
# ════════════════════════════════

class DetectionIn(BaseModel):
    video_id:        Optional[int]  = None
    defect_type:     str            # dent, damage, torn, scratch, crack, etc.
    category:        Optional[str]  = None  # structural, surface, label, appearance, component
    severity:        str            # critical | warning | passed
    confidence:      float
    product:         Optional[str]  = None
    line:            Optional[str]  = None
    camera:          Optional[str]  = None
    frame_number:    Optional[int]  = None
    video_timestamp: Optional[float] = None
    bbox_x1:         Optional[float] = None
    bbox_y1:         Optional[float] = None
    bbox_x2:         Optional[float] = None
    bbox_y2:         Optional[float] = None


class DetectionOut(BaseModel):
    id:              int
    video_id:        Optional[int]
    user_id:         int
    defect_type:     str
    category:        Optional[str]
    severity:        str
    confidence:      float
    product:         Optional[str]
    line:            Optional[str]
    camera:          Optional[str]
    frame_number:    Optional[int]
    video_timestamp: Optional[float]
    detected_at:     str


class DetectionBulkIn(BaseModel):
    detections: List[DetectionIn]


# ════════════════════════════════
#  ANALYTICS
# ════════════════════════════════

class AnalyticsPeriodResponse(BaseModel):
    period:          str
    date_label:      str
    total_scanned:   int
    total_defects:   int
    total_approved:  int
    defect_rate:     float
    quality_score:   float
    biscuits_defects: int
    honey_defects:   int
    packets_defects: int
    nuts_defects:    int
    trend:           Optional[List[dict]] = None


class AnalyticsSummaryResponse(BaseModel):
    today:  AnalyticsPeriodResponse
    week:   AnalyticsPeriodResponse
    month:  AnalyticsPeriodResponse


# ════════════════════════════════
#  REPORTS
# ════════════════════════════════

class ReportOut(BaseModel):
    id:            int
    report_name:   str
    report_type:   str
    period_start:  Optional[str]
    period_end:    Optional[str]
    total_scanned: int
    total_defects: int
    quality_score: int
    downloaded:    int
    created_at:    str


class ReportFilterRequest(BaseModel):
    report_type:  Optional[str] = None   # daily | weekly | monthly
    date_from:    Optional[str] = None
    date_to:      Optional[str] = None
