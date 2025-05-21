import sys
from PyQt6.QtWidgets import QApplication
from ui.window import RenderUpdateChecker

def run_app():
    app = QApplication(sys.argv)
    win = RenderUpdateChecker()
    win.show()
    sys.exit(app.exec())
