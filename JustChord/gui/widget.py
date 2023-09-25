# coding:utf-8
from PyQt6 import QtGui
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QFrame

import JustChord.gui.monitor as monitor


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
        if e.button == Qt.MouseButton.LeftButton:
            self.isMouseDown = True
        self.p = e.globalPosition()

    def mouseMoveEvent(self, e: QMouseEvent):
        p = e.globalPosition()
        self.move(self.pos() + (p - self.p).toPoint())
        self.p = p

    def mouseReleaseEvent(self, e):
        self.isMouseDown = False
        # self.setStyleSheet('.Widget {background: #888;}')

    def initMonitor(self):
        if not Widget.monitoring:
            Widget.monitoring = True
            print("Widget connected to monitor.")
            Widget.monitor = monitor.Monitor()
            Widget.monitor.start()
            if not monitor.MIDI_INITIALIZED:
                print("WARNING: No MIDI device is selected")

    def center(self):
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        self.move(cp.x(), cp.y())

    def moveWindows(self, x, y):
        # print(self.pos)
        p = self.pos()
        newx = p.x() + x
        newy = p.y() + y
        if newx <= 10:
            newx = 10
        if newy <= 10:
            newy = 10
        # if newx + self.width() >= self.screenX:
        # 	newx = self.screenX - self.width()
        # if newy + self.height() >= self.screenY:
        # 	newy = self.screenY - self.height()
        if newx >= (self.screenX - 10):
            newx = self.screenX - 10
        if newy >= (self.screenY - 10):
            newy = self.screenY - 10

        self.move(newx, newy)

    def _initUI(self):
        self.isMouseDown = False
        self.opacity = 1.0
        # if self.isTransparent:
        #     self.setWindowFlag(Qt.FramelessWindowHint)
