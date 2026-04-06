"""
VISIONZ — Detections Routes
No auth required on save — local tokens won't be in backend DB.
The app works offline-first so we never block detection saving.
"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional
import logging
from app.database import get_db
from app.models.schemas import DetectionIn
from app.errors import DatabaseError, ValidationError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/")
def save_detection(body: DetectionIn, authorization: Optional[str] = Header(None)):
    """
    Save a detection. Auth is optional — works with local tokens too.
    Returns error response on database failure (not silent).
    """
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        # Try to resolve user_id from token if available
        user_id = 1  # default to first user if no auth
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:]
            try:
                cur.execute("""
                    SELECT user_id FROM sessions WHERE token = ? AND is_active = 1
                """, (token,))
                row = cur.fetchone()
                if row:
                    user_id = row["user_id"]
            except Exception as e:
                logger.warning(f"Failed to resolve token: {e}")
                # Continue with default user_id

        # Insert detection
        cur.execute("""
            INSERT INTO detections
            (video_id, user_id, defect_type, severity, confidence,
             product, line, camera, frame_number, video_timestamp,
             bbox_x, bbox_y, bbox_w, bbox_h)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            body.video_id, user_id, body.defect_type, body.severity,
            body.confidence, body.product, body.line, body.camera,
            body.frame_number, body.video_timestamp,
            body.bbox_x, body.bbox_y, body.bbox_w, body.bbox_h,
        ))
        detection_id = cur.lastrowid
        conn.commit()
        
        return {
            "success": True,
            "id": detection_id,
            "message": "Detection saved successfully.",
        }
    
    except Exception as e:
        logger.error(f"Database error saving detection: {e}", exc_info=True)
        raise DatabaseError(
            "Failed to save detection",
            {"error": str(e)}
        )
    
    finally:
        if conn:
            conn.close()


@router.get("/live")
def live_detections(authorization: Optional[str] = Header(None)):
    """Latest 20 detections for live feed."""
    conn = get_db()
    cur  = conn.cursor()
    try:
        cur.execute("SELECT * FROM detections ORDER BY detected_at DESC LIMIT 20")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"detections": rows}
    except Exception:
        conn.close()
        return {"detections": []}


@router.get("/")
def list_detections(
    authorization: Optional[str] = Header(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    conn = get_db()
    cur  = conn.cursor()
    try:
        cur.execute("SELECT * FROM detections ORDER BY detected_at DESC LIMIT ? OFFSET ?", (limit, offset))
        rows = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT COUNT(*) FROM detections")
        total = cur.fetchone()[0]
        conn.close()
        return {"detections": rows, "total": total}
    except Exception:
        conn.close()
        return {"detections": [], "total": 0}
