# YOLO-Salamander-Tracker

YOLO-based salamander detection project for training and inference on images and video.

## Requirements

Use **Python 3.12**. Other versions (especially Python 3.14+) may fail due to PyTorch compatibility issues.

### macOS / Linux Setup

```bash
deactivate
rm -rf venv

python3.12 -m venv venv
source venv/bin/activate
python --version
pip install --upgrade pip
pip install -r backend/requirements.txt
```

Expected version:

```text
Python 3.12.x
```

### Windows Setup

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend\requirements.txt
```

---

## Model Setup

Place the trained model file:

```text
best.pt
```

inside:

```text
backend/models/
```

Final structure:

```text
backend/
├── models/
│   └── best.pt
├── scripts/
├── data/
└── outputs/
```

---

## Training

Train the YOLO model:

### Windows

```powershell
python backend\scripts\train.py --epochs 75 --imgsz 640 --batch 8 --device 0 --name salamander_run1_gpu
```

### macOS / Linux

```bash
python3 backend/scripts/train.py --epochs 75 --imgsz 640 --batch 8 --device 0 --name salamander_run1_gpu
```

The trained weights will be saved to:

```text
runs/detect/salamander_run1_gpu/weights/best.pt
```

---

## Single Image Inference (From Root)

Run inference on a single image.

### Windows

```powershell
python backend\scripts\infer_image.py --weights backend\models\best.pt --source backend\data\captured\ensantina\frame_0138.png
```

### macOS / Linux

```bash
python3 backend/scripts/infer_image.py --weights backend/models/best.pt --source backend/data/captured/ensantina/frame_0138.png
```

Output:

```text
backend/outputs/single_image_test.jpg
```

---

## Video Inference (From Root)

Run inference on a full video.

### Windows

```powershell
python backend\scripts\infer_video.py --weights backend\models\best.pt --source videos\ensantina.mp4 --output backend\outputs\salamander_video_test.mp4
```

### macOS / Linux

```bash
python3 backend/scripts/infer_video.py --weights backend/models/best.pt --source videos/ensantina.mp4 --output backend/outputs/salamander_video_test.mp4
```

Output:

```text
backend/outputs/salamander_video_test.mp4
```

---

## Notes

Do **not** commit generated files such as:

```text
runs/
backend/data/
backend/outputs/
*.pt
```

Share the trained model (`best.pt`) separately with teammates if needed.

## Reflection

One thing we noticed while testing was that YOLO worked much better than color masking in uncontrolled environments. In videos with background noise such as similar colors to the salamander, shadows, or textured environments, YOLO was still able to detect and track the salamander pretty well. A color masking approach would've probably struggled more in these situations since it relies heavily on matching color ranges, which could cause parts of the background to get detected if the colors were too similar to the salamander. However, color masking would still be a good option in a more controlled environment with consistent lighting and cleaner backgrounds.

If given more time, we would've like to try to implement a path trail. It was something we experimented with early on but the line drawn for the path trail wasn't the best. We would ideally find the best way to track the center mass of the salamander and then have lines drawn to follow that center mass over time.