import sys
import time
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)


class StopwatchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cronometro Simples")
        self.resize(520, 300)
        self.setMinimumSize(420, 260)

        self.elapsed_before_start = 0.0
        self.started_at = None
        self.running = False

        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_displays)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title = QLabel("Cronometro")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")

        self.stopwatch_label = QLabel("00:00:00")
        self.stopwatch_label.setAlignment(Qt.AlignCenter)
        self.stopwatch_label.setObjectName("stopwatch")

        self.clock_label = QLabel("")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setObjectName("clock")

        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        self.start_button = QPushButton("Iniciar")
        self.pause_button = QPushButton("Pausar")
        self.reset_button = QPushButton("Zerar")

        self.start_button.clicked.connect(self.start_stopwatch)
        self.pause_button.clicked.connect(self.pause_stopwatch)
        self.reset_button.clicked.connect(self.reset_stopwatch)

        buttons.addWidget(self.start_button)
        buttons.addWidget(self.pause_button)
        buttons.addWidget(self.reset_button)

        layout.addWidget(title)
        layout.addWidget(self.stopwatch_label)
        layout.addWidget(self.clock_label)
        layout.addLayout(buttons)

        self.update_displays()
        self.timer.start()

    def current_elapsed(self):
        if not self.running or self.started_at is None:
            return self.elapsed_before_start
        return self.elapsed_before_start + (time.perf_counter() - self.started_at)

    def format_elapsed(self, elapsed):
        total_seconds = int(elapsed)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_displays(self):
        self.stopwatch_label.setText(self.format_elapsed(self.current_elapsed()))
        self.clock_label.setText(datetime.now().strftime("Relogio: %H:%M:%S"))

    def start_stopwatch(self):
        if self.running:
            return
        self.started_at = time.perf_counter()
        self.running = True

    def pause_stopwatch(self):
        if not self.running:
            return
        self.elapsed_before_start = self.current_elapsed()
        self.started_at = None
        self.running = False

    def reset_stopwatch(self):
        self.elapsed_before_start = 0.0
        self.started_at = None
        self.running = False
        self.update_displays()


APP_STYLE = """
QMainWindow {
    background: #111111;
}

QWidget {
    background: #111111;
    color: #ffffff;
}

QLabel#title {
    font: 700 18px 'Arial';
}

QLabel#stopwatch {
    font: 700 44px 'Courier New';
    border: 2px solid #ffffff;
    padding: 20px;
    background: #1a1a1a;
}

QLabel#clock {
    font: 400 18px 'Courier New';
}

QPushButton {
    background: #1a1a1a;
    color: #ffffff;
    border: 1px solid #ffffff;
    padding: 10px 16px;
    font: 600 14px 'Arial';
}

QPushButton:hover {
    background: #262626;
}
"""


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    app.setFont(QFont("Arial", 11))

    window = StopwatchWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
