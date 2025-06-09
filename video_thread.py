# video_thread.py

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage
import cv2
import time
import numpy as np


class VideoThread(QThread):
    # Signals to communicate with the main UI
    update_frame = Signal(QImage)
    update_fps = Signal(str)
    update_detections = Signal(list)
    update_progress = Signal(int)

    def __init__(self, process_frame_func, parent=None):
        super().__init__(parent)
        self.process_frame = process_frame_func
        self.video_source = 0
        self.running = False
        self.is_paused = False
        self.is_video_file = False
        self.video_capture = None
        self.prev_frame = None

    def set_video_source(self, source):
        self.video_source = source
        self.is_video_file = not isinstance(source, int)

    def run(self):
        self.running = True
        self.video_capture = cv2.VideoCapture(self.video_source)

        if not self.video_capture.isOpened():
            print(f"Error: Could not open video source: {self.video_source}")
            self.running = False
            return

        total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)) if self.is_video_file else 0

        start_time = time.time()
        fps_frame_count = 0

        while self.running:
            if self.is_paused:
                self.msleep(50)  # Sleep while paused to reduce CPU usage
                continue

            ret, frame = self.video_capture.read()
            if not ret:
                break  # End of video or camera error

            # --- Frame Processing ---
            processed_frame, detections, annotated_for_email = self.process_frame(frame, self.prev_frame)
            self.prev_frame = frame

            # --- UI Updates via Signals ---
            h, w, ch = processed_frame.shape
            bytes_per_line = ch * w
            qt_frame = QImage(processed_frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            self.update_frame.emit(qt_frame)

            if detections:
                self.update_detections.emit(detections)

            # --- FPS Calculation ---
            fps_frame_count += 1
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1.0:
                fps = fps_frame_count / elapsed_time
                self.update_fps.emit(f"{fps:.1f}")
                start_time = time.time()
                fps_frame_count = 0

            # --- Video Progress ---
            if self.is_video_file and total_frames > 0:
                frame_counter = self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)
                progress = int((frame_counter / total_frames) * 100)
                self.update_progress.emit(progress)

        # Cleanup
        if self.video_capture:
            self.video_capture.release()
        self.update_progress.emit(0)  # Reset progress bar
        self.update_fps.emit("0.0")
        self.running = False

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    def stop(self):
        self.running = False
        self.wait(1000)  # Wait up to 1 second for the thread to finish cleanly

    def seek(self, position):
        """Safely seeks to a new position in the video file."""
        if self.is_video_file and self.video_capture and self.video_capture.isOpened() and self.running:
            total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames > 0:
                frame_number = int(total_frames * (position / 100))
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)