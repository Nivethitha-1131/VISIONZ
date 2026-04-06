"""
VISIONZ — Video Processing Service
Handles video metadata extraction, frame processing, and batch detection
"""

import cv2
import os
import logging
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class VideoMetadata:
    """Video metadata container"""
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.filename = os.path.basename(video_path)
        self.file_size = 0
        self.duration = 0.0
        self.fps = 0.0
        self.total_frames = 0
        self.width = 0
        self.height = 0
        self.codec = ""
        self.resolution = ""
        self.error = None
        
        self._extract_metadata()
    
    def _extract_metadata(self):
        """Extract metadata from video file"""
        try:
            # Get file size
            if os.path.exists(self.video_path):
                self.file_size = os.path.getsize(self.video_path)
            
            # Open video
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.error = "Cannot open video file"
                return
            
            # Extract properties
            self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.duration = self.total_frames / self.fps if self.fps > 0 else 0.0
            
            # Get codec
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            self.codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            
            # Resolution string
            self.resolution = f"{self.width}x{self.height}"
            
            cap.release()
            
            logger.info(f"[VideoMetadata] {self.filename} - {self.resolution} @ {self.fps:.1f}fps, {self.duration:.1f}s")
        
        except Exception as e:
            self.error = str(e)
            logger.error(f"[VideoMetadata] Error: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "file_size": self.file_size,
            "duration": self.duration,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "width": self.width,
            "height": self.height,
            "codec": self.codec,
            "resolution": self.resolution
        }
    
    def is_valid(self) -> bool:
        return self.error is None and self.total_frames > 0


class FrameExtractor:
    """Efficient frame extraction from video"""
    
    # Standard detection frame sizes based on video quality
    FRAME_SIZES = {
        "low": (320, 240),      # < 480p
        "medium": (640, 480),   # 480p - 720p
        "high": (1280, 720),    # 720p - 1080p
        "ultra": (1920, 1440)   # 1080p+
    }
    
    def __init__(self, video_path: str, skip_frames: int = 1, auto_resize: bool = True):
        self.video_path = video_path
        self.skip_frames = skip_frames
        self.auto_resize = auto_resize
        self.current_frame_idx = 0
        self.cap = None
        self.target_size = None
        self._open()
    
    def _open(self):
        """Open video file and determine target frame size"""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video: {self.video_path}")
        
        if self.auto_resize:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.target_size = self._get_optimal_frame_size(width, height)
    
    def _get_optimal_frame_size(self, width: int, height: int) -> Tuple[int, int]:
        """Determine optimal frame size based on video resolution"""
        total_pixels = width * height
        
        if total_pixels < 230400:  # < 480p
            return self.FRAME_SIZES["low"]
        elif total_pixels < 921600:  # < 720p
            return self.FRAME_SIZES["medium"]
        elif total_pixels < 2073600:  # < 1440p
            return self.FRAME_SIZES["high"]
        else:
            return self.FRAME_SIZES["ultra"]
    
    def get_next_frame(self) -> Tuple[Optional[np.ndarray], int]:
        """Get next frame (skipping frames if configured)"""
        if self.cap is None:
            return None, -1
        
        for _ in range(self.skip_frames):
            ret, frame = self.cap.read()
            if not ret:
                return None, -1
            self.current_frame_idx += 1
        
        # Resize frame if target size is set
        if self.target_size and ret:
            frame = cv2.resize(frame, self.target_size, interpolation=cv2.INTER_LINEAR)
        
        return frame, self.current_frame_idx
    
    def seek_frame(self, frame_idx: int):
        """Seek to specific frame"""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            self.current_frame_idx = frame_idx
    
    def close(self):
        """Close video file"""
        if self.cap:
            self.cap.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DetectionResult:
    """Single detection result with metadata"""
    
    def __init__(
        self,
        frame_idx: int,
        frame_timestamp: float,
        class_id: int,
        class_name: str,
        confidence: float,
        bbox: Tuple[float, float, float, float],
        severity: str = "warning",
        detection_id: Optional[int] = None
    ):
        self.frame_idx = frame_idx
        self.frame_timestamp = frame_timestamp
        self.class_id = class_id
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.severity = severity
        self.detection_id = detection_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_idx": self.frame_idx,
            "frame_timestamp": self.frame_timestamp,
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": float(self.confidence),
            "bbox": {
                "x1": float(self.bbox[0]),
                "y1": float(self.bbox[1]),
                "x2": float(self.bbox[2]),
                "y2": float(self.bbox[3])
            },
            "severity": self.severity,
            "detection_id": self.detection_id
        }


class VideoProcessingService:
    """Complete video processing pipeline"""
    
    def __init__(self, yolo_service):
        self.yolo_service = yolo_service
    
    def process_video(
        self,
        video_path: str,
        max_frames: Optional[int] = None,
        skip_frames: int = 1,
        confidence_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process entire video for defect detection
        
        Args:
            video_path: Path to video file
            max_frames: Maximum frames to process (None = all)
            skip_frames: Process every Nth frame
            confidence_threshold: Override detector confidence threshold
        
        Returns:
            Processing result with detections and statistics
        """
        
        # Validate video exists
        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"Video file not found: {video_path}",
                "metadata": None,
                "detections": [],
                "statistics": {}
            }
        
        # Extract metadata
        metadata = VideoMetadata(video_path)
        if not metadata.is_valid():
            return {
                "success": False,
                "error": f"Invalid video: {metadata.error}",
                "metadata": metadata.to_dict(),
                "detections": [],
                "statistics": {}
            }
        
        try:
            # Process frames
            all_detections = []
            defect_summary = {}
            failed_frames = 0
            processed_frames = 0
            
            with FrameExtractor(video_path, skip_frames=skip_frames) as extractor:
                frame_idx = 0
                while True:
                    frame, frame_idx = extractor.get_next_frame()
                    if frame is None:
                        break
                    
                    processed_frames += 1
                    timestamp = frame_idx / metadata.fps if metadata.fps > 0 else 0.0
                    
                    try:
                        # Run detection
                        annotated_frame, detections = self.yolo_service.detect_frame(frame)
                        
                        # Collect detection results
                        for detection in detections:
                            result = DetectionResult(
                                frame_idx=frame_idx,
                                frame_timestamp=timestamp,
                                class_id=detection.class_id,
                                class_name=detection.class_name,
                                confidence=detection.confidence,
                                bbox=detection.bbox,
                                severity=detection.severity
                            )
                            all_detections.append(result)
                            
                            # Update summary
                            if detection.class_name not in defect_summary:
                                defect_summary[detection.class_name] = 0
                            defect_summary[detection.class_name] += 1
                    
                    except Exception as e:
                        logger.error(f"[VideoProcessing] Frame {frame_idx} error: {e}")
                        failed_frames += 1
                    
                    # Stop if max frames reached
                    if max_frames and processed_frames >= max_frames:
                        break
            
            # Generate report
            report = {
                "success": True,
                "metadata": metadata.to_dict(),
                "processing": {
                    "total_frames": metadata.total_frames,
                    "processed_frames": processed_frames,
                    "skipped_frames": skip_frames - 1,
                    "failed_frames": failed_frames,
                    "detections_found": len(all_detections),
                    "processing_time_seconds": (datetime.now().isoformat())
                },
                "statistics": {
                    "defect_summary": defect_summary,
                    "total_defects": len(all_detections),
                    "defect_rate": f"{(len(all_detections) / processed_frames * 100):.2f}%" if processed_frames > 0 else "0%",
                    "unique_classes": len(defect_summary),
                    "frames_with_defects": len(set(d.frame_idx for d in all_detections))
                },
                "detections": [d.to_dict() for d in all_detections[:100]],  # Limit response
                "full_detections": all_detections  # Keep for database writing
            }
            
            logger.info(f"[VideoProcessing] Complete: {len(all_detections)} detections in {processed_frames} frames")
            return report
        
        except Exception as e:
            logger.error(f"[VideoProcessing] Error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "metadata": metadata.to_dict(),
                "detections": [],
                "statistics": {}
            }
    
    def save_detections_to_db(
        self,
        detections: List[DetectionResult],
        video_id: int,
        user_id: int,
        db_connection
    ) -> Dict[str, Any]:
        """
        Save detection results to database
        
        Args:
            detections: List of DetectionResult objects
            video_id: ID of source video
            user_id: ID of user who processed video
            db_connection: Database connection
        
        Returns:
            Save operation summary
        """
        
        cur = db_connection.cursor()
        saved_count = 0
        error_count = 0
        
        try:
            for detection in detections:
                try:
                    cur.execute("""
                        INSERT INTO detections
                        (video_id, user_id, defect_type, severity, confidence,
                         frame_number, video_timestamp, bbox_x, bbox_y, bbox_w, bbox_h)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        video_id, user_id, detection.class_name, detection.severity,
                        detection.confidence, detection.frame_idx, detection.frame_timestamp,
                        detection.bbox[0], detection.bbox[1],
                        detection.bbox[2] - detection.bbox[0],  # width
                        detection.bbox[3] - detection.bbox[1]   # height
                    ))
                    saved_count += 1
                
                except Exception as e:
                    error_count += 1
                    logger.error(f"[DB] Error saving detection: {e}")
                    continue
            
            # Update video status
            cur.execute(
                "UPDATE videos SET status = ? WHERE id = ?",
                ("processed", video_id)
            )
            
            db_connection.commit()
            
            return {
                "success": True,
                "saved_count": saved_count,
                "error_count": error_count,
                "total_detections": len(detections),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"[DB] Batch save error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "saved_count": saved_count,
                "error_count": error_count
            }


# Global instance
_video_processor_instance = None


def get_video_processor(yolo_service=None):
    """Get or create video processor instance"""
    global _video_processor_instance
    if _video_processor_instance is None:
        if yolo_service is None:
            from app.services.yolo_service import get_yolo_service
            yolo_service = get_yolo_service()
        _video_processor_instance = VideoProcessingService(yolo_service)
    return _video_processor_instance
