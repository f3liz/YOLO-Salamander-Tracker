from pathlib import Path
import argparse
import cv2
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", default="backend/outputs/video_test.mp4")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    model = YOLO(args.weights)

    cap = cv2.VideoCapture(args.source)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {args.source}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = cv2.VideoWriter(
        args.output,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    frame_count = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        results = model(frame, conf=args.conf, imgsz=args.imgsz, verbose=False)
        annotated = results[0].plot()
        writer.write(annotated)

        frame_count += 1

    cap.release()
    writer.release()

    print(f"Processed {frame_count} frames")
    print(f"Saved annotated video to {args.output}")


if __name__ == "__main__":
    main()