# YOLOv6 Model Training Guide for VISIONZ

## Overview
This guide explains how to prepare your dataset and fine-tune the YOLOv6 model for your specific product defects.

---

## Step 1: Prepare Your Training Dataset

### Directory Structure
```
training_data/
├── images/
│   ├── train/           # 70% of images
│   ├── val/             # 15% of images
│   └── test/            # 15% of images
└── labels/
    ├── train/           # YOLO format labels
    ├── val/
    └── test/
```

### Image Requirements
- **Format**: JPG, PNG
- **Size**: 640×480 to 1920×1440 (will be auto-resized)
- **Quantity**: Min 100 images per defect class (ideally 500+)
- **Variety**: Different angles, lighting, backgrounds
- **Resolution**: Capture at same resolution as production cameras

### Annotating Images

Use **Roboflow** or **LabelImg**:

1. **Download LabelImg**:
   ```bash
   pip install labelImg
   labelImg
   ```

2. **Create labels in YOLO format**:
   - For each image `image.jpg`, create `image.txt`
   - Format: `<class_id> <xc> <yc> <w> <h>` (normalized 0-1)

   Example: `0 0.5 0.5 0.3 0.4`
   - Class 0 = "dent"
   - Center at (0.5, 0.5) = middle of image
   - Width 0.3, Height 0.4 = 30% × 40% of image

3. **Multi-class per image**:
   ```
   # image.txt
   0 0.3 0.2 0.1 0.15   # dent
   7 0.7 0.8 0.15 0.1   # barcode_unreadable
   ```

---

## Step 2: Create Configuration File

Create `data.yaml`:

```yaml
# Dataset paths
path: /absolute/path/to/training_data  # dataset root
train: images/train
val: images/val
test: images/test

# Number of classes (VISIONZ has 17)
nc: 17

# Class names in order (MUST match IDs in yolo_service.py)
names: [
  'dent',                      # 0
  'damage',                    # 1
  'torn',                      # 2
  'scratch',                   # 3
  'crack',                     # 4
  'shape_deformation',         # 5
  'mislabeling',               # 6
  'barcode_unreadable',        # 7
  'missing_batch_number',      # 8
  'missing_expiry_date',       # 9
  'wrong_product_name',        # 10
  'missing_regulatory_info',   # 11
  'color_fade',                # 12
  'color_deviation',           # 13
  'discoloration',             # 14
  'missing_component',         # 15
  'loose_component'            # 16
]
```

---

## Step 3: Install Dependencies

```bash
# Activate virtual environment
cd D:\VISIONZ_FIXED_VIDEO
.\.venv\Scripts\Activate.ps1

# Install ultralytics
pip install --upgrade ultralytics

# Verify installation
python -c "from ultralytics import YOLO; print('✓ Ready to train')"
```

---

## Step 4: Train the Model

### Option A: Quick Start (Recommended)

```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO('yolov6s.pt')

# Train on your data
results = model.train(
    data='data.yaml',           # Your config file
    epochs=100,                 # Number of training passes
    imgsz=640,                  # Image size for training
    batch=16,                   # Batch size (adjust for GPU memory)
    patience=20,                # Early stopping patience
    device=0,                   # GPU ID (0 for first GPU, 'cpu' for CPU)
    project='runs/detect',      # Output directory
    name='visionz_v1',          # Experiment name
    save=True,                  # Save checkpoints
    verbose=True
)
```

### Option B: Advanced Training (With Data Augmentation)

```python
from ultralytics import YOLO

model = YOLO('yolov6s.pt')

results = model.train(
    data='data.yaml',
    epochs=150,
    imgsz=768,
    batch=32,
    device=0,
    
    # Augmentation
    hsv_h=0.015,        # HSV-Hue augmentation (%)
    hsv_s=0.7,          # HSV-Saturation augmentation (%)
    hsv_v=0.4,          # HSV-Value augmentation (%)
    degrees=10,         # Rotation (-10 to +10 degrees)
    translate=0.1,      # Translation (fraction)
    scale=0.5,          # Scale augmentation (±50%)
    flipud=0.5,         # Flip upside-down probability
    fliplr=0.5,         # Flip left-right probability
    mosaic=1.0,         # Mosaic augmentation
    mixup=0.1,          # Mixup augmentation
    
    # Save best model
    save_period=10,
    patience=25,
)
```

### Option C: Using Script

Create `train.py`:

```python
#!/usr/bin/env python
"""VISIONZ YOLOv6 Training Script"""

import sys
import os
from pathlib import Path
from ultralytics import YOLO
import argparse

def main():
    parser = argparse.ArgumentParser(description='Train YOLOv6 for VISIONZ')
    parser.add_argument('--data', type=str, required=True, help='Path to data.yaml')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch', type=int, default=16, help='Batch size')
    parser.add_argument('--imgsz', type=int, default=640, help='Image size')
    parser.add_argument('--device', default=0, help='Device to use (0=GPU, cpu=CPU)')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("VISIONZ YOLOv6 Training")
    print("="*60)
    
    # Load model
    print(f"\n[1] Loading YOLOv6s pretrained model...")
    model = YOLO('yolov6s.pt')
    
    # Train
    print(f"\n[2] Starting training with config: {args.data}")
    print(f"    Epochs: {args.epochs}")
    print(f"    Batch size: {args.batch}")
    print(f"    Image size: {args.imgsz}×{args.imgsz}")
    print(f"    Device: {args.device}\n")
    
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project='runs/detect',
        name='visionz_custom',
        patience=20,
    )
    
    # Evaluate
    print(f"\n[3] Evaluating model...")
    metrics = model.val()
    
    # Save
    best_model = 'runs/detect/visionz_custom/weights/best.pt'
    print(f"\n[4] Best model saved to: {best_model}")
    print(f"    mAP50: {metrics.box.map50:.3f}")
    print(f"    mAP50-95: {metrics.box.map:.3f}")

if __name__ == '__main__':
    main()
```

Run training:
```bash
python train.py --data data.yaml --epochs 100 --batch 16 --device 0
```

---

## Step 5: Validate & Test

### Validate on Test Set

```python
from ultralytics import YOLO

model = YOLO('runs/detect/visionz_custom/weights/best.pt')
metrics = model.val()

print(f"mAP50: {metrics.box.map50}")
print(f"mAP50-95: {metrics.box.map}")
```

### Test on Single Image

```python
model = YOLO('runs/detect/visionz_custom/weights/best.pt')

# Detect
results = model.predict(source='test_image.jpg', conf=0.45)

# Print results
for r in results:
    print(f"Boxes: {r.boxes.cls}")
    print(f"Confidence: {r.boxes.conf}")
    print(f"Detections: {len(r.boxes)}")

# Save annotated image
results[0].save('test_output.jpg')
```

### Test on Video

```python
model = YOLO('runs/detect/visionz_custom/weights/best.pt')

results = model.predict(
    source='test_video.mp4',
    conf=0.45,
    save=True,
    device=0
)
```

---

## Step 6: Deploy the Model

### Replace in VISIONZ

```bash
# Copy trained model to backend
cp runs/detect/visionz_custom/weights/best.pt D:\VISIONZ_FIXED_VIDEO\visionz_fixed\backend\weights\yolov6_custom.pt
```

### Update Backend Configuration

Edit `.env`:
```env
YOLO_MODEL_PATH=./weights/yolov6_custom.pt
YOLO_CONFIDENCE=0.45
```

### Update yolo_service.py

```python
def __init__(self, model_path: str = "./weights/yolov6_custom.pt"):
    self.model_path = model_path
    self.model = YOLO(model_path)
    self.available = True
```

### Restart Backend

```bash
# Terminal 1
cd D:\VISIONZ_FIXED_VIDEO
.\.venv\Scripts\Activate.ps1
cd visionz_fixed\backend
python run.py
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Out of Memory** | Reduce `batch` (e.g., 8 or 4) or `imgsz` (e.g., 480) |
| **Low accuracy** | Add more training images (500+ per class), or increase `epochs` |
| **Training too slow** | Use GPU: `device=0`, or reduce `imgsz` |
| **Labels not found** | Ensure `.txt` files are in same folder as images |
| **Wrong class predictions** | Verify class IDs in labels match `data.yaml` |
| **Model too large** | Use lighter variant: `yolov6n.pt` instead of `yolov6l.pt` |

---

## Performance Tips

### ✅ Best Practices
- **Balanced dataset**: Similar number of images per class
- **Quality labels**: Precise bounding boxes (not loose)
- **Consistent lighting**: Match production environment lighting
- **Multiple angles**: Images from different camera positions
- **Augmentation**: Let YOLOv6 augment during training

### ⚡ Speed Optimization
- Use lighter model: `yolov6n.pt` (nanno)
- Reduce `imgsz`: 416 instead of 640
- Quantization: Convert to INT8 after training
- GPU acceleration: CUDA-enabled GPU required

### 🎯 Accuracy Optimization
- Use heavier model: `yolov6l.pt` (large)
- Increase `imgsz`: 768 or 896
- Data augmentation: mixup, mosaic enabled
- More epochs: 150-200 for fine-tuning
- Lower confidence threshold: 0.3 instead of 0.45

---

## Model Variants

| Model | Parameters | Speed (GPU) | Speed (CPU) | Best For |
|-------|-----------|-----------|-----------|----------|
| yolov6n | 4.3M | 6ms | 100ms | Fast detection, real-time |
| yolov6s | 16.5M | 9ms | 220ms | **Recommended** |
| yolov6m | 34.3M | 15ms | 400ms | Balanced |
| yolov6l | 59.5M | 22ms | 700ms | High accuracy |
| yolov6x | 140M | 35ms | 1200ms | Maximum accuracy |

---

## Dataset Examples

### Minimal Training (500 images total)
```
- 50 images per class
- 350 training, 75 validation, 75 test
- Epochs: 50
- Time: ~10 minutes (GPU)
```

### Standard Training (1000 images)
```
- 60 images per class
- 700 training, 150 validation, 150 test
- Epochs: 100
- Time: ~25 minutes (GPU)
```

### Production Training (5000+ images)
```
- 300+ images per class
- 3500 training, 750 validation, 750 test
- Epochs: 150
- Time: ~2+ hours (GPU)
```

---

## Data Sources

### Synthetic Data
- Generate using CAD → rendering pipeline
- Use GAN to create variations
- Augment existing images

### Public Datasets
- COCO (general objects)
- Pascal VOC (detection benchmarks)
- Roboflow Community (including defect datasets)

### Capture Your Own
1. Set up 1-2 cameras on production line
2. Capture normal + defective products
3. Label with LabelImg/Roboflow
4. Split: 70% train, 15% val, 15% test
5. Train model

---

## Monitoring Training

### Tensorboard
```bash
tensorboard --logdir runs/detect
# Open browser: http://localhost:6006
```

### Training Output
```
Epoch 1/100
  100%|████████| 35/35 [00:45<00:00, 1.29s/it]
  Class     Images  Instances      Box(P          R      mAP50  mAP50-95)
  all         600       850      0.823      0.756      0.812      0.512
```

---

## Production Checklist

- [ ] Dataset prepared with 500+ images
- [ ] Labels verified in YOLO format
- [ ] `data.yaml` created with correct paths
- [ ] Model trained for 100+ epochs
- [ ] Validation metrics > 80% mAP50
- [ ] Test set evaluated separately
- [ ] Model weights saved to `weights/` folder
- [ ] `.env` updated with new model path
- [ ] Backend restarted successfully
- [ ] Test video processed with new model

---

## Support

- **Ultralytics Docs**: https://docs.ultralytics.com/
- **YOLO Guide**: https://github.com/ultralytics/yolov5/wiki
- **Roboflow**: https://roboflow.com/ (annotation tool)

---

**Last Updated**: 2026-03-30  
**System**: VISIONZ v1.0 - YOLOv6 Training Guide
