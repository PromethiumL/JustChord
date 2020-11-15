import traceback

from .chordwindow import *
from .staffwindow import *


class JustChordMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('JustChord')
        self.resize(1024, 512)

        """Container holds my own widgets"""
        self.container = QWidget(parent=self)
        self.container.resize(600, 600)
        self.opacity = 200  # Ranges from 0 to 255
        self.container.setStyleSheet('.QWidget {{background-color: rgb(255, 255, 255, {});}}'.format(self.opacity))
        self.container.show()
        self.chordWindow = ChordWindow(self.container, config={'keyName': 'C'})
        # self.setStyleSheet('border: 1px solid red')
        self.staffWindow = StaffWindow(self.container, config={'keyName': 'C'})
        container_layout = QHBoxLayout(self.container)
        container_layout.addWidget(self.staffWindow)
        container_layout.addWidget(self.chordWindow)
        self.container.setLayout(container_layout)

        layout = QHBoxLayout(self)
        layout.addWidget(self.container)
        # layout.setAlignment(Qt.AlignCenter)
        # layout.setStretch(0, 0)
        self.setLayout(layout)

        """This makes the UI semi-transparent"""
        self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_AlwaysStackOnTop)

        """Controls"""
        self.position_controls = []
        self.show_position_control = False
        for handle in "TL,TR,BL,BR".split(","):
            control = QWidget(self)
            control.setObjectName(handle)
            control.setFixedSize(20, 20)
            control.setStyleSheet('border: 3px solid #6f6; border-radius: 5px; background-color: #373; mouse:pointer;')
            w, h = self.width(), self.height()
            if handle == 'TL':
                control.move(0, 0)
            if handle == 'TR':
                control.move(w - 20, 0)
            if handle == 'BL':
                control.move(0, h - 20)
            if handle == 'BR':
                control.move(w - 20, h - 20)
            control.setVisible(self.show_position_control)
            self.position_controls.append(control)

        self.show()

    def togglePositionControl(self):
        print('triggered')
        self.show_position_control = not self.show_position_control
        for control in self.position_controls:
            control.setVisible(self.show_position_control)

    def contextMenuEvent(self, e):
        contextMenu = QMenu(self)
        # controls

        toggle_control = QAction('Show Resizing Controls', contextMenu, checkable=True,
                                 checked=self.show_position_control)
        toggle_control.triggered.connect(self.togglePositionControl)
        contextMenu.addAction(toggle_control)
        contextMenu.addSeparator()

        quit_btn = contextMenu.addAction('Quit')
        quit_btn.triggered.connect(lambda: QApplication.instance().quit())

        action = contextMenu.exec_(self.mapToGlobal(e.pos()))

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

    def wheelEvent(self, e: QWheelEvent):
        self.opacity += 5 if not e.angleDelta().y() < 0 else -5
        if self.opacity < 0: self.opacity = 0
        if self.opacity > 255: self.opacity = 255
        self.container.setStyleSheet('.QWidget {{background-color: rgb(255, 255, 255, {});}}'.format(self.opacity))


default_midi_port = 0


class JustChordApp(QApplication):
    def __init__(self):
        try:
            super(JustChordApp, self).__init__(sys.argv)
            self.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

            # Init MIDI
            portCount = monitor.midiIn.get_port_count()
            if portCount == 0:
                raise Exception('No midi in found. Continue?')
                # continue
            else:
                port = MidiSelectionDialog().exec()
                print('using midi port', port)
                monitor.initRtMidi(port=default_midi_port)

            # Load Font
            font_id = QFontDatabase.addApplicationFont('./assets/Gothic_A1/GothicA1-Light.ttf')
            if font_id == -1:
                raise Exception("default app font not found!")

            print(QFontDatabase.applicationFontFamilies(int(font_id)))
            font_name = QFontDatabase.applicationFontFamilies(int(font_id))[0]
            # print('css', 'QLabel {{ font: "{}"; }}'.format(font_name))
            self.setStyleSheet('.QLabel {{ font: "{}"; }}'.format(font_name))

            # Create Window
            jcMainWindow = JustChordMainWindow()

            sys.exit(self.exec_())
        except Exception as e:
            print(e)
            traceback.print_exc()


class MidiSelectionDialog(QDialog):
    def __init__(self):
        super(MidiSelectionDialog, self).__init__()
        self.setWindowTitle('MIDI In Settings')
        vlayout = QVBoxLayout(self)

        hintLabel = QLabel('Plugin your MIDI keyboard (or a virtual one) and select it below:')

        self.midiView = QListWidget(self)
        midiView = self.midiView
        midiView.addItems(self.getListItems())
        midiView.setCurrentRow(0)
        buttons = QDialogButtonBox(self)

        cancel_btn = buttons.addButton('Cancel', QDialogButtonBox.RejectRole)
        buttons.rejected.connect(self.reject)

        refresh_btn = buttons.addButton('Refresh', QDialogButtonBox.ActionRole)
        refresh_btn.clicked.connect(self.onRefresh)

        ok_btn = buttons.addButton('OK', QDialogButtonBox.AcceptRole)
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
        print('Available MIDI IN ports:')
        for i in range(ports):
            print('\t', monitor.midiIn.get_port_name(i))
        return [monitor.midiIn.get_port_name(p) for p in range(ports)]


if __name__ == '__main__':
    app = JustChordApp()
