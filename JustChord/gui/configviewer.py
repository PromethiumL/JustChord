from JustChord.gui.imports import *
from JustChord.gui.staffwindow import StaffWindowConfig


class MySettingsTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(30, 4, parent)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)


class ConfigViewer(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()

    def initUI(self):
        vbox = QVBoxLayout(self)
        myTable1 = MySettingsTable()
        myTable1.setParent(self)
        btns = QDialogButtonBox(self)
        btns.addButton('Apply', QDialogButtonBox.ApplyRole)
        btns.addButton('Cancel', QDialogButtonBox.NoRole)

        vbox.addWidget(myTable1)
        vbox.addWidget(btns)
        self.setLayout(vbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    configViewer = ConfigViewer()
    sys.exit(app.exec_())
