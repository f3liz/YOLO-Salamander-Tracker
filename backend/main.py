from threading import Thread
import time
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import cv2
from ultralytics import YOLO

from collections import defaultdict

VIDEOS_DIR = Path(__file__).parent / "videos"
VIDEOS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Salamander Tracker POC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/videos", StaticFiles(directory=str(VIDEOS_DIR)), name="videos")

job = {"status": "idle"}

model = YOLO("best.pt")
print(model.names)

@app.get("/")
def root():
    return {"ok": True}


def run_track_job():
    try:
        input_path = VIDEOS_DIR / "input.mp4"
        cap = cv2.VideoCapture(str(input_path))

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"fps={fps} dims={width}x{height} frames={total}")

        output_path = VIDEOS_DIR / "output.mp4"

        writer = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*"avc1"),
            fps,
            (width, height),
        )

        frames_seen = defaultdict(int)
        label_for = {}

        region_counts = {
            "top_left": 0,
            "top_right": 0,
            "bottom_left": 0,
            "bottom_right": 0,
        }

        # Divide the screen into 4 regions
        mid_x = width // 2
        mid_y = height // 2

        for frame_idx in range(total):

            ok, frame = cap.read()

            if not ok:
                break
            result = model.track(frame, persist=True, verbose=False)[0]

            boxes = result.boxes

            if boxes is not None and boxes.id is not None:
                for box, tid, cls_id in zip(
                    boxes.xyxy.tolist(),
                    boxes.id.tolist(),
                    boxes.cls.tolist()
                ):
                    tid = int(tid)
                    frames_seen[tid] += 1
                    label_for[tid] = model.names[int(cls_id)]

                    # Get coords of box
                    x1, y1, x2, y2 = box

                    # Calculate center of box(salamander)
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    # Determine region it is in
                    # Top Left
                    if center_x < mid_x and center_y < mid_y:
                        region_counts["top_left"] += 1

                    # Top Right
                    elif center_x >= mid_x and center_y < mid_y:
                        region_counts["top_right"] += 1

                    # Bottom Left
                    elif center_x < mid_x and center_y >= mid_y:
                        region_counts["bottom_left"] += 1

                    # Bottom Right
                    else:
                        region_counts["bottom_right"] += 1

            # Vertical line
            cv2.line(
                frame,
                (mid_x, 0),
                (mid_x, height),
                (0, 255, 0),
                2
            )

            # Horizontal line
            cv2.line(
                frame,
                (0, mid_y),
                (width, mid_y),
                (0, 255, 0),
                2
            )
            annotated_frame = result.plot()

            # Draw lines onto annotated frame
            cv2.line(
                annotated_frame,
                (mid_x, 0),
                (mid_x, height),
                (0, 255, 0),
                2
            )

            cv2.line(
                annotated_frame,
                (0, mid_y),
                (width, mid_y),
                (0, 255, 0),
                2
            )

            writer.write(annotated_frame)

            job["percent"] = int((frame_idx + 1) / total * 100)

            if frame_idx % 30 == 0:
                print(f"frame {frame_idx}/{total}")

        cap.release()
        writer.release()

        tracks = [
            {
                "track_id": tid,
                "time_on_screen_s": round(count / fps, 2),
                "label": label_for[tid],
            }
            for tid, count in frames_seen.items()
        ]

        # Convert frame count into seconds
        region_times = {
            region: round(count / fps, 2)
            for region, count in region_counts.items()
        }

        job.clear()
        job["status"] = "done"
        job["percent"] = 100
        job["result"] = {
            "video_url": f"http://localhost:8000/videos/output.mp4?t={int(time.time())}",
            "tracks": tracks,
            "region_dwell_times_seconds": region_times,
        }
    except Exception as e:
        print(f"error: {e}", flush=True)
        job.clear()
        job["status"] = "error"
        job["message"] = str(e)


@app.post("/track")
def start_track(video: UploadFile = File(...)):
    (VIDEOS_DIR / "input.mp4").write_bytes(video.file.read())
    job.clear()
    job["status"] = "processing"
    job["percent"] = 0
    Thread(target=run_track_job, daemon=True).start()
    return {"status": "processing"}


@app.get("/track")
def get_track():
    return job

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)