# ui_login.py
import json
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                               QPushButton, QMessageBox, QWidget, QHBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import qtawesome as qta


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - Surveillance System")
        self.setFixedSize(400, 250)
        self.user = None

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Intelligent Surveillance System")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Login Button
        login_button = QPushButton("Login")
        login_button.setIcon(qta.icon("fa5s.sign-in-alt"))
        login_button.clicked.connect(self.attempt_login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            with open("users.json", 'r') as f:
                users = json.load(f)

            if username in users and users[username] == password:
                self.user = username
                self.accept()  # Close the dialog and signal success
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "users.json file not found. Cannot log in.")
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Error reading users.json. The file might be corrupted.")