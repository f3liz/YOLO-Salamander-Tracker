# YOLO-Salamander-Tracker

## Model Setup

Place the trained model file:

```text
best.pt
```

inside:

```text
backend/models/
```

---

## Training

Run model training:

```powershell
python scripts\train.py --epochs 75 --imgsz 640 --batch 8 --device 0 --name salamander_run1_gpu
```

---

## Single Image Inference

Run inference on a single image:

```powershell
python backend\scripts\infer_image.py --weights backend\models\best.pt --source backend\data\captured\ensantina\frame_0138.png
```

The annotated image will be saved to:

```text
backend/outputs/single_image_test.jpg
```

---

## Video Inference

Run inference on a video:

```powershell
python backend\scripts\infer_video.py --weights backend\models\best.pt --source videos\ensantina.mp4 --output backend\outputs\salamander_video_test.mp4
```

The annotated video will be saved to:

```text
backend/outputs/salamander_video_test.mp4
```
