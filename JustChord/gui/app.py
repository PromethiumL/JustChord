import traceback

from JustChord.gui.chordwindow import *
from JustChord.gui.staffwindow import *
from JustChord.gui.keyboardwidget import *


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
        self.chordWindow = ChordWindow(self.container)
        # self.setStyleSheet('border: 1px solid red')
        self.staffWindow = StaffWindow(self.container)
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

        """Size Grips"""
        self.size_grips = []
        self.show_size_grips = True
        for position in "TL,TR,BL,BR".split(","):
            grip = QSizeGrip(self)
            grip.mouseMoveEvent = lambda *args: None
            grip.setObjectName(position)
            grip.setFixedSize(20, 20)
            # grip.setStyleSheet('border: 3px solid #6f6; border-radius: 5px; background-color: #373; mouse:pointer;')
            w, h = self.width(), self.height()
            if position == 'TL':
                grip.move(0, 0)
            if position == 'TR':
                grip.move(w - 20, 0)
            if position == 'BL':
                grip.move(0, h - 20)
            if position == 'BR':
                grip.move(w - 20, h - 20)
            grip.setVisible(self.show_size_grips)
            self.size_grips.append(grip)

        self.show()

    def toggleSizeGrips(self):
        print('triggered')
        self.show_size_grips = not self.show_size_grips
        for control in self.size_grips:
            control.setVisible(self.show_size_grips)

    def contextMenuEvent(self, e):
        contextMenu = QMenu(self)
        # controls

        toggle_control = QAction('Show Size Grips', contextMenu, checkable=True,
                                 checked=self.show_size_grips)
        toggle_control.triggered.connect(self.toggleSizeGrips)
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

    def resizeEvent(self, e):
        for grip in self.size_grips:
            w, h = self.width(), self.height()
            if grip.objectName() == 'TL':
                grip.move(0, 0)
            if grip.objectName() == 'TR':
                grip.move(w - 20, 0)
            if grip.objectName() == 'BL':
                grip.move(0, h - 20)
            if grip.objectName() == 'BR':
                grip.move(w - 20, h - 20)
            # grip.setVisible(self.show_size_grips)


default_midi_port = 0


class JustChordApp(QApplication):
    select_midi_mort_signal = pyqtSignal(str)

    def __init__(self):
        try:
            super(JustChordApp, self).__init__(sys.argv)
            self.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            # apply_stylesheet(self, theme='light_cyan.xml')

            # Init MIDI
            self.midi_in_wizard(force=False)
            # self.select_midi_mort_signal.connect(self.midi_in_wizard)

            # Load Font
            font_id = QFontDatabase.addApplicationFont('./assets/Gothic_A1/GothicA1-Regular.ttf')
            if font_id != -1:
                print(QFontDatabase.applicationFontFamilies(int(font_id)))
                # font_name = QFontDatabase.applicationFontFamilies(int(font_id))[0]
                # print('css', 'QLabel {{ font: "{}"; }}'.format(font_name))
                self.setStyleSheet('.QLabel { font: 24pt "Gothic A1"; }')
            else:
                print("default app font not found!")
                self.setStyleSheet('.QLabel {{ font: "Arial"; }}')

            # Create Window
            jcMainWindow = JustChordMainWindow()

            # Keyboard
            jcKeyboardWidget = KeyboardWidget()
            jcKeyboardWidget.move(jcMainWindow.pos().x() + (jcMainWindow.width() - jcKeyboardWidget.width()) // 2,
                                  jcMainWindow.pos().y() + jcMainWindow.height())
            widget.Widget.monitor.trigger.connect(jcKeyboardWidget.updateNotes)

            sys.exit(self.exec_())

        except Exception as e:
            print(e)
            traceback.print_exc()

    def midi_in_wizard(self, force=False):
        # print('MidiInSettings')
        portCount = monitor.midiIn.get_port_count()
        port = MidiSelectionDialog().exec()
        if port >= 0:
            print('using midi port', port)
            monitor.initRtMidi(port=port)
        elif force:
            popup = QMessageBox()
            popup.setWindowTitle('Alert')
            popup.setText('No MIDI input device is selected, which is currently not supported.')
            popup.setIcon(QMessageBox.Information)
            popup.addButton('Exit', QMessageBox.AcceptRole)
            popup.exec()
            sys.exit(0)
        else:
            monitor.initRtMidi(port=None)


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


def main():
    app = JustChordApp()


if __name__ == '__main__':
    main()
