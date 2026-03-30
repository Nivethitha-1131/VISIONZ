"""
VISIONZ — Video Routes
POST /api/video/upload
POST /api/video/detect
GET  /api/video/list
GET  /api/video/{video_id}
GET  /api/video/{video_id}/analysis
DELETE /api/video/{video_id}
"""

import os
import uuid
import logging
import asyncio
from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Query, Request
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.middleware.rate_limit import rate_limit
from app.services.video_processor import get_video_processor
from app.errors import DatabaseError, FileError, ValidationError

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR   = "uploads"
ALLOWED_EXTS = {".mp4", ".avi", ".mov", ".webm", ".mkv", ".flv"}
MAX_SIZE_MB  = 500


class VideoDetectionRequest(BaseModel):
    """Video detection processing request"""
    video_id: int
    skip_frames: int = 1
    max_frames: Optional[int] = None
    confidence_threshold: Optional[float] = None


class BatchProcessRequest(BaseModel):
    """Batch video processing request"""
    video_ids: list
    skip_frames: int = 1
    max_frames: Optional[int] = None
    confidence_threshold: Optional[float] = None


@router.post("/upload")
@rate_limit(requests=10, window_seconds=3600)  # 10 uploads per hour
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    authorization: str = Header(...)
):
    """Upload a video file for defect detection analysis."""
    user = get_current_user(authorization)

    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTS)}"
        )

    # Read file content
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Max allowed: {MAX_SIZE_MB} MB."
        )

    # Save with unique filename
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path   = os.path.join(UPLOAD_DIR, unique_name)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(content)

    # Insert record
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO videos (user_id, filename, original_name, file_size, status) VALUES (?,?,?,?,?)",
        (user["id"], unique_name, file.filename, len(content), "uploaded")
    )
    video_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        "video_id":     video_id,
        "filename":     unique_name,
        "original_name": file.filename,
        "file_size_mb": round(size_mb, 2),
        "url":          f"/uploads/{unique_name}",
        "message":      "Video uploaded successfully. Ready for analysis.",
    }


@router.get("/list")
def list_videos(authorization: str = Header(...)):
    """List all videos uploaded by current user."""
    user = get_current_user(authorization)
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "SELECT * FROM videos WHERE user_id = ? ORDER BY uploaded_at DESC",
        (user["id"],)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"videos": rows, "total": len(rows)}


@router.get("/{video_id}")
def get_video(video_id: int, authorization: str = Header(...)):
    """Get single video info."""
    user = get_current_user(authorization)
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM videos WHERE id = ? AND user_id = ?", (video_id, user["id"]))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Video not found.")
    return dict(row)


@router.delete("/{video_id}")
def delete_video(video_id: int, authorization: str = Header(...)):
    """Delete a video and its detections."""
    user = get_current_user(authorization)
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT filename FROM videos WHERE id = ? AND user_id = ?", (video_id, user["id"]))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Video not found.")

    # Remove file from disk
    path = os.path.join(UPLOAD_DIR, row["filename"])
    if os.path.exists(path):
        os.remove(path)

    # Delete detections then video record
    cur.execute("DELETE FROM detections WHERE video_id = ?", (video_id,))
    cur.execute("DELETE FROM videos WHERE id = ?", (video_id,))
    conn.commit()
    conn.close()
    return {"message": "Video deleted successfully."}


@router.post("/detect")
@rate_limit(requests=20, window_seconds=3600)  # 20 detections per hour per user
def detect_video_defects(request: Request, req: VideoDetectionRequest, authorization: str = Header(...)):
    """
    Process video for defect detection using YOLOv6.
    Runs detection on frames and saves results to database.
    """
    user = get_current_user(authorization)
    
    try:
        # Get video from database
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM videos WHERE id = ? AND user_id = ?",
            (req.video_id, user["id"])
        )
        video_row = cur.fetchone()
        conn.close()
        
        if not video_row:
            raise HTTPException(status_code=404, detail="Video not found.")
        
        # Build video path
        video_path = os.path.join(UPLOAD_DIR, video_row["filename"])
        if not os.path.exists(video_path):
            raise FileError("Video file not found on disk", {"video_id": req.video_id})
        
        logger.info(f"[Video Processing] Starting detection for video {req.video_id}")
        
        # Process video
        processor = get_video_processor()
        result = processor.process_video(
            video_path,
            max_frames=req.max_frames,
            skip_frames=req.skip_frames,
            confidence_threshold=req.confidence_threshold
        )
        
        if not result["success"]:
            logger.error(f"[Video Processing] Failed: {result.get('error')}")
            raise DatabaseError("Video processing failed", {"error": result.get("error")})
        
        # Save detections to database
        conn = get_db()
        full_detections = result.pop("full_detections", [])  # Extract for batch insert
        
        save_result = processor.save_detections_to_db(
            full_detections,
            req.video_id,
            user["id"],
            conn
        )
        
        conn.close()
        
        if not save_result["success"]:
            logger.error(f"[Video Processing] Save failed: {save_result.get('error')}")
            raise DatabaseError("Failed to save detections", save_result)
        
        logger.info(f"[Video Processing] Complete: Saved {save_result['saved_count']} detections")
        
        # Combine results
        result["save_result"] = save_result
        result["message"] = "Video processed successfully and detections saved."
        
        return result
    
    except Exception as e:
        logger.error(f"[Video Detection] Error: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise DatabaseError(str(e))


@router.get("/{video_id}/analysis")
def get_video_analysis(video_id: int, authorization: str = Header(...)):
    """
    Get detection analysis and statistics for a video.
    Includes defect summary, frames affected, and severity breakdown.
    """
    user = get_current_user(authorization)
    
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Verify video ownership
        cur.execute(
            "SELECT * FROM videos WHERE id = ? AND user_id = ?",
            (video_id, user["id"])
        )
        video_row = cur.fetchone()
        
        if not video_row:
            conn.close()
            raise HTTPException(status_code=404, detail="Video not found.")
        
        # Get all detections for this video
        cur.execute(
            """
            SELECT 
                defect_type, 
                severity, 
                confidence,
                frame_number,
                COUNT(*) as count
            FROM detections
            WHERE video_id = ?
            GROUP BY defect_type, severity, frame_number
            ORDER BY defect_type
            """,
            (video_id,)
        )
        
        detections = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        # Generate statistics
        total_detections = sum(d["count"] for d in detections)
        defect_summary = {}
        severity_summary = {"critical": 0, "warning": 0}
        frames_affected = set()
        
        for det in detections:
            defect_type = det["defect_type"]
            severity = det["severity"]
            
            if defect_type not in defect_summary:
                defect_summary[defect_type] = 0
            defect_summary[defect_type] += det["count"]
            
            if severity in severity_summary:
                severity_summary[severity] += det["count"]
            
            frames_affected.add(det["frame_number"])
        
        return {
            "success": True,
            "video_id": video_id,
            "video_info": dict(video_row),
            "analysis": {
                "total_detections": total_detections,
                "frames_affected": len(frames_affected),
                "defect_summary": defect_summary,
                "severity_summary": severity_summary,
                "detections": detections
            }
        }
    
    except Exception as e:
        logger.error(f"[Video Analysis] Error: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise DatabaseError(str(e))


@router.post("/batch-process")
@rate_limit(requests=5, window_seconds=3600)  # 5 batch processes per hour
def batch_process_videos(request: Request, req: BatchProcessRequest, authorization: str = Header(...)):
    """
    Process multiple videos for defect detection (batch operation).
    Returns summary of all processed videos.
    """
    user = get_current_user(authorization)
    
    try:
        if not req.video_ids:
            raise ValidationError("No videos to process", {"video_ids": "List cannot be empty"})
        
        if len(req.video_ids) > 10:
            raise ValidationError("Too many videos", {"max_allowed": 10, "requested": len(req.video_ids)})
        
        processor = get_video_processor()
        conn = get_db()
        results = []
        
        for video_id in req.video_ids:
            try:
                # Get video
                cur = conn.cursor()
                cur.execute(
                    "SELECT * FROM videos WHERE id = ? AND user_id = ?",
                    (video_id, user["id"])
                )
                video_row = cur.fetchone()
                
                if not video_row:
                    results.append({
                        "video_id": video_id,
                        "success": False,
                        "error": "Video not found"
                    })
                    continue
                
                # Process video
                video_path = os.path.join(UPLOAD_DIR, video_row["filename"])
                result = processor.process_video(
                    video_path,
                    max_frames=req.max_frames,
                    skip_frames=req.skip_frames
                )
                
                if result["success"]:
                    # Save detections
                    full_detections = result.pop("full_detections", [])
                    save_result = processor.save_detections_to_db(
                        full_detections,
                        video_id,
                        user["id"],
                        conn
                    )
                    result["video_id"] = video_id
                    result["save_result"] = save_result
                
                results.append(result)
            
            except Exception as e:
                logger.error(f"[Batch Process] Video {video_id} failed: {e}")
                results.append({
                    "video_id": video_id,
                    "success": False,
                    "error": str(e)
                })
        
        conn.close()
        
        success_count = sum(1 for r in results if r.get("success"))
        failed_count = len(results) - success_count
        
        return {
            "success": True,
            "batch_id": f"batch_{user['id']}",
            "total_videos": len(req.video_ids),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"[Batch Process] Error: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise DatabaseError(str(e))
