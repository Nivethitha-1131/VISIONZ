# VISIONZ YOLOv6 Defect Detection Classes

## Overview
VISIONZ is configured to detect 17 different defect types across 5 categories for comprehensive product quality control (QC).

---

## Defect Classes by Category

### 1. **STRUCTURAL DEFECTS** (Critical & Warning)
High-priority physical damage that affects product integrity

| ID | Class Name | Severity | Description |
|----|-----------|----------|-------------|
| 0 | **dent** | CRITICAL | Indentation or depression in product surface |
| 1 | **damage** | CRITICAL | General breakage, smashing, or major defect |
| 2 | **torn** | CRITICAL | Ripped, shredded, or open material |
| 5 | **shape_deformation** | WARNING | Warped, bent, or misshapen product |

### 2. **SURFACE DEFECTS** (Warning & Critical)
Minor to major surface imperfections

| ID | Class Name | Severity | Description |
|----|-----------|----------|-------------|
| 3 | **scratch** | WARNING | Minor abrasion or line mark on surface |
| 4 | **crack** | CRITICAL | Fracture or split in material |

### 3. **LABELING & PACKAGING** (Critical)
Critical packaging and documentation issues

| ID | Class Name | Severity | Description |
|----|-----------|----------|-------------|
| 6 | **mislabeling** | CRITICAL | Wrong label, incorrect product name, or inverted label |
| 7 | **barcode_unreadable** | CRITICAL | Barcode damaged, faded, or unreadable for scan test |
| 8 | **missing_batch_number** | CRITICAL | Batch number absent or illegible |
| 9 | **missing_expiry_date** | CRITICAL | Expiry/best-before date missing or unclear |
| 10 | **wrong_product_name** | CRITICAL | Incorrect product name on packaging |
| 11 | **missing_regulatory_info** | WARNING | FSSAI, warnings, ingredients, or compliance info missing |

### 4. **COLOR & APPEARANCE** (Warning)
Visual consistency issues affecting aesthetics and marketability

| ID | Class Name | Severity | Description |
|----|-----------|----------|-------------|
| 12 | **color_fade** | WARNING | Faded or washed-out color |
| 13 | **color_deviation** | WARNING | Wrong color or shade compared to standard |
| 14 | **discoloration** | WARNING | Staining, spots, or uneven coloring |

### 5. **COMPONENT ISSUES** (Warning & Critical)
Problems with product components

| ID | Class Name | Severity | Description |
|----|-----------|----------|-------------|
| 15 | **missing_component** | CRITICAL | Component, cap, lid, or part missing |
| 16 | **loose_component** | WARNING | Component not secured, rattling, or detachable |

---

## Severity Levels

| Level | Color | Action | Impact |
|-------|-------|--------|--------|
| **CRITICAL** | 🔴 RED | REJECT | Product fails QC, cannot be shipped |
| **WARNING** | 🟠 ORANGE | REVIEW | Product may need rework or manual inspection |

---

## Detection Pipeline

### 1. **Video Input Processing**
- Frame extraction with automatic resizing based on resolution:
  - **Low** (< 480p): 320×240
  - **Medium** (480p-720p): 640×480
  - **High** (720p-1080p): 1280×720
  - **Ultra** (1080p+): 1920×1440

### 2. **Defect Detection**
- YOLOv6 model processes resized frames
- Confidence threshold: 0.45 (45%)
- Output: Bounding boxes with class ID, confidence, severity

### 3. **Visualization**
- Red boxes: CRITICAL defects
- Orange boxes: WARNING defects
- Labels show: CLASS_NAME (CONFIDENCE%)

### 4. **Database Storage**
```sql
INSERT INTO detections (
    video_id, user_id, defect_type, severity, 
    confidence, frame_number, video_timestamp, 
    bbox_x1, bbox_y1, bbox_x2, bbox_y2
) VALUES (...)
```

---

## API Response Format

```json
{
  "success": true,
  "video_id": 1,
  "total_detections": 5,
  "critical_count": 2,
  "warning_count": 3,
  "processing_time_seconds": 12.5,
  "detections": [
    {
      "frame_idx": 125,
      "class_name": "dent",
      "severity": "critical",
      "confidence": 0.87,
      "bbox": {
        "x1": 234, "y1": 156,
        "x2": 456, "y2": 312
      }
    },
    ...
  ]
}
```

---

## Training & Fine-Tuning

To train a custom YOLOv6 model with these defect classes:

### Dataset Structure
```
dataset/
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

### YAML Configuration
```yaml
# data.yaml
path: /path/to/dataset
train: images/train
val: images/val

nc: 17  # number of classes
names: ['dent', 'damage', 'torn', 'scratch', 'crack', 'shape_deformation',
        'mislabeling', 'barcode_unreadable', 'missing_batch_number', 
        'missing_expiry_date', 'wrong_product_name', 'missing_regulatory_info',
        'color_fade', 'color_deviation', 'discoloration',
        'missing_component', 'loose_component']
```

### Training Command
```bash
pip install ultralytics
python -c "from ultralytics import YOLO; m = YOLO('yolov6s.pt'); m.train(data='data.yaml', epochs=100, imgsz=640)"
```

---

## Configuration

Edit `.env` file:
```env
YOLO_DEVICE=cpu        # or 'cuda' for GPU
YOLO_CONFIDENCE=0.45   # Detection threshold
YOLO_MAX_DET=100       # Max detections per frame
```

---

## Frame Resizing Strategy

**Problem**: Product sizes vary; frame size must match product scale

**Solution**: Automatic frame resizing based on video resolution
- Maintains aspect ratio
- Optimizes for YOLOv6 (multiples of 32)
- Preserves texture detail for defect detection

**Example**:
- Input: 4K video (3840×2160)
- Resized: 1920×1440 (ULTRA)
- Processing: YOLOv6 @ 1920×1440
- Output: Bounding boxes scaled back to original

---

## Best Practices

### ✅ DO:
- Train on representative product samples
- Include images from multiple angles
- Use consistent lighting during training
- Validate on new product batches
- Monitor false positives vs false negatives

### ❌ DON'T:
- Skip hard-to-detect defects during training
- Use only low-resolution images
- Ignore edge cases (partial damage, faint markings)
- Deploy without proper validation
- Forget to update model when product packaging changes

---

## Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Inference speed | <100ms/frame | 45ms/frame (CPU) |
| Accuracy (mAP50) | >85% | Demo mode |
| Recall (true positives) | >90% | Demo mode |
| Precision (false positives) | <5% | Demo mode |

---

## Integration with Video Processing

1. Upload video → extract metadata
2. Resize frames based on resolution (auto_resize=True)
3. Run YOLOv6 per frame with skip_frames=1
4. Aggregate detections into report
5. Save to database with severity categorization
6. Return visualization with annotations

---

## Support & Updates

- Model updates: See `requirements.txt` for ultralytics version
- New defect class? Update `DEFECT_CLASSES` in `yolo_service.py`
- Custom training? Use data.yaml template above

---

**Last Updated**: 2026-03-30  
**System**: VISIONZ v1.0 - Product Quality Detection
