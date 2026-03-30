"""
VISIONZ — YOLOv6 Object Detection Service
Real-time defect detection using YOLOv6
"""

import os
import cv2
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

try:
    import torch
    from ultralytics import YOLO
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[YOLOv6] Warning: PyTorch not available - running in demo mode")


class Detection:
    """Single detection result"""
    
    def __init__(
        self,
        class_id: int,
        class_name: str,
        confidence: float,
        bbox: Tuple[float, float, float, float],
        severity: str = "warning"
    ):
        self.class_id = class_id
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox  # (x, y, w, h)
        self.severity = severity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": float(self.confidence),
            "bbox": {
                "x": float(self.bbox[0]),
                "y": float(self.bbox[1]),
                "w": float(self.bbox[2]),
                "h": float(self.bbox[3])
            },
            "severity": self.severity
        }


class YOLOv6Service:
    """YOLOv6 object detection service"""
    
    # Defect classes and severity mapping - Product Quality Control
    DEFECT_CLASSES = {
        # Physical/Structural Defects
        0: {"name": "dent", "severity": "critical", "category": "structural"},
        1: {"name": "damage", "severity": "critical", "category": "structural"},
        2: {"name": "torn", "severity": "critical", "category": "structural"},
        3: {"name": "scratch", "severity": "warning", "category": "surface"},
        4: {"name": "crack", "severity": "critical", "category": "surface"},
        5: {"name": "shape_deformation", "severity": "warning", "category": "structural"},
        
        # Labeling & Packaging
        6: {"name": "mislabeling", "severity": "critical", "category": "label"},
        7: {"name": "barcode_unreadable", "severity": "critical", "category": "label"},
        8: {"name": "missing_batch_number", "severity": "critical", "category": "label"},
        9: {"name": "missing_expiry_date", "severity": "critical", "category": "label"},
        10: {"name": "wrong_product_name", "severity": "critical", "category": "label"},
        11: {"name": "missing_regulatory_info", "severity": "warning", "category": "label"},
        
        # Color & Appearance
        12: {"name": "color_fade", "severity": "warning", "category": "appearance"},
        13: {"name": "color_deviation", "severity": "warning", "category": "appearance"},
        14: {"name": "discoloration", "severity": "warning", "category": "appearance"},
        
        # Component Issues
        15: {"name": "missing_component", "severity": "critical", "category": "component"},
        16: {"name": "loose_component", "severity": "warning", "category": "component"},
    }
    
    def __init__(self, model_name: str = "yolov8s", confidence_threshold: float = 0.45):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.available = False
        self.device = None
        
        if TORCH_AVAILABLE:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize YOLOv8 model"""
        try:
            # Set device
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f"[YOLO] Using device: {self.device}")
            
            # Try to load pretrained model (requires internet for first download)
            try:
                # Use yolov8 variants: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
                model_variant = "yolov8s.pt"  # Small model: good balance of speed/accuracy
                print(f"[YOLO] Loading model: {model_variant}...")
                self.model = YOLO(model_variant)
                self.model.to(self.device)
                self.available = True
                print(f"[YOLO] Model '{model_variant}' loaded successfully ✓")
            except Exception as e:
                print(f"[YOLO] Could not load model: {e}")
                print("[YOLO] Running in demo mode")
                self.available = False
        
        except Exception as e:
            print(f"[YOLO] Initialization error: {e}")
            self.available = False
    
    def detect_frame(
        self,
        frame: np.ndarray
    ) -> Tuple[np.ndarray, List[Detection]]:
        """
        Run detection on a frame
        
        Args:
            frame: Input frame (BGR format)
        
        Returns:
            Tuple of (annotated_frame, detections_list)
        """
        
        detections = []
        annotated_frame = frame.copy()
        
        if not self.available:
            return annotated_frame, detections
        
        try:
            # Make prediction
            results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
            
            # Extract detections from first result
            if results and len(results) > 0:
                result = results[0]
                boxes = result.boxes
                
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        xyxy = box.xyxy[0]  # [x1, y1, x2, y2]
                        x1, y1, x2, y2 = float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])
                        x, y = x1, y1
                        w, h = x2 - x1, y2 - y1
                        
                        # Get confidence and class
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        
                        # Get class info
                        if class_id in self.DEFECT_CLASSES:
                            class_info = self.DEFECT_CLASSES[class_id]
                            class_name = class_info["name"]
                            severity = class_info["severity"]
                            category = class_info.get("category", "unknown")
                        else:
                            class_name = f"defect_{class_id}"
                            severity = "warning"
                            category = "unknown"
                        
                        # Create detection
                        detection = Detection(class_id, class_name, confidence, (x, y, w, h), severity)
                        detections.append(detection)
                        
                        # Draw on frame with enhanced visualization
                        # Color coding: Red=critical, Orange=warning, Green=info
                        if severity == "critical":
                            color = (0, 0, 255)  # Red
                            thickness = 3
                        else:
                            color = (0, 165, 255)  # Orange
                            thickness = 2
                        
                        # Draw bounding box
                        cv2.rectangle(annotated_frame, (int(x), int(y)), (int(x2), int(y2)), color, thickness)
                        
                        # Draw label background
                        label = f"{class_name.upper()} ({confidence:.0%})"
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.6
                        font_thickness = 2
                        (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
                        
                        # Label background
                        cv2.rectangle(
                            annotated_frame,
                            (int(x-2), int(y-text_h-10)),
                            (int(x+text_w+4), int(y)),
                            color,
                            -1
                        )
                        
                        # Draw text
                        cv2.putText(
                            annotated_frame,
                            label,
                            (int(x), int(y-5)),
                            font,
                            font_scale,
                            (255, 255, 255),
                            font_thickness
                        )
        
        except Exception as e:
            print(f"[YOLOv6] Detection error: {e}")
            detections = []
        
        return annotated_frame, detections
    
    def detect_video(
        self,
        video_path: str,
        max_frames: Optional[int] = None,
        skip_frames: int = 1
    ) -> Dict[str, Any]:
        """
        Run detection on a video file
        
        Args:
            video_path: Path to video file
            max_frames: Maximum frames to process (None = all)
            skip_frames: Process every Nth frame
        
        Returns:
            Detection summary
        """
        
        if not os.path.exists(video_path):
            return {
                "success": False,
                "message": f"Video file not found: {video_path}",
                "detections": [],
                "summary": {}
            }
        
        if not self.available:
            return self._demo_video_detection(video_path)
        
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        all_detections = []
        defect_counts = {}
        frame_count = 0
        processed_frames = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Skip frames if specified
                if frame_count % skip_frames != 0:
                    continue
                
                processed_frames += 1
                
                # Process frame
                _, detections = self.detect_frame(frame)
                
                for detection in detections:
                    all_detections.append({
                        "frame": frame_count,
                        "timestamp": frame_count / fps if fps > 0 else 0,
                        **detection.to_dict()
                    })
                    
                    # Count by class
                    if detection.class_name not in defect_counts:
                        defect_counts[detection.class_name] = 0
                    defect_counts[detection.class_name] += 1
                
                # Stop if max frames reached
                if max_frames and processed_frames >= max_frames:
                    break
            
            cap.release()
            
            return {
                "success": True,
                "video_path": video_path,
                "total_frames": total_frames,
                "fps": fps,
                "resolution": f"{width}x{height}",
                "processed_frames": processed_frames,
                "detection_count": len(all_detections),
                "defect_summary": defect_counts,
                "detections": all_detections[:100],  # Limit response size
                "timestamp": datetime.now().isoformat(),
                "model": self.model_name
            }
        
        except Exception as e:
            cap.release()
            print(f"[YOLOv6] Video processing error: {e}")
            return {
                "success": False,
                "message": str(e),
                "detections": [],
                "summary": {}
            }
    
    def _demo_video_detection(self, video_path: str) -> Dict[str, Any]:
        """Demo video detection when model unavailable"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"success": False, "message": "Cannot open video"}
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        demo_defects = {
            "damage": np.random.randint(3, 8),
            "contamination": np.random.randint(1, 4),
            "label_defect": np.random.randint(2, 6),
        }
        
        return {
            "success": True,
            "video_path": video_path,
            "total_frames": total_frames,
            "fps": fps,
            "resolution": f"{width}x{height}",
            "processed_frames": min(100, total_frames),
            "detection_count": sum(demo_defects.values()),
            "defect_summary": demo_defects,
            "detections": [],
            "timestamp": datetime.now().isoformat(),
            "model": "yolov6-demo",
            "note": "Running in demo mode"
        }


# Global instance
_yolo_instance: Optional[YOLOv6Service] = None


def get_yolo_service() -> YOLOv6Service:
    """Get or create YOLOv6 service instance"""
    global _yolo_instance
    if _yolo_instance is None:
        _yolo_instance = YOLOv6Service()
    return _yolo_instance


def initialize_yolo():
    """Initialize YOLOv6 service"""
    global _yolo_instance
    _yolo_instance = YOLOv6Service()
    print(f"[YOLOv6] Service initialized - Available: {_yolo_instance.available}")
    if _yolo_instance.available:
        print(f"[YOLOv6] Model: {_yolo_instance.model_name}")
        print(f"[YOLOv6] Device: {_yolo_instance.device}")
