# Terminal ASCII Video

Convert videos into animated ASCII playback directly in the terminal using Python.

The tool supports:
- Video-to-ASCII conversion
- Saved ASCII animation generation
- Replay of previously generated ASCII animations
- Configurable playback settings

## Technologies
- Python
- OpenCV
- Pillow
- NumPy

## Generate ASCII Video
```bash
python3 video_to_ascii.py generate rickroll.mp4 --cols 120 --fps 24 --detailed
```

## Replay Saved ASCII Animation
```bash
python3 video_to_ascii.py replay ascii_runs/rickroll_20260516_232221
```

## Features
- Configurable ASCII resolution
- Adjustable playback FPS
- Detailed ASCII character sets
- Automatic run folder generation
- Saved frame replay support

## Demo
<img width="400" height="233" alt="Screen Recording 2026-05-16 at 11 28 23 PM" src="https://github.com/user-attachments/assets/cd9cf0c8-3fb8-4ce3-997c-99c8e2d40b73" />


