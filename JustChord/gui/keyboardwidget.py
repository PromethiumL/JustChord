from imports import *

class KeyboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(500, 500)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    kb = KeyboardWidget()
    sys.exit(app.exec_())
