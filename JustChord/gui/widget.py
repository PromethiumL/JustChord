# coding:utf-8
from JustChord.gui.imports import *


class Widget(QFrame):
    monitoring = False
    monitor = None

    def __init__(self):
        super().__init__()
        self.initMonitor()
        self._initUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_Q:
            QApplication.instance().quit()

    def mousePressEvent(self, e):
        if e.button == Qt.LeftButton:
            self.isMouseDown = True
        self.p = e.globalPos()

    def mouseMoveEvent(self, e):
        p = e.globalPos()
        self.move(self.pos() + p - self.p)
        self.p = p

    def mouseReleaseEvent(self, e):
        self.isMouseDown = False
        # self.setStyleSheet('.Widget {background: #888;}')

    def initMonitor(self):
        if not Widget.monitoring:
            Widget.monitoring = True
            print('Widget connected to monitor.')
            Widget.monitor = monitor.Monitor()
            Widget.monitor.start()
            if not monitor.MIDI_INITIALIZED:
                print('WARNING: No MIDI device is selected')

    def center(self):
        self.screenX = QApplication.desktop().width()
        self.screenY = QApplication.desktop().height()
        self.move(self.screenX / 2, self.screenY / 2)

    def moveWindows(self, x, y):
        # print(self.pos())
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
