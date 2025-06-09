# ui_main_window.py

import sys
import os
import cv2
import datetime
import threading
import smtplib
import ssl
import winsound
import pandas as pd
from email.message import EmailMessage

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTabWidget, QFileDialog, QComboBox, QCheckBox,
                               QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                               QMessageBox, QProgressBar, QSlider, QFrame, QFormLayout,
                               QGroupBox)
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtCore import Qt, Slot, QTimer, QThread, Signal

import torch
from ultralytics import YOLO
import qtawesome as qta

from video_thread import VideoThread
from email_templates import EMAIL_TEMPLATES


# ===================================================================
# THREAD FOR LOADING MODELS IN THE BACKGROUND
# ===================================================================
class ModelLoaderThread(QThread):
    models_loaded = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, model_paths, parent=None):
        super().__init__(parent)
        self.model_paths = model_paths

    def run(self):
        try:
            models = {}
            print("Background thread: Starting model loading...")
            for model_name, path in self.model_paths.items():
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Model path does not exist for '{model_name}': {path}")

                if model_name == "fire":
                    print(f"Loading YOLOv5 model: {model_name}")
                    models[model_name] = torch.hub.load('ultralytics/yolov5', 'custom', path=path, force_reload=True)
                    models[model_name].conf = 0.5
                else:
                    print(f"Loading YOLOv8 model: {model_name}")
                    models[model_name] = YOLO(path)

            print("Background thread: All models loaded successfully.")
            self.models_loaded.emit(models)
        except Exception as e:
            error_str = f"Error loading models: {e}"
            print(error_str)
            self.error_occurred.emit(error_str)


# ===================================================================
# MAIN WINDOW
# ===================================================================
class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle(f"Intelligent Video Surveillance System - Logged in as {self.user_data['username']}")
        self.showFullScreen()

        self.models = {}
        self.models_loaded_status = False
        self.alert_flags = {"weapon": False, "fire": False, "accident": False}
        self.video_thread = None
        self.current_video_source = "None"
        self.log_files = {"detection": "logs/detection_log.csv", "email": "logs/email_log.csv"}

        self.init_logs()
        self.setup_ui()
        self.load_logs_to_ui()
        self.start_model_loading()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        top_bar_layout = QHBoxLayout()
        title_label = QLabel("Surveillance Dashboard")
        title_label.setObjectName("title_label")
        user_label = QLabel(f"👤 {self.user_data['username']}")
        self.mode_label = QLabel("Mode: Indoor")
        self.fps_label = QLabel("FPS: 0.0")
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.mode_label)
        top_bar_layout.addWidget(self.fps_label)
        top_bar_layout.addWidget(user_label)
        main_layout.addLayout(top_bar_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.create_surveillance_tab()
        self.create_settings_tab()
        self.create_analytics_tab()
        self.create_help_tab()

    def create_surveillance_tab(self):
        surveillance_widget = QWidget()
        layout = QHBoxLayout(surveillance_widget)

        video_layout = QVBoxLayout()
        self.video_display_label = QLabel("Please start a video source from the controls.")
        self.video_display_label.setObjectName("video_display_label")
        self.video_display_label.setAlignment(Qt.AlignCenter)
        self.video_display_label.setMinimumSize(800, 600)
        video_layout.addWidget(self.video_display_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.video_slider = QSlider(Qt.Horizontal)
        self.video_slider.setVisible(False)
        self.video_slider.sliderReleased.connect(self.seek_video)
        video_layout.addWidget(self.progress_bar)
        video_layout.addWidget(self.video_slider)

        layout.addLayout(video_layout, 7)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)
        controls_layout.setAlignment(Qt.AlignTop)

        src_group = QGroupBox("Video Source")
        src_group_layout = QVBoxLayout(src_group)
        self.webcam_combo = QComboBox()
        self.populate_webcams()
        src_group_layout.addWidget(self.webcam_combo)
        self.start_webcam_btn = QPushButton(qta.icon("fa5s.video"), " Start Webcam")
        self.start_webcam_btn.clicked.connect(self.start_webcam)
        src_group_layout.addWidget(self.start_webcam_btn)
        self.open_video_btn = QPushButton(qta.icon("fa5s.folder-open"), " Open Video File")
        self.open_video_btn.clicked.connect(self.open_video_file)
        src_group_layout.addWidget(self.open_video_btn)
        controls_layout.addWidget(src_group)

        playback_group = QGroupBox("Playback Controls")
        playback_group_layout = QVBoxLayout(playback_group)
        self.pause_play_btn = QPushButton(qta.icon("fa5s.pause"), " Pause")
        self.pause_play_btn.clicked.connect(self.toggle_pause_play)
        playback_group_layout.addWidget(self.pause_play_btn)
        self.stop_btn = QPushButton(qta.icon("fa5s.stop-circle"), " Stop Video")
        self.stop_btn.clicked.connect(self.stop_video)
        playback_group_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(playback_group)

        status_group = QGroupBox("Live Status")
        status_form_layout = QFormLayout(status_group)
        self.current_source_label = QLabel("None")
        self.current_source_label.setWordWrap(True)
        status_form_layout.addRow("Source:", self.current_source_label)
        self.detection_label = QLabel("None")
        self.detection_label.setObjectName("status_label")
        self.detection_label.setWordWrap(True)
        status_form_layout.addRow("Detections:", self.detection_label)
        controls_layout.addWidget(status_group)

        controls_layout.addStretch(5)
        layout.addLayout(controls_layout, 3)

        self.tabs.addTab(surveillance_widget, qta.icon("fa5s.tv"), "Surveillance")

    def create_settings_tab(self):
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setAlignment(Qt.AlignTop)

        profile_group = QGroupBox("User Profile")
        profile_layout = QFormLayout(profile_group)
        profile_layout.addRow("Username:", QLabel(self.user_data['username']))
        profile_layout.addRow("Email:", QLabel(self.user_data['email']))
        self.logout_btn = QPushButton(qta.icon("fa5s.sign-out-alt"), " Logout")
        self.logout_btn.clicked.connect(self.handle_logout)
        profile_layout.addRow(self.logout_btn)
        layout.addWidget(profile_group)

        mode_group = QGroupBox("Detection Mode")
        mode_layout = QVBoxLayout(mode_group)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Indoor", "Outdoor", "Custom"])
        self.mode_combo.currentTextChanged.connect(self.update_mode_and_models)
        mode_layout.addWidget(self.mode_combo)
        layout.addWidget(mode_group)

        self.model_group = QGroupBox("Model Selection")
        self.model_checkbox_layout = QVBoxLayout(self.model_group)
        self.model_group.setEnabled(False)
        layout.addWidget(self.model_group)

        alert_group = QGroupBox("Alert Configuration")
        alert_layout = QVBoxLayout(alert_group)
        self.enable_sound_check = QCheckBox("Enable Sound Alerts")
        self.enable_sound_check.setChecked(True)
        alert_layout.addWidget(self.enable_sound_check)
        self.user_email_input = QLineEdit(self.user_data['email'])
        self.user_email_input.setPlaceholderText("Enter alert email address")
        email_form = QFormLayout()
        email_form.addRow("Send Email Alerts To:", self.user_email_input)
        alert_layout.addLayout(email_form)
        layout.addWidget(alert_group)

        layout.addStretch()
        self.tabs.addTab(settings_widget, qta.icon("fa5s.cog"), "Settings")

    def create_analytics_tab(self):
        analytics_widget = QWidget()
        layout = QVBoxLayout(analytics_widget)
        log_tabs = QTabWidget()
        self.detection_log_table = QTableWidget()
        self.detection_log_table.setColumnCount(3)
        self.detection_log_table.setHorizontalHeaderLabels(["Timestamp", "Detection Type", "Details"])
        self.detection_log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        log_tabs.addTab(self.detection_log_table, qta.icon("fa5s.history"), "Detection Log")
        self.email_log_table = QTableWidget()
        self.email_log_table.setColumnCount(4)
        self.email_log_table.setHorizontalHeaderLabels(["Timestamp", "Alert Type", "Recipient", "Status"])
        self.email_log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        log_tabs.addTab(self.email_log_table, qta.icon("fa5s.envelope"), "Email Alert Log")
        layout.addWidget(log_tabs)
        self.tabs.addTab(analytics_widget, qta.icon("fa5s.chart-bar"), "Analytics")

    def create_help_tab(self):
        help_widget = QWidget()
        layout = QVBoxLayout(help_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        help_text = """
        <h2>Help & About</h2>
        <p>Welcome to the Intelligent Video Surveillance System.</p>

        <h3>Tabs Guide:</h3>
        <ul>
            <li><b>Surveillance:</b> The main dashboard for viewing live or recorded video feeds. Use the controls on the right to start/stop video sources.</li>
            <li><b>Settings:</b> Configure the system. Choose between Indoor/Outdoor modes, enable or disable specific detection models, and set up email alerts.</li>
            <li><b>Analytics:</b> Review past events. This section contains detailed logs of all detections and email alerts sent by the system.</li>
        </ul>

        <h3>Contact:</h3>
        <p>For support, please contact the system administrator.</p>
        <p><i>Version 1.2</i></p>
        """
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setTextFormat(Qt.RichText)
        help_label.setAlignment(Qt.AlignTop)
        layout.addWidget(help_label)
        self.tabs.addTab(help_widget, qta.icon("fa5s.question-circle"), "Help")

    def start_model_loading(self):
        self.update_control_buttons(running=False, loading=True)
        self.video_display_label.setText("⏳ Loading AI Models, please wait...")
        model_paths = {
            "weapon": "Weapon.pt",
            "fire": "firedetectionmodel.pt",
            "accident": "Accident.pt",
            "object": "objectdetectionmodel.pt"
       }
        self.model_loader_thread = ModelLoaderThread(model_paths)
        self.model_loader_thread.models_loaded.connect(self.on_models_loaded)
        self.model_loader_thread.error_occurred.connect(self.on_model_error)
        self.model_loader_thread.start()

    @Slot(dict)
    def on_models_loaded(self, models):
        self.models = models
        self.models_loaded_status = True
        print("Main UI: Models loaded and assigned.")
        self.video_display_label.setText("✅ Models loaded successfully.\nPlease start a video source.")

        self.model_checkboxes = {}
        for model_name in self.models.keys():
            self.model_checkboxes[model_name] = QCheckBox(model_name.capitalize())
            self.model_checkbox_layout.addWidget(self.model_checkboxes[model_name])

        self.model_group.setEnabled(True)
        self.update_mode_and_models(self.mode_combo.currentText())
        self.update_control_buttons(running=False, loading=False)

    @Slot(str)
    def on_model_error(self, error_msg):
        self.video_display_label.setText(f"❌ {error_msg}")
        QMessageBox.critical(self, "Model Loading Error", error_msg)
        self.update_control_buttons(running=False, loading=True)

    def process_frame(self, frame, prev_frame):
        processed = frame.copy()
        annotated_for_email = frame.copy()
        detections = []
        if not self.models_loaded_status:
            return processed, detections, annotated_for_email

        active_models = self.get_active_models()

        if "fire" in active_models and "fire" in self.models:
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.models["fire"](rgb_frame, size=640)
                for det in results.pred[0]:
                    if det[4] > self.models["fire"].conf:
                        x1, y1, x2, y2 = map(int, det[:4])
                        cv2.rectangle(processed, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.rectangle(annotated_for_email, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(processed, "Fire", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                        cv2.putText(annotated_for_email, "Fire", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                    (0, 0, 255), 2)
                        detections.append("Fire")
                        if not self.alert_flags["fire"]:
                            self.alert_flags["fire"] = True
                            self.handle_alert("fire", annotated_for_email)
            except Exception as e:
                print(f"Fire detection error: {e}")

        if "accident" in active_models and "accident" in self.models:
            results = self.models["accident"](frame, stream=True, verbose=False)
            for result in results:
                for box in result.boxes:
                    if box.conf[0] > 0.5:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(processed, (x1, y1), (x2, y2), (255, 200, 0), 2)
                        cv2.rectangle(annotated_for_email, (x1, y1), (x2, y2), (255, 200, 0), 2)
                        cv2.putText(processed, "Accident", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 200, 0),
                                    2)
                        cv2.putText(annotated_for_email, "Accident", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                    (255, 200, 0), 2)
                        detections.append("Accident")
                        if not self.alert_flags["accident"]:
                            self.alert_flags["accident"] = True
                            self.handle_alert("accident", annotated_for_email)

        if "weapon" in active_models and "weapon" in self.models:
            results = self.models["weapon"](frame, verbose=False)
            for r in results:
                for box in r.boxes:
                    if box.conf[0] >= 0.4:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        label = r.names[int(box.cls[0])]
                        conf = box.conf[0]
                        cv2.rectangle(processed, (x1, y1), (x2, y2), (0, 100, 255), 2)
                        cv2.rectangle(annotated_for_email, (x1, y1), (x2, y2), (0, 100, 255), 2)
                        cv2.putText(processed, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                    (0, 100, 255), 2)
                        cv2.putText(annotated_for_email, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.9, (0, 100, 255), 2)
                        detections.append(label)
                        if not self.alert_flags["weapon"]:
                            self.alert_flags["weapon"] = True
                            self.handle_alert("weapon", annotated_for_email)

        if "object" in active_models and "object" in self.models:
            results = self.models["object"](frame, verbose=False)
            processed = results[0].plot(img=processed)
            annotated_for_email = results[0].plot(img=annotated_for_email)
            for r in results:
                for box in r.boxes:
                    detections.append(r.names[int(box.cls[0])])

        return processed, detections, annotated_for_email

    def handle_alert(self, alert_type, frame):
        timestamp = datetime.datetime.now()
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        if self.enable_sound_check.isChecked(): self.play_beep()
        self.add_log_entry("detection",
                           [timestamp_str, alert_type.capitalize(), f"Source: {self.current_video_source}"])

        filename = f"logs/{alert_type}_alert_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(filename, frame)

        threading.Thread(
            target=self.send_email_alert,
            args=(alert_type, filename, timestamp_str, self.current_video_source),
            daemon=True
        ).start()

    def send_email_alert(self, detection_type, frame_path, timestamp, source):
        recipient_email = self.user_email_input.text()
        if not recipient_email: return

        SMTP_SERVER, SMTP_PORT = "smtp.gmail.com", 465
        SENDER_EMAIL = "intelligentvideosurveillance@gmail.com"  # ⚠️ YOUR SENDER EMAIL HERE
        APP_PASSWORD = "istnvxdlmxhkflak"  # ⚠️ YOUR GMAIL APP PASSWORD HERE

        try:
            msg = EmailMessage()
            msg["Subject"] = f"❗ {detection_type.capitalize()} Detection Alert!"
            msg["From"] = SENDER_EMAIL
            msg["To"] = recipient_email

            html_content = EMAIL_TEMPLATES.get(detection_type, "<p>An alert was triggered.</p>").format(
                timestamp=timestamp, source=source)
            msg.add_alternative(html_content, subtype="html")

            with open(frame_path, "rb") as f:
                img_data = f.read()
                msg.add_attachment(img_data, maintype='image', subtype='jpeg', cid='<detection_img>')

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.send_message(msg)

            print(f"✅ Email sent successfully to {recipient_email}")
            self.add_log_entry("email", [timestamp, detection_type.capitalize(), recipient_email, "Success"])
        except Exception as e:
            print(f"❌ Email send failed: {e}")
            self.add_log_entry("email", [timestamp, detection_type.capitalize(), recipient_email, f"Failed: {e}"])

    @Slot(QImage)
    def update_frame(self, frame):
        pixmap = QPixmap.fromImage(frame)
        self.video_display_label.setPixmap(
            pixmap.scaled(self.video_display_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    @Slot(str)
    def update_fps(self, fps_str):
        self.fps_label.setText(f"FPS: {fps_str}")

    @Slot(list)
    def update_detections(self, detections):
        self.detection_label.setText(f"{', '.join(sorted(list(set(detections))))}" if detections else "None")

    @Slot(int)
    def update_progress(self, value):
        if not self.video_slider.isSliderDown():
            self.video_slider.setValue(value)
        self.progress_bar.setValue(value)

    def seek_video(self):
        if self.video_thread:
            self.video_thread.seek(self.video_slider.value())

    def start_webcam(self):
        webcam_index = self.webcam_combo.currentData()
        if webcam_index is None:
            QMessageBox.warning(self, "Webcam Error", "No webcam selected or available.")
            return
        self.start_video(webcam_index)
        self.current_video_source = self.webcam_combo.currentText()
        self.current_source_label.setText(self.current_video_source)

    def open_video_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi *.mov *.mkv)")
        if filepath:
            self.start_video(filepath)
            self.current_video_source = os.path.basename(filepath)
            self.current_source_label.setText(self.current_video_source)

    def start_video(self, source):
        if not self.models_loaded_status:
            QMessageBox.warning(self, "Models Not Ready", "The AI models are still loading.")
            return
        if self.video_thread and self.video_thread.isRunning():
            self.stop_video()
        self.reset_alerts()
        self.video_thread = VideoThread(self.process_frame)
        self.video_thread.set_video_source(source)
        self.video_thread.update_frame.connect(self.update_frame)
        self.video_thread.update_fps.connect(self.update_fps)
        self.video_thread.update_detections.connect(self.update_detections)
        self.video_thread.update_progress.connect(self.update_progress)
        is_video_file = isinstance(source, str)
        self.progress_bar.setVisible(is_video_file)
        self.video_slider.setVisible(is_video_file)
        self.video_thread.start()
        self.update_control_buttons(running=True)

    def stop_video(self):
        if self.video_thread:
            self.video_thread.stop()
        self.video_display_label.setText("Video stopped. Please select a new source.")
        self.video_display_label.repaint()
        self.update_control_buttons(running=False)
        self.current_source_label.setText("None")
        self.detection_label.setText("None")
        self.fps_label.setText("FPS: 0.0")

    def toggle_pause_play(self):
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.toggle_pause()
            if self.video_thread.is_paused:
                self.pause_play_btn.setText(" Play");
                self.pause_play_btn.setIcon(qta.icon("fa5s.play"))
            else:
                self.pause_play_btn.setText(" Pause");
                self.pause_play_btn.setIcon(qta.icon("fa5s.pause"))

    def update_control_buttons(self, running, loading=False):
        is_ready = self.models_loaded_status and not loading
        self.start_webcam_btn.setEnabled(is_ready and not running)
        self.open_video_btn.setEnabled(is_ready and not running)
        self.pause_play_btn.setEnabled(is_ready and running)
        self.stop_btn.setEnabled(is_ready and running)

    def update_mode_and_models(self, mode):
        self.mode_label.setText(f"Mode: {mode}")
        if not self.models_loaded_status: return

        is_custom = (mode == "Custom")
        self.model_group.setEnabled(is_custom)

        if not is_custom:
            for name, checkbox in self.model_checkboxes.items():
                if mode == "Indoor":
                    checkbox.setChecked(name != "accident")
                elif mode == "Outdoor":
                    checkbox.setChecked(True)

        self.reset_alerts()

    def handle_logout(self):
        self.stop_video()
        self.logout_requested.emit()
        self.close()

    def get_active_models(self):
        if not self.models_loaded_status: return []
        return [name for name, cb in self.model_checkboxes.items() if cb.isChecked()]

    def reset_alerts(self):
        self.alert_flags = {key: False for key in self.alert_flags}
        QTimer.singleShot(10000, self.reset_alerts)

    def play_beep(self):
        try:
            winsound.PlaySound("beep.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Could not play sound: {e}")

    def populate_webcams(self):
        self.webcam_combo.clear()
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                self.webcam_combo.addItem(f"Webcam {i}", i)
                cap.release()
        if self.webcam_combo.count() == 0:
            self.webcam_combo.addItem("No Webcams Found", None)
            self.webcam_combo.setEnabled(False)

    def init_logs(self):
        os.makedirs("logs", exist_ok=True)
        if not os.path.exists(self.log_files["detection"]):
            pd.DataFrame(columns=["Timestamp", "Type", "Details"]).to_csv(self.log_files["detection"], index=False)
        if not os.path.exists(self.log_files["email"]):
            pd.DataFrame(columns=["Timestamp", "Type", "Recipient", "Status"]).to_csv(self.log_files["email"],
                                                                                      index=False)

    def add_log_entry(self, log_type, data):
        file_path = self.log_files[log_type]
        df = pd.DataFrame([data])
        df.to_csv(file_path, mode='a', header=False, index=False)

        table = self.detection_log_table if log_type == "detection" else self.email_log_table
        row_position = table.rowCount()
        table.insertRow(row_position)
        for i, item in enumerate(data):
            table.setItem(row_position, i, QTableWidgetItem(str(item)))

    def load_logs_to_ui(self):
        try:
            det_df = pd.read_csv(self.log_files["detection"])
            self.detection_log_table.setRowCount(0)  # Clear table before loading
            for i, row in det_df.iterrows():
                row_position = self.detection_log_table.rowCount()
                self.detection_log_table.insertRow(row_position)
                for j, item in enumerate(row):
                    self.detection_log_table.setItem(row_position, j, QTableWidgetItem(str(item)))

            email_df = pd.read_csv(self.log_files["email"])
            self.email_log_table.setRowCount(0)  # Clear table before loading
            for i, row in email_df.iterrows():
                row_position = self.email_log_table.rowCount()
                self.email_log_table.insertRow(row_position)
                for j, item in enumerate(row):
                    self.email_log_table.setItem(row_position, j, QTableWidgetItem(str(item)))
        except Exception as e:
            print(f"Could not load log files: {e}")

    def closeEvent(self, event):
        self.stop_video()
        event.accept()