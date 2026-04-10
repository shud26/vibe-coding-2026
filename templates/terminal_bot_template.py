#!/usr/bin/env python3
"""
Terminal Style Bot UI Template
- 해커/터미널 느낌의 모던 데스크톱 앱
- PySide6 (Qt) 기반
- 재사용 가능한 템플릿

사용법:
  1. 이 파일 복사
  2. BotWorker 클래스에 봇 로직 구현
  3. 사이드바/버튼 커스터마이즈
"""

import sys
import queue
import threading
import time
from datetime import datetime, timezone, timedelta

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTextEdit, QFrame, QSlider,
    QCheckBox, QLineEdit,
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject


# ─── 색상 테마 (터미널 스타일) ─────────────────────────────
COLORS = {
    "bg":       "#0a0a0a",      # 배경 (거의 검정)
    "card":     "#0f0f0f",      # 카드 배경
    "border":   "#1a3a1a",      # 테두리 (어두운 초록)
    "green":    "#00ff41",      # 메인 초록 (Matrix 느낌)
    "green2":   "#00cc33",      # 보조 초록
    "dim":      "#2d5a2d",      # 흐린 초록 (비활성)
    "text":     "#00ff41",      # 텍스트
    "yellow":   "#ccff00",      # 강조 (노랑)
    "red":      "#ff3333",      # 에러/위험
    "cyan":     "#00ffff",      # 액센트 (시안)
}

MONO_FONT = "SF Mono, Menlo, Consolas, monospace"

STYLESHEET = f"""
QMainWindow {{ background-color: {COLORS["bg"]}; }}
QWidget {{ color: {COLORS["green"]}; font-family: {MONO_FONT}; font-size: 14px; }}
QLabel {{ background: transparent; }}
QComboBox {{
    background-color: {COLORS["bg"]};
    border: 1px solid {COLORS["border"]};
    padding: 6px 10px;
    color: {COLORS["green"]};
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox::down-arrow {{ border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid {COLORS["dim"]}; margin-right: 8px; }}
QComboBox QAbstractItemView {{ background-color: {COLORS["bg"]}; border: 1px solid {COLORS["border"]}; color: {COLORS["green"]}; selection-background-color: {COLORS["border"]}; }}
QLineEdit {{
    background-color: {COLORS["bg"]};
    border: 1px solid {COLORS["border"]};
    padding: 6px 10px;
    color: {COLORS["green"]};
}}
QPushButton {{
    background-color: transparent;
    border: 1px solid {COLORS["border"]};
    padding: 10px 20px;
    color: {COLORS["green"]};
    font-size: 14px;
}}
QPushButton:hover {{ background-color: {COLORS["border"]}; }}
QPushButton:disabled {{ color: {COLORS["dim"]}; border-color: {COLORS["dim"]}; }}
QTextEdit {{
    background-color: {COLORS["bg"]};
    border: none;
    color: {COLORS["green"]};
    font-family: {MONO_FONT};
    font-size: 14px;
}}
QSlider::groove:horizontal {{ height: 2px; background: {COLORS["border"]}; }}
QSlider::handle:horizontal {{ background: {COLORS["green"]}; width: 10px; height: 10px; margin: -4px 0; border-radius: 5px; }}
QSlider::sub-page:horizontal {{ background: {COLORS["green"]}; }}
QCheckBox {{ spacing: 8px; }}
QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {COLORS["border"]}; background: {COLORS["bg"]}; }}
QCheckBox::indicator:checked {{ background: {COLORS["green"]}; border-color: {COLORS["green"]}; }}
"""

KST = timezone(timedelta(hours=9))


# ─── 로그 큐 (stdout 캡처) ─────────────────────────────────
class QueueWriter:
    def __init__(self, q):
        self._q = q

    def write(self, text):
        if text and text.strip():
            self._q.put(text.rstrip("\n"))

    def flush(self):
        pass


# ─── 시그널 브릿지 (스레드 → UI) ───────────────────────────
class Bridge(QObject):
    log = Signal(str)
    status = Signal(bool)  # running True/False
    update_value = Signal(str, str)  # key, value


# ─── 사이드바 섹션 위젯 ───────────────────────────────────
class SidebarSection(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setStyleSheet(f"border: 1px solid {COLORS['border']}; background: {COLORS['card']};")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(10)

        header = QLabel(title)
        header.setStyleSheet(f"color: {COLORS['dim']}; font-size: 13px; border: none; letter-spacing: 2px;")
        self.layout.addWidget(header)

    def add_row(self, label, value_widget):
        row = QHBoxLayout()
        row.setSpacing(10)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {COLORS['dim']}; font-size: 14px; border: none;")
        row.addWidget(lbl)
        row.addStretch()

        if isinstance(value_widget, str):
            val = QLabel(value_widget)
            val.setStyleSheet(f"color: {COLORS['green']}; font-size: 14px; border: none;")
            row.addWidget(val)
            self.layout.addLayout(row)
            return val
        else:
            row.addWidget(value_widget)
            self.layout.addLayout(row)
            return value_widget


# ─── 메인 앱 ─────────────────────────────────────────────
class TerminalBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TERMINAL BOT")
        self.setMinimumSize(1100, 750)
        self.resize(1200, 800)

        self.running = False
        self.stop_event = threading.Event()
        self.log_queue = queue.Queue()
        self.start_time = datetime.now(KST)
        self._orig_stdout = sys.stdout
        sys.stdout = QueueWriter(self.log_queue)

        # 시그널 브릿지
        self.bridge = Bridge()
        self.bridge.log.connect(self._append_log)
        self.bridge.status.connect(self._set_status)

        # 메인 레이아웃
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._build_header(main_layout)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._build_sidebar(body)
        self._build_main(body)

        main_layout.addLayout(body, stretch=1)

        # 타이머
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)
        self._timer.start(100)

        self._time_timer = QTimer()
        self._time_timer.timeout.connect(self._update_time)
        self._time_timer.start(1000)

    def _build_header(self, parent):
        header = QFrame()
        header.setStyleSheet(f"background: {COLORS['bg']}; border-bottom: 1px solid {COLORS['border']};")
        header.setFixedHeight(60)

        h = QHBoxLayout(header)
        h.setContentsMargins(20, 0, 20, 0)

        # 타이틀
        title = QLabel("TERMINAL BOT")
        title.setStyleSheet(f"color: {COLORS['green']}; font-size: 18px; font-weight: bold; border: none;")
        h.addWidget(title)

        # 버전
        ver = QLabel("v1.0")
        ver.setStyleSheet(f"color: {COLORS['dim']}; font-size: 12px; border: 1px solid {COLORS['border']}; padding: 4px 10px; border-radius: 3px;")
        h.addWidget(ver)

        h.addStretch()

        # 상태 표시
        self.status_label = QLabel("IDLE")
        self.status_label.setStyleSheet(f"color: {COLORS['dim']}; font-size: 14px; border: none;")
        h.addWidget(self.status_label)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color: {COLORS['red']}; font-size: 14px; border: none; margin-left: 6px;")
        h.addWidget(self.status_dot)

        spacer = QLabel("    ")
        spacer.setStyleSheet("border: none;")
        h.addWidget(spacer)

        # 시간
        self.time_label = QLabel("00:00:00")
        self.time_label.setStyleSheet(f"color: {COLORS['green']}; font-size: 16px; border: none;")
        h.addWidget(self.time_label)

        parent.addWidget(header)

    def _build_sidebar(self, parent):
        sidebar = QFrame()
        sidebar.setStyleSheet(f"background: {COLORS['bg']}; border-right: 1px solid {COLORS['border']};")
        sidebar.setFixedWidth(280)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # ─── STATUS 섹션 ───
        status_sec = SidebarSection("STATUS")
        self.engine_val = status_sec.add_row("Engine", "IDLE")
        self.uptime_val = status_sec.add_row("Uptime", "00:00:00")
        layout.addWidget(status_sec)

        # ─── CONFIG 섹션 (커스터마이즈) ───
        config_sec = SidebarSection("CONFIG")

        self.input1 = QLineEdit("default")
        self.input1.setFixedWidth(100)
        config_sec.add_row("Input 1", self.input1)

        self.combo1 = QComboBox()
        self.combo1.addItems(["Option A", "Option B", "Option C"])
        self.combo1.setFixedWidth(100)
        config_sec.add_row("Select", self.combo1)

        self.checkbox1 = QCheckBox("Enable Feature")
        self.checkbox1.setStyleSheet(f"color: {COLORS['cyan']}; border: none;")
        config_sec.layout.addWidget(self.checkbox1)

        layout.addWidget(config_sec)

        # ─── STATS 섹션 ───
        stats_sec = SidebarSection("STATS")
        self.stat1_val = stats_sec.add_row("Counter", "0")
        self.stat2_val = stats_sec.add_row("Total", "$0")
        layout.addWidget(stats_sec)

        layout.addStretch()
        parent.addWidget(sidebar)

    def _build_main(self, parent):
        main = QFrame()
        main.setStyleSheet(f"background: {COLORS['bg']};")

        layout = QVBoxLayout(main)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 콘솔 영역
        console_frame = QFrame()
        console_layout = QVBoxLayout(console_frame)
        console_layout.setContentsMargins(16, 16, 16, 16)
        console_layout.setSpacing(12)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        console_layout.addWidget(self.log_text, stretch=1)

        # 버튼 영역
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_start = QPushButton("[ START ]")
        self.btn_start.setStyleSheet(f"color: {COLORS['green']}; border-color: {COLORS['green']};")
        self.btn_start.clicked.connect(self._on_start)
        btn_row.addWidget(self.btn_start)

        self.btn_stop = QPushButton("[ STOP ]")
        self.btn_stop.setStyleSheet(f"color: {COLORS['red']}; border-color: {COLORS['red']};")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._on_stop)
        btn_row.addWidget(self.btn_stop)

        self.btn_action = QPushButton("[ ACTION ]")
        self.btn_action.setStyleSheet(f"color: {COLORS['cyan']}; border-color: {COLORS['cyan']};")
        self.btn_action.clicked.connect(self._on_action)
        btn_row.addWidget(self.btn_action)

        btn_row.addStretch()

        console_layout.addLayout(btn_row)
        layout.addWidget(console_frame, stretch=1)

        parent.addWidget(main, stretch=1)

    # ─── 유틸리티 ─────────────────────────────────────────

    def _log(self, msg):
        self.log_queue.put(msg)

    def _poll(self):
        for _ in range(50):
            try:
                self.bridge.log.emit(self.log_queue.get_nowait())
            except queue.Empty:
                break

    def _update_time(self):
        now = datetime.now(KST)
        self.time_label.setText(now.strftime("%H:%M:%S"))

        delta = now - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.uptime_val.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def _append_log(self, msg):
        ts = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")

        if "[!]" in msg or "fail" in msg.lower() or "error" in msg.lower():
            color = COLORS["red"]
        elif "complete" in msg.lower() or "success" in msg.lower():
            color = COLORS["green"]
        elif "wait" in msg.lower() or "start" in msg.lower():
            color = COLORS["yellow"]
        else:
            color = COLORS["dim"]

        line = f'<span style="color:{COLORS["dim"]}">[{ts}]</span> <span style="color:{color}">{msg}</span>'
        self.log_text.append(line)

    def _set_status(self, running):
        self.running = running
        if running:
            self.engine_val.setText("RUNNING")
            self.engine_val.setStyleSheet(f"color: {COLORS['green']}; font-size: 14px; border: none;")
            self.status_dot.setStyleSheet(f"color: {COLORS['green']}; font-size: 14px; border: none; margin-left: 6px;")
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
        else:
            self.engine_val.setText("IDLE")
            self.engine_val.setStyleSheet(f"color: {COLORS['dim']}; font-size: 14px; border: none;")
            self.status_dot.setStyleSheet(f"color: {COLORS['red']}; font-size: 14px; border: none; margin-left: 6px;")
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)

    # ─── 버튼 핸들러 (커스터마이즈) ────────────────────────

    def _on_start(self):
        self.stop_event.clear()
        self._set_status(True)

        def worker():
            try:
                self._log("Bot started!")
                counter = 0
                while not self.stop_event.is_set():
                    counter += 1
                    self._log(f"Running... count={counter}")
                    # 여기에 실제 봇 로직 구현
                    time.sleep(2)
                self._log("Bot stopped")
            except Exception as e:
                self._log(f"[!] Error: {e}")
            finally:
                self.bridge.status.emit(False)

        threading.Thread(target=worker, daemon=True).start()

    def _on_stop(self):
        self._log("Stopping...")
        self.stop_event.set()

    def _on_action(self):
        self._log("Action button clicked!")
        # 여기에 커스텀 액션 구현

    def closeEvent(self, e):
        self.stop_event.set()
        sys.stdout = self._orig_stdout
        e.accept()


# ─── 메인 ────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = TerminalBotApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
