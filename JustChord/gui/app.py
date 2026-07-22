import logging
import sys
from dataclasses import dataclass

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QFontDatabase, QPainter, QWheelEvent
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMenu,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)

import JustChord.gui.monitor as monitor
from JustChord.core import config
from JustChord.gui.chordwindow import ChordWindow
from JustChord.gui.keyboardwidget import KeyboardWidget
from JustChord.gui.staffwindow import StaffWindow
from JustChord.gui.widget import Widget

_log = logging.getLogger("justchord.ui")

FONT_PATH = "./assets/Gothic_A1/GothicA1-Regular.ttf"


@dataclass
class MainWindowConfig:
    window_width: int = 1024
    window_height: int = 512
    default_opacity: int = 255
    min_opacity: int = 0
    max_opacity: int = 255
    opacity_step: int = 5
    grip_size: int = 20
    default_font_size: int = 24

    @classmethod
    def from_config(cls):
        win = config.section("window")
        return cls(
            window_width=win.get("width", 1024),
            window_height=win.get("height", 512),
            default_opacity=win.get("default_opacity", 255),
            opacity_step=win.get("opacity_step", 5),
            grip_size=win.get("grip_size", 20),
            default_font_size=win.get("default_font_size", 24),
        )


class _BackgroundWidget(QWidget):
    """Container that paints its own background without stylesheet (avoids layout recalc)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_alpha = 255

    def setBgAlpha(self, alpha):
        self._bg_alpha = alpha
        self.update()  # repaint only, no layout recalc

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 255, self._bg_alpha))
        painter.end()


class JustChordMainWindow(QWidget):
    def __init__(self, config=None):
        super().__init__()
        self.config = config or MainWindowConfig.from_config()
        self.isMouseDown = False
        self.setWindowTitle("JustChord")
        self.resize(self.config.window_width, self.config.window_height)

        self.container = _BackgroundWidget(parent=self)
        self.opacity = self.config.default_opacity
        self.container.setBgAlpha(self.opacity)
        self.container.show()
        self.chordWindow = ChordWindow(self.container)
        self.staffWindow = StaffWindow(self.container)
        container_layout = QHBoxLayout(self.container)
        container_layout.addWidget(self.staffWindow)
        container_layout.addWidget(self.chordWindow)
        self.container.setLayout(container_layout)

        layout = QHBoxLayout(self)
        layout.addWidget(self.container)
        self.setLayout(layout)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.size_grips = []
        self.show_size_grips = True
        for pos in "TL,TR,BL,BR".split(","):
            grip = QSizeGrip(self)
            grip.mouseMoveEvent = lambda *args: None
            grip.setObjectName(pos)
            gs = self.config.grip_size
            grip.setFixedSize(gs, gs)
            w, h = self.width(), self.height()
            if pos == "TL":
                grip.move(0, 0)
            if pos == "TR":
                grip.move(w - gs, 0)
            if pos == "BL":
                grip.move(0, h - gs)
            if pos == "BR":
                grip.move(w - gs, h - gs)
            grip.setVisible(self.show_size_grips)
            self.size_grips.append(grip)

        self.show()

    def toggleSizeGrips(self):
        self.show_size_grips = not self.show_size_grips
        for control in self.size_grips:
            control.setVisible(self.show_size_grips)

    def contextMenuEvent(self, e):
        _log.debug("MainWindow.contextMenuEvent")
        contextMenu = QMenu(self)
        toggle_control = QAction("Show Size Grips", contextMenu, checkable=True, checked=self.show_size_grips)
        toggle_control.triggered.connect(self.toggleSizeGrips)
        contextMenu.addAction(toggle_control)
        contextMenu.addSeparator()

        quit_btn = contextMenu.addAction("Quit")
        quit_btn.triggered.connect(lambda: QApplication.instance().quit())

        contextMenu.exec(self.mapToGlobal(e.pos()))

    def mousePressEvent(self, e):
        _log.debug("MainWindow.mousePressEvent button=%s", e.button())
        if e.button() == Qt.MouseButton.LeftButton:
            self.isMouseDown = True
            self.p = e.globalPosition()

    def mouseMoveEvent(self, e):
        if not self.isMouseDown:
            return
        _log.debug("MainWindow.mouseMoveEvent (dragging)")
        p = e.globalPosition()
        self.move(self.pos() + (p - self.p).toPoint())
        self.p = p

    def mouseReleaseEvent(self, e):
        _log.debug("MainWindow.mouseReleaseEvent button=%s", e.button())
        if e.button() == Qt.MouseButton.LeftButton:
            self.isMouseDown = False

    def wheelEvent(self, e: QWheelEvent):
        delta = e.angleDelta().y()
        if delta == 0:
            return
        _log.debug("MainWindow.wheelEvent delta=%s", delta)
        step = self.config.opacity_step
        self.opacity += step if delta > 0 else -step
        self.opacity = max(self.config.min_opacity, min(self.config.max_opacity, self.opacity))
        self.container.setBgAlpha(self.opacity)

    def resizeEvent(self, e):
        _log.debug("MainWindow.resizeEvent %dx%d -> %dx%d", e.oldSize().width(), e.oldSize().height(), e.size().width(), e.size().height())
        gs = self.config.grip_size
        for grip in self.size_grips:
            w, h = self.width(), self.height()
            if grip.objectName() == "TL":
                grip.move(0, 0)
            if grip.objectName() == "TR":
                grip.move(w - gs, 0)
            if grip.objectName() == "BL":
                grip.move(0, h - gs)
            if grip.objectName() == "BR":
                grip.move(w - gs, h - gs)


class Toast(QLabel):
    """A temporary notification that fades out after a delay."""

    FADE_DURATION_MS = 800

    def __init__(self, text, parent, duration_ms=6000):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setStyleSheet(
            "QLabel {"
            "  background-color: rgba(0, 0, 0, 180);"
            "  color: white;"
            "  padding: 12px 16px;"
            "  border-radius: 8px;"
            "  font-size: 13pt;"
            "}"
        )
        self.adjustSize()
        self.setFixedWidth(min(parent.width() - 40, 480))
        self.adjustSize()
        self.move(
            (parent.width() - self.width()) // 2,
            parent.height() - self.height() - 40,
        )

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_anim.setDuration(self.FADE_DURATION_MS)
        self._fade_anim.setStartValue(1.0)
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_anim.finished.connect(self.deleteLater)

        self.show()
        QTimer.singleShot(duration_ms, self._fade_anim.start)


class JustChordApp(QApplication):
    def __init__(self):
        try:
            super().__init__(sys.argv)
            self._no_midi_hint = False

            self.midi_in_wizard(force=False)

            font_id = QFontDatabase.addApplicationFont(FONT_PATH)
            if font_id != -1:
                self.setStyleSheet(f'.QLabel {{ font: {MainWindowConfig.default_font_size}pt "Gothic A1"; }}')
            else:
                self.setStyleSheet('.QLabel { font: "Arial"; }')

            jcMainWindow = JustChordMainWindow()

            jcKeyboardWidget = KeyboardWidget()
            jcKeyboardWidget.move(
                jcMainWindow.pos().x() + (jcMainWindow.width() - jcKeyboardWidget.width()) // 2,
                jcMainWindow.pos().y() + jcMainWindow.height(),
            )
            Widget.monitor.trigger.connect(jcKeyboardWidget.updateNotes)

            if self._no_midi_hint:
                Toast(
                    "No MIDI device detected. Use the virtual keyboard below to play "
                    "(spacebar = sustain pedal). Right-click the chord display to "
                    "select a MIDI device later.",
                    jcMainWindow,
                )

            sys.exit(self.exec())

        except Exception:
            _log.exception("Fatal error in JustChordApp")

    def midi_in_wizard(self, force=False):
        if monitor.midiIn.get_port_count() == 0 and not force:
            monitor.initRtMidi(port=None)
            self._no_midi_hint = True
            return
        port = MidiSelectionDialog().exec()
        if port >= 0:
            monitor.initRtMidi(port=port)
        else:
            monitor.initRtMidi(port=None)


class MidiSelectionDialog(QDialog):
    def __init__(self):
        super(MidiSelectionDialog, self).__init__()
        self.setWindowTitle("MIDI In Settings")
        vlayout = QVBoxLayout(self)

        hintLabel = QLabel("Plugin your MIDI keyboard (or a virtual one) and select it below:")

        self.midiView = QListWidget(self)
        midiView = self.midiView
        midiView.addItems(self.getListItems())
        midiView.setCurrentRow(0)
        buttons = QDialogButtonBox(self)

        buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.rejected.connect(self.reject)

        refresh_btn = buttons.addButton("Refresh", QDialogButtonBox.ButtonRole.ActionRole)
        refresh_btn.clicked.connect(self.onRefresh)

        ok_btn = buttons.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.accepted.connect(self.accept)
        ok_btn.setDefault(True)

        vlayout.addWidget(hintLabel)
        vlayout.addWidget(midiView)
        vlayout.addWidget(buttons)
        self.setLayout(vlayout)

    def onRefresh(self):
        self.midiView.clear()
        self.midiView.addItems(self.getListItems())

    def accept(self):
        self.done(self.midiView.currentRow())

    def reject(self):
        self.done(-1)

    def getListItems(self):
        ports = monitor.midiIn.get_port_count()
        return [monitor.midiIn.get_port_name(p) for p in range(ports)]


def main():
    from JustChord.log import setup
    setup()
    JustChordApp()


if __name__ == "__main__":
    main()
