import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
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

class VideoCompressorGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Video Compressor")
        self.window.geometry("600x200")  # Adjusted height since output selection is removed

        # Input file
        self.input_frame = ttk.Frame(self.window)
        self.input_frame.pack(pady=10, padx=10, fill="x")

        self.input_label = ttk.Label(self.input_frame, text="Input File:")
        self.input_label.pack(side="left")

        self.input_path = tk.StringVar()
        self.input_entry = ttk.Entry(self.input_frame, textvariable=self.input_path)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(5,5))

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
        self.compress_button.pack(pady=20)

        # Status
        self.status_label = ttk.Label(self.window, text="")
        self.status_label.pack(pady=10)

    def select_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Input Video",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)

    def compress_video(self):
        input_path = self.input_path.get()
        if not input_path:
            self.status_label.config(text="Please select input file")
            logging.error("Compression failed: No input file selected.")
            return

        # Generate output filename with timestamp
        input_file = Path(input_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = input_file.parent / f"{input_file.stem}_{timestamp}_compressed{input_file.suffix}"

        try:
            # Check input file size and log it
            input_size = input_file.stat().st_size / (1024 * 1024)
            logging.info(f"Input file: {input_path}")
            logging.info(f"Input size: {input_size:.2f} MB")

            # Check video file validity
            probe_command = [
                'ffmpeg', '-v', 'error', '-i', input_path, '-f', 'null', '-'
            ]
            probe_result = subprocess.run(
                probe_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if probe_result.stderr:
                logging.warning(f"Video file issues detected: {probe_result.stderr}")

            command = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx265',
                '-crf', self.crf_value.get(),
                '-preset', 'medium',
                str(output_path)
            ]

            logging.info(f"Executing command: {' '.join(command)}")

            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if process.returncode == 0:
                output_size = output_path.stat().st_size / (1024 * 1024)
                compression_ratio = (input_size - output_size) / input_size * 100
                
                status_text = f"Compression successful!\nOutput size: {output_size:.2f} MB\nSaved as: {output_path.name}"
                self.status_label.config(text=status_text)
                
                # Log detailed compression results
                logging.info(f"Compression completed for {input_path}")
                logging.info(f"Input size: {input_size:.2f} MB")
                logging.info(f"Output size: {output_size:.2f} MB")
                logging.info(f"Compression ratio: {compression_ratio:.2f}%")
                
                # Log warnings if compression result is unusual
                if output_size > input_size:
                    logging.warning(f"Output file is larger than input file: {output_path}")
                if compression_ratio < 5:
                    logging.warning(f"Low compression ratio ({compression_ratio:.2f}%) achieved")
                
                # Log any FFmpeg warnings
                if process.stderr:
                    logging.warning(f"FFmpeg warnings during compression: {process.stderr}")
            else:
                self.status_label.config(text="Error: Compression failed")
                logging.error(f"Compression failed for {input_path}")
                logging.error(f"FFmpeg Error: {process.stderr}")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            logging.error(f"Exception occurred during compression: {e}")
            if hasattr(e, '__traceback__'):
                logging.error(f"Traceback: ", exc_info=True)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = VideoCompressorGUI()
    app.run()