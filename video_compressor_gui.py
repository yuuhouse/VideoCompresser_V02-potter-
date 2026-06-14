import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import threading
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Configure logging with more detailed settings
logging.basicConfig(
    filename='video_compression.log',
    level=logging.INFO,  # Changed from ERROR to INFO to capture all levels
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add file handler to ensure all messages are written to file
file_handler = logging.FileHandler('video_compression.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Get the root logger and add the file handler
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)

# Determine ffmpeg executable path (prefer bundled ffmpeg.exe next to this script)
script_dir = Path(__file__).parent
ffmpeg_candidates = [script_dir / "ffmpeg.exe", script_dir / "bin" / "ffmpeg.exe"]
ffmpeg_path = None
for p in ffmpeg_candidates:
    if p.exists():
        ffmpeg_path = p
        break
if ffmpeg_path:
    FFMPEG_CMD = str(ffmpeg_path)
    logging.info(f"Using bundled ffmpeg: {FFMPEG_CMD}")
else:
    FFMPEG_CMD = "ffmpeg"
    logging.warning("Bundled ffmpeg.exe not found. Falling back to system 'ffmpeg' command.")

class VideoCompressorGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Video Compressor")
        self.window.geometry("720x520")

        # Input file
        self.input_frame = ttk.Frame(self.window)
        self.input_frame.pack(pady=10, padx=10, fill="x")

        self.input_label = ttk.Label(self.input_frame, text="Input File:")
        self.input_label.pack(side="left")

        self.input_path = tk.StringVar()
        self.input_entry = ttk.Entry(self.input_frame, textvariable=self.input_path)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))

        self.input_button = ttk.Button(self.input_frame, text="Browse", command=self.select_input_file)
        self.input_button.pack(side="right")

        # CRF Value
        self.crf_frame = ttk.Frame(self.window)
        self.crf_frame.pack(pady=10, padx=10)

        self.crf_label = ttk.Label(self.crf_frame, text="CRF Value (0-51):")
        self.crf_label.pack(side="left")

        self.crf_value = tk.StringVar(value="28")
        self.crf_entry = ttk.Entry(self.crf_frame, textvariable=self.crf_value, width=5)
        self.crf_entry.pack(side="left", padx=5)

        # Compress button
        self.compress_button = ttk.Button(self.window, text="Compress", command=self.compress_video)
        self.compress_button.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(self.window, text="Ready to compress.")
        self.status_label.pack(pady=(0, 10))

        # Real-time log output
        self.output_frame = ttk.Frame(self.window)
        self.output_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        self.output_text = tk.Text(self.output_frame, height=14, wrap="none", state="disabled")
        self.output_text.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.output_frame, orient="vertical", command=self.output_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=self.scrollbar.set)

    def select_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Input Video",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)

    def append_output(self, message: str):
        self.output_text.config(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")

    def set_status(self, message: str):
        self.status_label.config(text=message)

    def log_message(self, message: str):
        logging.info(message)
        self.window.after(0, lambda: self.append_output(message))

    def clear_output(self):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")

    def compress_video(self):
        input_path = self.input_path.get().strip()
        if not input_path:
            self.set_status("Please select input file")
            logging.error("Compression failed: No input file selected.")
            return

        try:
            input_file = Path(input_path)
            if not input_file.exists():
                raise FileNotFoundError(f"Input file does not exist: {input_path}")
            if not input_file.is_file():
                raise ValueError(f"Selected path is not a file: {input_path}")

            supported_extensions = {".mp4", ".avi", ".mkv", ".mov"}
            if input_file.suffix.lower() not in supported_extensions:
                raise ValueError(f"Unsupported file type: {input_file.suffix}. Supported types: {', '.join(sorted(supported_extensions))}")

            crf_text = self.crf_value.get().strip()
            if not crf_text:
                raise ValueError("Please enter a CRF value")
            if not crf_text.isdigit():
                raise ValueError("CRF value must be an integer between 0 and 51")
            crf_value = int(crf_text)
            if crf_value < 0 or crf_value > 51:
                raise ValueError("CRF value must be between 0 and 51")

            if FFMPEG_CMD == "ffmpeg" and shutil.which("ffmpeg") is None:
                raise FileNotFoundError("FFmpeg executable not found. Please install FFmpeg or place ffmpeg.exe next to this script.")
            if FFMPEG_CMD != "ffmpeg" and not Path(FFMPEG_CMD).exists():
                raise FileNotFoundError(f"Bundled FFmpeg not found at: {FFMPEG_CMD}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = input_file.parent / f"{input_file.stem}_{timestamp}_compressed{input_file.suffix}"

            self.clear_output()
            self.set_status("Starting compression...")
            self.compress_button.config(state="disabled")
            self.input_button.config(state="disabled")

            compression_thread = threading.Thread(
                target=self.run_compression,
                args=(input_path, str(output_path), crf_value),
                daemon=True
            )
            compression_thread.start()
        except Exception as e:
            self.set_status(f"Error: {e}")
            logging.error(f"Exception occurred preparing compression: {e}", exc_info=True)

    def read_stream(self, stream, prefix=""):
        if stream is None:
            return
        for line in iter(stream.readline, ""):
            line = line.rstrip()
            if line:
                self.log_message(f"{prefix}{line}")
        stream.close()

    def run_compression(self, input_path: str, output_path: str, crf_value: int):
        try:
            input_file = Path(input_path)
            input_size = input_file.stat().st_size / (1024 * 1024)
            self.log_message(f"Input file: {input_path}")
            self.log_message(f"Input size: {input_size:.2f} MB")

            probe_command = [
                FFMPEG_CMD, '-v', 'error', '-i', input_path, '-f', 'null', '-'
            ]
            probe_result = subprocess.run(
                probe_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if probe_result.returncode != 0:
                raise RuntimeError(f"Input file validation failed: {probe_result.stderr.strip()}")
            if probe_result.stderr:
                self.log_message(f"[WARN] Video file issues detected: {probe_result.stderr.strip()}")

            command = [
                FFMPEG_CMD, '-i', input_path,
                '-c:v', 'libx265',
                '-crf', str(crf_value),
                '-preset', 'medium',
                output_path
            ]
            self.log_message(f"Executing command: {' '.join(command)}")

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )

            stdout_thread = threading.Thread(target=self.read_stream, args=(process.stdout, ""), daemon=True)
            stderr_thread = threading.Thread(target=self.read_stream, args=(process.stderr, "[ERR] "), daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            process.wait()
            stdout_thread.join()
            stderr_thread.join()

            if process.returncode == 0:
                output_size = Path(output_path).stat().st_size / (1024 * 1024)
                compression_ratio = (input_size - output_size) / input_size * 100
                result_message = (
                    f"Compression successful!\n"
                    f"Output size: {output_size:.2f} MB\n"
                    f"Saved as: {Path(output_path).name}"
                )
                self.window.after(0, lambda: self.set_status(result_message))
                self.log_message(f"Compression completed for {input_path}")
                self.log_message(f"Output size: {output_size:.2f} MB")
                self.log_message(f"Compression ratio: {compression_ratio:.2f}%")
                if output_size > input_size:
                    self.log_message(f"[WARN] Output file is larger than input file: {output_path}")
                if compression_ratio < 5:
                    self.log_message(f"[WARN] Low compression ratio ({compression_ratio:.2f}%) achieved")
            else:
                error_message = "Error: Compression failed"
                self.window.after(0, lambda: self.set_status(error_message))
                self.log_message(f"Compression failed for {input_path}")
                self.log_message(f"[ERR] FFmpeg exited with code {process.returncode}")
        except Exception as e:
            self.window.after(0, lambda: self.set_status(f"Error: {e}"))
            logging.error(f"Exception occurred during compression: {e}", exc_info=True)
            self.log_message(f"[ERR] Exception: {e}")
        finally:
            self.window.after(0, lambda: self.compress_button.config(state="normal"))
            self.window.after(0, lambda: self.input_button.config(state="normal"))

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = VideoCompressorGUI()
    app.run()