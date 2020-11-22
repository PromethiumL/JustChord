from PyQt5.QtWidgets import QGraphicsWidget
from JustChord.gui import *


class WheelWindow(QGraphicsWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def iniUI(self):
        self.resize(500, 500);
