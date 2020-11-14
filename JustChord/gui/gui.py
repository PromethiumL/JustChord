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


class JustChordApp:
    def __init__(self):
        try:
            self.app = app = QApplication(sys.argv)
            app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            monitor.initRtMidi(port=default_midi_port)

            font_id = QFontDatabase.addApplicationFont('./assets/Gothic_A1/GothicA1-Light.ttf')
            print('fontid', font_id)
            if font_id == -1:
                raise Exception("default app font not found!")

            print(QFontDatabase.applicationFontFamilies(int(font_id)))
            font_name = QFontDatabase.applicationFontFamilies(int(font_id))[0]
            print('css', 'QLabel {{ font: "{}"; }}'.format(font_name))
            app.setStyleSheet('.QLabel {{ font: "{}"; }}'.format(font_name))

            jcMainWindow = JustChordMainWindow()

            sys.exit(self.app.exec_())
        except Exception as e:
            print(e)
            traceback.print_exc()


def main():
    app = JustChordApp()


if __name__ == '__main__':
    main()
