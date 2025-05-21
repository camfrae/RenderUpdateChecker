from PyQt6.QtWidgets import QLabel, QPushButton
import webbrowser

def make_link(text, url):
    label = QLabel(f"<a href='{url}' style='color: #FCA311; text-decoration: none'>{text}</a>")
    label.setOpenExternalLinks(True)
    return label

def make_donate_button():
    button = QPushButton("🤙 Донат")
    button.clicked.connect(lambda: webbrowser.open("https://camfrae.com/donate"))
    button.setStyleSheet("color: #FCA311; background: transparent; border: none;")
    return button
