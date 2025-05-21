import os
import sys
import threading
from playsound import playsound
from PyQt6.QtCore import QTimer

class AlertSound:
    def __init__(self, sound_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        self.full_path = os.path.join(base_path, sound_path)
        self.enabled = True
        self._repeating = False

    def play_once(self):
        if self.enabled:
            def _play():
                try:
                    playsound(self.full_path)
                except Exception as e:
                    print("Sound error:", e)
            threading.Thread(target=_play, daemon=True).start()

    def stop(self):
        # playsound нет функции stop — игнорируем
        pass

    def disable(self, button=None):
        self.enabled = False
        if button:
            button.setStyleSheet("font-size: 18px; opacity: 0.3;")
            button.setEnabled(False)

    def repeat_every(self, interval_ms, condition_callable):
        self._repeating = True

        def repeat():
            if self.enabled and self._repeating and condition_callable():
                self.play_once()
                QTimer.singleShot(interval_ms, repeat)
        repeat()

    def stop_repeat(self):
        self._repeating = False
