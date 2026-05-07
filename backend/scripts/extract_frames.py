"""Extract evenly spaced frames from a video for YOLO training datasets."""

import argparse
from pathlib import Path
import cv2


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--video", required=True)
    parser.add_argument("--output-dir", default="data/captured")
    parser.add_argument("--frames", type=int, default=150)
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)

    args = parser.parse_args()

    video_path = Path(args.video)

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    video_name = video_path.stem
    output_dir = Path(args.output_dir) / video_name
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise RuntimeError("Could not open video")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # fallback if metadata is broken
    use_metadata = total > 0

    print("Video:", video_name)
    print("Saving to:", output_dir.resolve())

    saved = 0
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # decide whether to save frame
        if use_metadata:
            interval = max(total // args.frames, 1)
            should_save = frame_idx % interval == 0
        else:
            # fallback: time-based sampling
            should_save = frame_idx % 5 == 0

        if should_save:
            if args.width and args.height:
                frame = cv2.resize(frame, (args.width, args.height))

            saved += 1
            filename = f"frame_{saved:04d}.jpg"
            cv2.imwrite(str(output_dir / filename), frame)

            print(f"saved {saved}")

            if saved >= args.frames:
                break

        frame_idx += 1

    cap.release()
    print("done:", saved, "frames")