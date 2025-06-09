# main.py

import sys
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QTimer
import qtawesome as qta

from ui_auth import AuthWindow
from ui_main_window import MainWindow


class AppController:
    def __init__(self, app):
        self.app = app
        self.main_win = None

    def start(self):
        """Initial start of the application."""
        self.show_login()

    def show_login(self):
        """Displays the authentication window."""
        auth_dialog = AuthWindow()
        if auth_dialog.exec() == QDialog.Accepted:
            self.show_main_window(auth_dialog.user_data)
        else:
            self.app.quit()  # Exit if user closes the auth window

    def show_main_window(self, user_data):
        """Displays the main application window."""
        self.main_win = MainWindow(user_data=user_data)
        self.main_win.logout_requested.connect(self.handle_logout)
        self.main_win.show()

    def handle_logout(self):
        """Handles the logout signal from the main window."""
        self.main_win = None  # Clear reference to the old window
        QTimer.singleShot(100, self.show_login)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app_icon = qta.icon("fa5s.shield-alt")
    app.setWindowIcon(app_icon)
    try:
        with open("style.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Stylesheet 'style.qss' not found. Using default style.")

    controller = AppController(app)
    controller.start()

    sys.exit(app.exec())