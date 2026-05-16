import argparse
import os
import time
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm


GSCALE_DETAILED = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
GSCALE_SIMPLE = "@%#*+=-:. "


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def create_run_folder(base_dir: str, video_path: str) -> Path:
    video_name = Path(video_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_dir = Path(base_dir) / f"{video_name}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    return run_dir


def save_metadata(run_dir: Path, fps: float):
    metadata_path = run_dir / "metadata.txt"

    with open(metadata_path, "w") as f:
        f.write(f"fps={fps}\n")


def load_metadata(run_dir: Path):
    metadata_path = run_dir / "metadata.txt"

    fps = 24

    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            for line in f:
                if line.startswith("fps="):
                    fps = float(line.strip().split("=")[1])

    return fps


def frame_to_ascii(frame, cols: int, scale: float, detailed: bool) -> str:
    image = Image.fromarray(
        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    ).convert("L")

    width, height = image.size

    tile_width = width / cols
    tile_height = tile_width / scale

    rows = int(height / tile_height)

    gscale = GSCALE_DETAILED if detailed else GSCALE_SIMPLE
    max_index = len(gscale) - 1

    ascii_rows = []

    for row in range(rows):

        y1 = int(row * tile_height)
        y2 = int((row + 1) * tile_height)

        if row == rows - 1:
            y2 = height

        ascii_row = ""

        for col in range(cols):

            x1 = int(col * tile_width)
            x2 = int((col + 1) * tile_width)

            if col == cols - 1:
                x2 = width

            tile = image.crop((x1, y1, x2, y2))

            avg_luminance = np.average(np.array(tile))

            char_index = int(
                (avg_luminance * max_index) / 255
            )

            ascii_row += gscale[char_index]

        ascii_rows.append(ascii_row)

    return "\n".join(ascii_rows)


def generate_ascii_video(
    video_path: str,
    cols: int,
    scale: float,
    fps: float,
    detailed: bool,
    output_dir: str,
    frame_gap: int,
):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise FileNotFoundError(
            f"Could not open video file: {video_path}"
        )

    run_dir = create_run_folder(output_dir, video_path)

    save_metadata(run_dir, fps)

    frame_index = 0
    ascii_index = 0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    estimated_frames = max(1, total_frames // frame_gap)

    progress = tqdm(
        total=estimated_frames,
        desc="Generating ASCII frames",
        unit="frame"
    )

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_index % frame_gap != 0:
            frame_index += 1
            continue

        ascii_frame = frame_to_ascii(
            frame,
            cols,
            scale,
            detailed
        )

        frame_file = run_dir / f"frame_{ascii_index:05d}.txt"

        frame_file.write_text(
            ascii_frame,
            encoding="utf-8"
        )

        progress.update(1)

        frame_index += 1
        ascii_index += 1

    progress.close()

    cap.release()

    print("\nASCII video generation complete.")
    print(f"Saved to: {run_dir}")


def replay_ascii_video(run_dir: str, fps_override=None):
    run_path = Path(run_dir)

    if not run_path.exists():
        raise FileNotFoundError(
            f"Run directory not found: {run_dir}"
        )

    fps = (
        fps_override
        if fps_override is not None
        else load_metadata(run_path)
    )

    delay = 1 / fps

    frames = sorted(
        run_path.glob("frame_*.txt")
    )

    if not frames:
        raise ValueError(
            "No ASCII frames found in directory."
        )

    while True:
        for frame_file in frames:

            clear_terminal()

            with open(frame_file, "r", encoding="utf-8") as f:
                print(f.read())

            time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(
        description="ASCII terminal video generator and player."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # GENERATE

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate ASCII frames from a video."
    )

    generate_parser.add_argument(
        "video",
        help="Input video file."
    )

    generate_parser.add_argument(
        "--cols",
        type=int,
        default=100,
        help="ASCII output width."
    )

    generate_parser.add_argument(
        "--scale",
        type=float,
        default=0.43,
        help="Aspect ratio correction."
    )

    generate_parser.add_argument(
        "--fps",
        type=float,
        default=24,
        help="Playback FPS metadata."
    )

    generate_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Use detailed ASCII charset."
    )

    generate_parser.add_argument(
        "--output-dir",
        default="ascii_runs",
        help="Folder for generated ASCII runs."
    )

    generate_parser.add_argument(
        "--frame-gap",
        type=int,
        default=1,
        help="Process every Nth frame."
    )

    # REPLAY

    replay_parser = subparsers.add_parser(
        "replay",
        help="Replay a saved ASCII animation."
    )

    replay_parser.add_argument(
        "run_dir",
        help="Directory containing saved ASCII frames."
    )

    replay_parser.add_argument(
        "--fps",
        type=float,
        default=None,
        help="Override playback FPS."
    )

    args = parser.parse_args()

    if args.command == "generate":
        generate_ascii_video(
            video_path=args.video,
            cols=args.cols,
            scale=args.scale,
            fps=args.fps,
            detailed=args.detailed,
            output_dir=args.output_dir,
            frame_gap=args.frame_gap,
        )

    elif args.command == "replay":
        replay_ascii_video(
            run_dir=args.run_dir,
            fps_override=args.fps
        )


if __name__ == "__main__":
    main()
