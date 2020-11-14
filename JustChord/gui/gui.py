import traceback

from .chordwindow import *
from .staffwindow import *


class JustChordMainWindow(MainWidget):
    def __init__(self):
        super().__init__()
        self.resize(1024, 512)
        self.layout = QHBoxLayout()
        self.chordWindow = ChordWindow({'keyName': 'C'})
        self.staffWindow = StaffWindow({'keyName': 'C'})
        self.layout.addWidget(self.staffWindow)
        self.layout.addWidget(self.chordWindow)
        # self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)
        self.show()


default_midi_port = 0

def main():
    try:
        justChordApp = QApplication(sys.argv)
        justChordApp.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        monitor.initRtMidi(port=default_midi_port)

        jcMainWindow = JustChordMainWindow()
        sys.exit(justChordApp.exec_())
    except Exception as e:
        print(e)
        traceback.print_exc()


if __name__ == '__main__':
    main()
