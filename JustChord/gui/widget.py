import logging

from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QFrame

import JustChord.gui.monitor as monitor

_log = logging.getLogger("justchord.ui")


class Widget(QFrame):
    monitoring = False
    monitor = None

    def __init__(self):
        super().__init__()
        self.initMonitor()
        self._initUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_Q:
            QApplication.instance().quit()

    def mousePressEvent(self, e: QMouseEvent):
        _log.debug("Widget(%s).mousePressEvent button=%s", self.__class__.__name__, e.button())
        if e.button() == Qt.MouseButton.LeftButton:
            self.isMouseDown = True
            self.p = e.globalPosition()

    def mouseMoveEvent(self, e: QMouseEvent):
        if not self.isMouseDown:
            return
        _log.debug("Widget(%s).mouseMoveEvent (dragging)", self.__class__.__name__)
        p = e.globalPosition()
        self.move(self.pos() + (p - self.p).toPoint())
        self.p = p

    def mouseReleaseEvent(self, e):
        _log.debug("Widget(%s).mouseReleaseEvent button=%s", self.__class__.__name__, e.button())
        if e.button() == Qt.MouseButton.LeftButton:
            self.isMouseDown = False

    def initMonitor(self):
        if not Widget.monitoring:
            Widget.monitoring = True
            Widget.monitor = monitor.Monitor()
            Widget.monitor.start()
            if not monitor.MIDI_INITIALIZED:
                print("WARNING: No MIDI device is selected")

    def center(self):
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        self.move(cp.x(), cp.y())

    def _initUI(self):
        self.isMouseDown = False
