# ui_auth.py
import json
import re
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                               QPushButton, QMessageBox, QWidget, QHBoxLayout,
                               QStackedWidget)
from PySide6.QtCore import Qt
import qtawesome as qta


class AuthWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Authentication - Surveillance System")
        self.setFixedSize(450, 400)
        self.user_data = None

        # Main Layout
        main_layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget()

        # Create Login and Signup Widgets
        self.login_widget = self.create_login_widget()
        self.signup_widget = self.create_signup_widget()

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.signup_widget)

        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def create_login_widget(self):
        """Creates the UI for the login form."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title_label = QLabel("Login")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.login_username_input = QLineEdit()
        self.login_username_input.setPlaceholderText("Username")
        layout.addWidget(self.login_username_input)

        self.login_password_input = QLineEdit()
        self.login_password_input.setPlaceholderText("Password")
        self.login_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.login_password_input)

        login_button = QPushButton("Login")
        login_button.setIcon(qta.icon("fa5s.sign-in-alt"))
        login_button.clicked.connect(self.attempt_login)
        layout.addWidget(login_button)

        switch_button = QPushButton("Don't have an account? Sign Up")
        switch_button.setStyleSheet("background-color: transparent; border: none; color: #88C0D0;")
        switch_button.setCursor(Qt.PointingHandCursor)
        switch_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(switch_button)

        return widget

    def create_signup_widget(self):
        """Creates the UI for the signup form."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title_label = QLabel("Create Account")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.signup_username_input = QLineEdit()
        self.signup_username_input.setPlaceholderText("Username")
        layout.addWidget(self.signup_username_input)

        self.signup_email_input = QLineEdit()
        self.signup_email_input.setPlaceholderText("Email Address")
        layout.addWidget(self.signup_email_input)

        self.signup_password_input = QLineEdit()
        self.signup_password_input.setPlaceholderText("Password")
        self.signup_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.signup_password_input)

        signup_button = QPushButton("Sign Up")
        signup_button.setIcon(qta.icon("fa5s.user-plus"))
        signup_button.clicked.connect(self.attempt_signup)
        layout.addWidget(signup_button)

        switch_button = QPushButton("Already have an account? Login")
        switch_button.setStyleSheet("background-color: transparent; border: none; color: #88C0D0;")
        switch_button.setCursor(Qt.PointingHandCursor)
        switch_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(switch_button)

        return widget

    def attempt_login(self):
        username = self.login_username_input.text()
        password = self.login_password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Username and password cannot be empty.")
            return

        try:
            with open("users.json", 'r') as f:
                users = json.load(f)

            if username in users and users[username]["password"] == password:
                self.user_data = {"username": username, "email": users[username]["email"]}
                self.accept()  # Close the dialog and signal success
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.critical(self, "Error", "Could not read user database. A new one will be created on signup.")
            return

    def attempt_signup(self):
        username = self.signup_username_input.text().strip()
        email = self.signup_email_input.text().strip()
        password = self.signup_password_input.text()

        if not all([username, email, password]):
            QMessageBox.warning(self, "Signup Failed", "All fields are required.")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Signup Failed", "Please enter a valid email address.")
            return

        try:
            with open("users.json", 'r') as f:
                users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            users = {}

        if username in users:
            QMessageBox.warning(self, "Signup Failed", "This username is already taken.")
            return

        users[username] = {"password": password, "email": email}

        with open("users.json", 'w') as f:
            json.dump(users, f, indent=4)

        QMessageBox.information(self, "Success", "Account created successfully! Please login.")
        self.stacked_widget.setCurrentIndex(0)