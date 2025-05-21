import time
import sys
import os

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt, QTimer

from core.monitor import get_snapshot, should_trigger_alert
from core.alerts import AlertSound
from core.timer import get_uptime_minutes, format_idle_duration

from ui.components import make_link, make_donate_button
from utils.helpers import safe_float

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon



class RenderUpdateChecker(QWidget):
    def __init__(self):
        super().__init__()

# --- ДОБАВЛЕНО В ИНИЦИАЛИЗАТОРЕ ---
self.sound_enabled = True

        self.folder_path = ""
        self.timeout_minutes = 1
        self.monitoring = False
        self.last_change = time.time()
        self.last_snapshot = {}
        self.alert_counter = 0
        self.uptime_start = time.time()
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, "assets/icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.alert = AlertSound("assets/alert_fixed.wav")

        self.init_ui()
        self.init_timers()

    def init_ui(self):
        self.setWindowTitle("RenderUpdateChecker 1.0")
        self.setFixedSize(500, 350)
        layout = QVBoxLayout()

        title = QLabel("➿ RenderUpdateChecker 1.0")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # выбор папки
        self.folder_label = QLabel("📁 Отслеживаемая папка")
        layout.addWidget(self.folder_label)

        select_btn = QPushButton("📂 Выбрать папку")
        select_btn.clicked.connect(self.select_folder)
        layout.addWidget(select_btn)

        # таймер ожидания
        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("⌛ Время ожидания (мин):"))
        self.timeout_input = QLineEdit("1")
        time_row.addWidget(self.timeout_input)
        layout.addLayout(time_row)

        # кнопка Старт/Пауза
        
        # кнопка Старт/Пауза + Звук
        control_row = QHBoxLayout()
        self.toggle_btn = QPushButton("🔎 Старт")
        self.toggle_btn.clicked.connect(self.toggle_monitoring)
        control_row.addWidget(self.toggle_btn)

        self.sound_btn = QPushButton("🔔")
        self.sound_btn.setCheckable(True)
        self.sound_btn.setChecked(True)
        self.sound_btn.clicked.connect(self.toggle_sound)
        self.sound_btn.setFixedSize(32, 32)
        control_row.addWidget(self.sound_btn)

        layout.addLayout(control_row)


        # строка статуса и времени активности
        status_row = QHBoxLayout()
        self.status = QLabel("🔲 Готов к запуску")
        self.timer_counter_label = QLabel("⏱ Время активности: 0 мин.")
        status_row.addWidget(self.status)
        status_row.addWidget(self.timer_counter_label)
        layout.addLayout(status_row)

        # предупреждение
        self.warning_block = QFrame()
        self.warning_block.setFrameShape(QFrame.Shape.StyledPanel)
        self.warning_block.setVisible(False)
        warning_layout = QVBoxLayout()

        self.warning_label = QLabel("⛔ Нет новых файлов")
        self.counter_label = QLabel("⌛ Время бездействия: 0 сек.")
        warning_layout.addWidget(self.warning_label)
        warning_layout.addWidget(self.counter_label)

        btn_row = QHBoxLayout()
        
        self.resume_btn = QPushButton("✅ Продолжить")
        self.resume_btn.clicked.connect(self.resume_monitoring)
        btn_row.addStretch()
        btn_row.addWidget(self.resume_btn)

        self.pause_btn = QPushButton("❌ Стоп")
        self.pause_btn.clicked.connect(self.pause_monitoring)
        btn_row.addWidget(self.pause_btn)

        warning_layout.addLayout(btn_row)
        self.warning_block.setLayout(warning_layout)
        layout.addWidget(self.warning_block)
        
        # кредиты и донат
        link_row = QHBoxLayout()
        link_row.addWidget(QLabel("💡 Идея "))
        link_row.addWidget(make_link("camfrae", "https://camfrae.com/"))
        link_row.addWidget(QLabel("🤖 Реализация "))
        link_row.addWidget(make_link("ChatGPT", "https://openai.com/"))
        link_row.addWidget(QLabel("📜 Исходный код "))
        link_row.addWidget(make_link("GitHub", "https://github.com/camfrae"))
        link_row.addWidget(make_link("🤙 Донат", "https://camfrae.com/donate"))
        layout.addLayout(link_row)


        self.setLayout(layout)

    def init_timers(self):
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.check_folder)

        self.idle_timer = QTimer()
        self.idle_timer.setInterval(1000)
        self.idle_timer.timeout.connect(self.update_idle_counter)

        self.uptime_timer = QTimer()
        self.uptime_timer.setInterval(60000)
        self.uptime_timer.timeout.connect(self.update_uptime)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:
            self.folder_path = folder
            self.folder_label.setText(f"📁 {folder}")

    def toggle_monitoring(self):
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        self.sound_enabled = True
        self.alert.enabled = True
        self.sound_btn.setChecked(True)
        self.sound_btn.setText("🔔")

        try:
            self.timeout_minutes = safe_float(self.timeout_input.text())
        except:
            self.timeout_minutes = 1

        if not self.folder_path:
            self.status.setText("❌ Укажите папку")
            return

        self.last_snapshot = get_snapshot(self.folder_path)
        self.last_change = time.time()
        self.uptime_start = time.time()
        self.alert_counter = 0
        self.monitoring = True
        self.status.setText("🟢 Мониторинг активен")
        self.toggle_btn.setText("⏸ Пауза")
        self.timer.start()
        self.uptime_timer.start()

    def stop_monitoring(self):
        self.monitoring = False
        self.timer.stop()
        self.uptime_timer.stop()
        self.alert.stop()
        self.alert.stop_repeat()
        self.status.setText("⏸ Мониторинг приостановлен")
        self.toggle_btn.setText("▶ Старт")


    def resume_monitoring(self):
        self.sound_enabled = True
        self.alert.enabled = True
        self.sound_btn.setChecked(True)
        self.sound_btn.setText("🔔")

        self.idle_timer.stop()
        self.warning_block.setVisible(False)
        self.alert.stop()
                self.mute_btn.setStyleSheet("font-size: 18px;")
        self.start_monitoring()

    def pause_monitoring(self):
        self.idle_timer.stop()
        self.warning_block.setVisible(False)
        self.alert.stop()
        self.stop_monitoring()

    
        self.alert.disable(self.mute_btn)

    def check_folder(self):
        if not self.monitoring:
            return

        current = get_snapshot(self.folder_path)
        should_alert, self.last_snapshot, self.last_change = should_trigger_alert(
            self.last_snapshot, current, self.last_change, self.timeout_minutes
        )

        if should_alert:
            self.trigger_warning()

    def trigger_warning(self):
        self.monitoring = False
        self.timer.stop()
        self.alert_counter = 0
        self.warning_block.setVisible(True)
        self.status.setText("⚠ Обнаружено бездействие")
        self.alert.repeat_every(10000, lambda: not self.monitoring)
        self.idle_timer.start()
        QApplication.alert(self, 0)  # ← мигает иконкой на панели задач

    def update_idle_counter(self):
        self.alert_counter += 1
        formatted = format_idle_duration(self.alert_counter)
        self.counter_label.setText(f"⌛ Время бездействия: {formatted}")

    def update_uptime(self):
        mins = get_uptime_minutes(self.uptime_start)
        self.timer_counter_label.setText(f"⏱ Время активности: {mins} мин.")
        

    def toggle_sound(self):
        self.sound_enabled = self.sound_btn.isChecked()
        self.alert.enabled = self.sound_enabled
        if self.sound_enabled:
            self.sound_btn.setText("🔔")
        else:
            self.sound_btn.setText("🔕")
