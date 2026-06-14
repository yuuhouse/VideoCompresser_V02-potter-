# Agent Guidance for VideoCompresser_V02-potter-

## What this project is
A small video compression GUI project for Windows. It supports two code paths:
- `video_compressor_gui.py`: Python/Tkinter GUI that invokes FFmpeg for compression.
- `video_compressor_gui.cpp`: native Windows C++ GUI using Win32 APIs and FFmpeg via command execution.

## Key files
- `README.md` — primary user-facing instructions, runtime requirements, and usage commands.
- `video_compressor_gui.py` — main Python GUI implementation; preferred runtime path for day-to-day work.
- `video_compressor_gui.cpp` — alternate native C++ GUI implementation.
- `run_lazy.bat` / `run_lazy.ps1` — convenient launcher for the Python version.
- `video_compression.log` — runtime log file produced by the Python app.

## Languages and environment
- Python 3.6+ with `tkinter` and `subprocess`.
- Windows-native C++ with `g++` compile command shown in README.
- FFmpeg must be present; Python code prefers a bundled `ffmpeg.exe` beside the script or in `bin/ffmpeg.exe`, otherwise it falls back to the system `ffmpeg` command.

## Run and build commands
- Python: `python video_compressor_gui.py`
- Windows C++ compile:
  `g++ video_compressor_gui.cpp -o video_compressor_gui.exe -std=c++17 -municode -mwindows -static -static-libgcc -static-libstdc++`
- Lazy run (Python): execute `run_lazy.bat` or `run_lazy.ps1`.

## Important conventions
- The Python GUI accepts a CRF value from `0` to `51` and uses `libx265` with `-preset medium`.
- Output file names follow `originalname_YYYYMMDD_HHMMSS_compressed.ext`.
- Keep `README.md` as the source of truth for usage and environment notes.
- Logging should remain in `video_compression.log`.
- Avoid breaking the simple GUI flow: browse input file, enter CRF, compress.

## Notes for agents
- There is no formal build system or test suite in this repo.
- Changes should preserve the current user-facing behavior and runtime assumptions unless explicitly asked to improve compatibility or usability.
- Use the README for any workflow or runtime requirement details before editing behavior.
