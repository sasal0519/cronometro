import sys
import time
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class StopwatchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cronometro Simples")
        self.resize(640, 420)
        self.setMinimumSize(560, 380)

        self.current_mode = "stopwatch"
        self.elapsed_before_start = 0.0
        self.started_at = None
        self.running = False
        self.pomodoro_schedule = [
            ("Foco", 25 * 60),
            ("Pausa", 5 * 60),
            ("Foco", 25 * 60),
            ("Pausa", 5 * 60),
            ("Foco", 25 * 60),
            ("Pausa", 5 * 60),
            ("Foco", 25 * 60),
            ("Pausa longa", 15 * 60),
        ]
        self.pomodoro_phase_index = 0
        self.pomodoro_remaining_before_start = float(self.pomodoro_schedule[0][1])

        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_displays)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        display_card = QWidget()
        display_card.setObjectName("displayCard")

        display_layout = QVBoxLayout(display_card)
        display_layout.setContentsMargins(32, 32, 32, 32)
        display_layout.setSpacing(22)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(12)

        mode_switch = QHBoxLayout()
        mode_switch.setContentsMargins(0, 0, 0, 0)
        mode_switch.setSpacing(10)

        self.stopwatch_mode_button = QPushButton("Cronometro")
        self.stopwatch_mode_button.setObjectName("modeButton")
        self.stopwatch_mode_button.clicked.connect(lambda: self.set_mode("stopwatch"))

        self.pomodoro_mode_button = QPushButton("Pomodoro")
        self.pomodoro_mode_button.setObjectName("modeButton")
        self.pomodoro_mode_button.clicked.connect(lambda: self.set_mode("pomodoro"))

        mode_switch.addWidget(self.stopwatch_mode_button)
        mode_switch.addWidget(self.pomodoro_mode_button)
        top_row.addLayout(mode_switch)
        top_row.addStretch(1)

        clock_badge = QWidget()
        clock_badge.setObjectName("clockBadge")

        clock_badge_layout = QVBoxLayout(clock_badge)
        clock_badge_layout.setContentsMargins(16, 12, 16, 12)
        clock_badge_layout.setSpacing(0)

        self.stopwatch_label = QLabel("00:00:00")
        self.stopwatch_label.setAlignment(Qt.AlignCenter)
        self.stopwatch_label.setObjectName("stopwatch")

        self.clock_label = QLabel("")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setObjectName("clock")

        clock_badge_layout.addWidget(self.clock_label)
        top_row.addWidget(clock_badge, alignment=Qt.AlignTop)

        self.mode_label = QLabel("")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setObjectName("modeLabel")

        markers_layout = QHBoxLayout()
        markers_layout.setContentsMargins(0, 0, 0, 0)
        markers_layout.setSpacing(8)

        self.pomodoro_markers = []
        for _ in self.pomodoro_schedule:
            marker = QLabel("")
            marker.setObjectName("pomodoroMarker")
            marker.setFixedHeight(18)
            markers_layout.addWidget(marker, stretch=1)
            self.pomodoro_markers.append(marker)

        self.markers_widget = QWidget()
        self.markers_widget.setObjectName("markersWidget")
        self.markers_widget.setLayout(markers_layout)

        display_layout.addLayout(top_row)
        display_layout.addWidget(self.mode_label)
        display_layout.addWidget(self.markers_widget)
        display_layout.addStretch(1)
        display_layout.addWidget(self.stopwatch_label)
        display_layout.addStretch(1)

        buttons = QHBoxLayout()
        buttons.setSpacing(14)

        self.start_button = QPushButton("Iniciar")
        self.start_button.setObjectName("startButton")
        self.pause_button = QPushButton("Pausar")
        self.pause_button.setObjectName("pauseButton")
        self.reset_button = QPushButton("Zerar")
        self.reset_button.setObjectName("resetButton")

        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.pause_timer)
        self.reset_button.clicked.connect(self.reset_timer)

        buttons.addWidget(self.start_button)
        buttons.addWidget(self.pause_button)
        buttons.addWidget(self.reset_button)
        buttons.setStretch(0, 1)
        buttons.setStretch(1, 1)
        buttons.setStretch(2, 1)

        self.apply_shadow(clock_badge, blur_radius=0, offset_y=5, color="rgba(0, 0, 0, 255)")
        self.apply_shadow(self.stopwatch_mode_button, blur_radius=0, offset_y=5, color="rgba(0, 0, 0, 255)")
        self.apply_shadow(self.pomodoro_mode_button, blur_radius=0, offset_y=5, color="rgba(0, 0, 0, 255)")
        self.apply_shadow(self.start_button, blur_radius=0, offset_y=6, color="rgba(0, 0, 0, 255)")
        self.apply_shadow(self.pause_button, blur_radius=0, offset_y=6, color="rgba(0, 0, 0, 255)")
        self.apply_shadow(self.reset_button, blur_radius=0, offset_y=6, color="rgba(0, 0, 0, 255)")

        display_layout.addLayout(buttons)
        layout.addWidget(display_card, stretch=1)

        self.update_mode_buttons()
        self.update_markers()
        self.update_displays()
        self.timer.start()

    def apply_shadow(self, widget, blur_radius, offset_y, color):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur_radius)
        shadow.setOffset(0, offset_y)
        shadow.setColor(Qt.GlobalColor.transparent)
        shadow.setColor(color_from_rgba_string(color))
        widget.setGraphicsEffect(shadow)

    def current_elapsed(self):
        if not self.running or self.started_at is None:
            return self.elapsed_before_start
        return self.elapsed_before_start + (time.perf_counter() - self.started_at)

    def current_pomodoro_remaining(self):
        if not self.running or self.started_at is None:
            return self.pomodoro_remaining_before_start
        remaining = self.pomodoro_remaining_before_start - (time.perf_counter() - self.started_at)
        return max(0.0, remaining)

    def format_elapsed(self, elapsed):
        total_seconds = int(elapsed)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def format_mode_label(self):
        if self.current_mode == "stopwatch":
            return "Cronometro livre"

        phase_name, _ = self.pomodoro_schedule[self.pomodoro_phase_index]
        cycle_number = (self.pomodoro_phase_index // 2) + 1
        return f"Pomodoro · {phase_name} {cycle_number}"

    def update_mode_buttons(self):
        self.stopwatch_mode_button.setProperty(
            "active", "true" if self.current_mode == "stopwatch" else "false"
        )
        self.pomodoro_mode_button.setProperty(
            "active", "true" if self.current_mode == "pomodoro" else "false"
        )
        for button in (self.stopwatch_mode_button, self.pomodoro_mode_button):
            button.style().unpolish(button)
            button.style().polish(button)

    def update_markers(self):
        markers_visible = self.current_mode == "pomodoro"
        self.markers_widget.setVisible(markers_visible)
        for index, marker in enumerate(self.pomodoro_markers):
            if not markers_visible:
                marker.setProperty("state", "hidden")
            elif index < self.pomodoro_phase_index:
                marker.setProperty("state", "done")
            elif index == self.pomodoro_phase_index:
                marker.setProperty("state", "current")
            else:
                marker.setProperty("state", "upcoming")
            marker.style().unpolish(marker)
            marker.style().polish(marker)

    def set_mode(self, mode):
        if mode == self.current_mode:
            return

        self.running = False
        self.started_at = None
        self.current_mode = mode
        if mode == "pomodoro":
            self.pomodoro_phase_index = 0
            self.pomodoro_remaining_before_start = float(self.pomodoro_schedule[0][1])
        self.update_mode_buttons()
        self.update_markers()
        self.update_displays()

    def advance_pomodoro_phase(self):
        self.pomodoro_phase_index = (self.pomodoro_phase_index + 1) % len(self.pomodoro_schedule)
        self.pomodoro_remaining_before_start = float(self.pomodoro_schedule[self.pomodoro_phase_index][1])
        if self.running:
            self.started_at = time.perf_counter()
        else:
            self.started_at = None
        self.update_markers()

    def update_displays(self):
        if self.current_mode == "stopwatch":
            self.stopwatch_label.setText(self.format_elapsed(self.current_elapsed()))
        else:
            remaining = self.current_pomodoro_remaining()
            if self.running and remaining <= 0:
                self.advance_pomodoro_phase()
                remaining = self.current_pomodoro_remaining()
            self.stopwatch_label.setText(self.format_elapsed(remaining))

        self.clock_label.setText(datetime.now().strftime("%H:%M:%S"))
        self.mode_label.setText(self.format_mode_label())

    def start_timer(self):
        if self.running:
            return
        self.started_at = time.perf_counter()
        self.running = True

    def pause_timer(self):
        if not self.running:
            return
        if self.current_mode == "stopwatch":
            self.elapsed_before_start = self.current_elapsed()
        else:
            self.pomodoro_remaining_before_start = self.current_pomodoro_remaining()
        self.started_at = None
        self.running = False

    def reset_timer(self):
        self.started_at = None
        self.running = False
        if self.current_mode == "stopwatch":
            self.elapsed_before_start = 0.0
        else:
            self.pomodoro_phase_index = 0
            self.pomodoro_remaining_before_start = float(self.pomodoro_schedule[0][1])
            self.update_markers()
        self.update_displays()


def color_from_rgba_string(value):
    components = value.removeprefix("rgba(").removesuffix(")")
    red, green, blue, alpha = [int(part.strip()) for part in components.split(",")]
    return QColor(red, green, blue, alpha)


def build_app_style():
    return f"""
QMainWindow {{
    background: #111111;
}}

QWidget {{
    color: #ffffff;
}}

QWidget#central {{
    background: transparent;
}}

QWidget#displayCard {{
    background: #f3f3f3;
    border: 4px solid #000000;
    border-radius: 0px;
}}

QWidget#clockBadge {{
    background: #ffffff;
    border: 4px solid #000000;
    border-radius: 12px;
}}

QWidget#markersWidget {{
    background: transparent;
}}

QLabel#stopwatch {{
    font: 900 72px 'Courier New';
    color: #f5f5f5;
    border: 4px solid #000000;
    border-radius: 18px;
    padding: 34px 20px;
    background: #161616;
    selection-background-color: #7a7a7a;
}}

QLabel#clock {{
    font: 900 22px 'Arial Black';
    background: transparent;
    color: #111111;
}}

QLabel#modeLabel {{
    font: 900 16px 'Arial Black';
    color: #111111;
    background: transparent;
}}

QLabel#pomodoroMarker {{
    background: #d2d2d2;
    border: 3px solid #000000;
    border-radius: 6px;
    min-width: 24px;
}}

QLabel#pomodoroMarker[state="current"] {{
    background: #111111;
}}

QLabel#pomodoroMarker[state="done"] {{
    background: #7e7e7e;
}}

QLabel#pomodoroMarker[state="upcoming"] {{
    background: #f8f8f8;
}}

QLabel#pomodoroMarker[state="hidden"] {{
    background: transparent;
    border-color: transparent;
}}

QPushButton {{
    min-height: 28px;
    color: #111111;
    border: 4px solid #000000;
    padding: 16px 18px;
    font: 900 14px 'Arial Black';
    border-radius: 12px;
}}

QPushButton:hover {{
    color: #000000;
    background: #f4f4f4;
}}

QPushButton:pressed {{
    padding-top: 19px;
    padding-bottom: 13px;
    background: #bdbdbd;
}}

QPushButton#startButton {{
    background: #ffffff;
}}

QPushButton#startButton:hover {{
    background: #f4f4f4;
}}

QPushButton#pauseButton {{
    background: #d9d9d9;
}}

QPushButton#pauseButton:hover {{
    background: #cccccc;
}}

QPushButton#resetButton {{
    background: #a6a6a6;
}}

QPushButton#resetButton:hover {{
    background: #979797;
}}

QPushButton#modeButton {{
    min-height: 18px;
    padding: 12px 16px;
    background: #d9d9d9;
}}

QPushButton#modeButton[active="true"] {{
    background: #111111;
    color: #f5f5f5;
}}

QPushButton#modeButton[active="true"]:hover {{
    background: #222222;
    color: #ffffff;
}}
"""


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(build_app_style())
    app.setFont(QFont("Arial", 11))

    window = StopwatchWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
