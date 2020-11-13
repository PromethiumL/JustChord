# coding:utf-8
from .imports import *


class MainWidget(QWidget):
    monitoring = False
    monitor = None

    def __init__(self):
        super().__init__()
        if not MainWidget.monitoring:
            self.initMonitor()
        self.isMouseDown = False
        self.isTransparent = False
        if self.isTransparent:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)

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

    def initMonitor(self):
        if monitor.MIDI_INITIALIZED:
            MainWidget.monitoring = True
            print('MainWidget connected to monitor.')
            MainWidget.monitor = monitor.Monitor()
            MainWidget.monitor.start()

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

    def initUI(self):
        pass
