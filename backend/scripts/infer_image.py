from pathlib import Path
import argparse
import cv2
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", default="backend/outputs/single_image_test.jpg")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    model = YOLO(args.weights)

    results = model(args.source, conf=args.conf, imgsz=args.imgsz)

    annotated = results[0].plot()

    cv2.imwrite(args.output, annotated)

    print(f"Saved annotated image to {args.output}")


if __name__ == "__main__":
    main()