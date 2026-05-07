"""
Extract exactly N evenly spaced frames from a video using ffmpeg.

Usage:
    python scripts/capture.py --video ../videos/ensantina.mp4

Optional:
    python scripts/capture.py --video ../videos/ensantina.mp4 --frames 150 --output data/captured
"""

import argparse
import subprocess
from pathlib import Path


def extract_exact_frames(video_path: str, output_folder: str, num_frames: int):
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # Get total frame count using ffprobe
    probe_cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-count_packets",
        "-show_entries", "stream=nb_read_packets",
        "-of", "csv=p=0",
        video_path
    ]

    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    try:
        total_frames = int(result.stdout.strip())
    except:
        total_frames = None

    if not total_frames or total_frames <= 0:
        raise RuntimeError("Could not determine frame count from video.")

    # Compute evenly spaced frame indices
    step = total_frames / num_frames
    indices = [int(i * step) for i in range(num_frames)]

    print(f"Total frames in video: {total_frames}")
    print(f"Extracting {num_frames} evenly spaced frames...")

    for i, frame_idx in enumerate(indices):
        output_file = output_path / f"frame_{i+1:04d}.png"

        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vf", f"select=eq(n\\,{frame_idx})",
            "-vframes", "1",
            str(output_file)
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"[{i+1}/{num_frames}] saved frame {frame_idx}")

    print(f"Done. Saved {num_frames} frames to {output_path.resolve()}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--video", required=True)
    parser.add_argument("--output", default="data/captured")
    parser.add_argument("--frames", type=int, default=150)

    args = parser.parse_args()

    video_path = Path(args.video)

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    extract_exact_frames(
        str(video_path),
        args.output,
        args.frames
    )


if __name__ == "__main__":
    main()