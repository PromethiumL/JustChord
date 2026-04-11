import sys
import traceback
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFontDatabase, QWheelEvent
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMenu,
    QMessageBox,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)

import JustChord.gui.monitor as monitor
from JustChord.gui.chordwindow import ChordWindow
from JustChord.gui.keyboardwidget import KeyboardWidget
from JustChord.gui.staffwindow import StaffWindow
from JustChord.gui.widget import Widget

FONT_PATH = "./assets/Gothic_A1/GothicA1-Regular.ttf"


@dataclass
class MainWindowConfig:
    window_width: int = 1024
    window_height: int = 512
    default_opacity: int = 255
    min_opacity: int = 0
    max_opacity: int = 255
    opacity_step: int = 5
    grip_size: int = 20
    default_font_size: int = 24


class JustChordMainWindow(QWidget):
    def __init__(self, config=None):
        super().__init__()
        self.config = config or MainWindowConfig()
        self.setWindowTitle("JustChord")
        self.resize(self.config.window_width, self.config.window_height)

        self.container = QWidget(parent=self)
        self.opacity = self.config.default_opacity
        self.container.setStyleSheet(".QWidget {{background-color: rgba(255, 255, 255, {});}}".format(self.opacity))
        self.container.show()
        self.chordWindow = ChordWindow(self.container)
        self.staffWindow = StaffWindow(self.container)
        container_layout = QHBoxLayout(self.container)
        container_layout.addWidget(self.staffWindow)
        container_layout.addWidget(self.chordWindow)
        self.container.setLayout(container_layout)

        layout = QHBoxLayout(self)
        layout.addWidget(self.container)
        self.setLayout(layout)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.size_grips = []
        self.show_size_grips = True
        for pos in "TL,TR,BL,BR".split(","):
            grip = QSizeGrip(self)
            grip.mouseMoveEvent = lambda *args: None
            grip.setObjectName(pos)
            gs = self.config.grip_size
            grip.setFixedSize(gs, gs)
            w, h = self.width(), self.height()
            if pos == "TL":
                grip.move(0, 0)
            if pos == "TR":
                grip.move(w - gs, 0)
            if pos == "BL":
                grip.move(0, h - gs)
            if pos == "BR":
                grip.move(w - gs, h - gs)
            grip.setVisible(self.show_size_grips)
            self.size_grips.append(grip)

        self.show()

    def toggleSizeGrips(self):
        self.show_size_grips = not self.show_size_grips
        for control in self.size_grips:
            control.setVisible(self.show_size_grips)

    def contextMenuEvent(self, e):
        contextMenu = QMenu(self)
        toggle_control = QAction("Show Size Grips", contextMenu, checkable=True, checked=self.show_size_grips)
        toggle_control.triggered.connect(self.toggleSizeGrips)
        contextMenu.addAction(toggle_control)
        contextMenu.addSeparator()

        quit_btn = contextMenu.addAction("Quit")
        quit_btn.triggered.connect(lambda: QApplication.instance().quit())

        contextMenu.exec(self.mapToGlobal(e.pos()))

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.isMouseDown = True
        self.p = e.globalPosition()

    def mouseMoveEvent(self, e):
        p = e.globalPosition()
        self.move(self.pos() + (p - self.p).toPoint())
        self.p = p

    def mouseReleaseEvent(self, e):
        self.isMouseDown = False

    def wheelEvent(self, e: QWheelEvent):
        step = self.config.opacity_step
        self.opacity += step if e.angleDelta().y() > 0 else -step
        self.opacity = max(self.config.min_opacity, min(self.config.max_opacity, self.opacity))
        self.container.setStyleSheet(".QWidget {{background-color: rgba(255, 255, 255, {});}}".format(self.opacity))

    def resizeEvent(self, e):
        gs = self.config.grip_size
        for grip in self.size_grips:
            w, h = self.width(), self.height()
            if grip.objectName() == "TL":
                grip.move(0, 0)
            if grip.objectName() == "TR":
                grip.move(w - gs, 0)
            if grip.objectName() == "BL":
                grip.move(0, h - gs)
            if grip.objectName() == "BR":
                grip.move(w - gs, h - gs)


class JustChordApp(QApplication):
    def __init__(self):
        try:
            super().__init__(sys.argv)

            self.midi_in_wizard(force=False)

            font_id = QFontDatabase.addApplicationFont(FONT_PATH)
            if font_id != -1:
                self.setStyleSheet(f'.QLabel {{ font: {MainWindowConfig.default_font_size}pt "Gothic A1"; }}')
            else:
                self.setStyleSheet('.QLabel { font: "Arial"; }')

            # Create Window
            jcMainWindow = JustChordMainWindow()

            # Keyboard
            jcKeyboardWidget = KeyboardWidget()
            jcKeyboardWidget.move(
                jcMainWindow.pos().x() + (jcMainWindow.width() - jcKeyboardWidget.width()) // 2,
                jcMainWindow.pos().y() + jcMainWindow.height(),
            )
            Widget.monitor.trigger.connect(jcKeyboardWidget.updateNotes)

            sys.exit(self.exec())

        except Exception as e:
            print(e)
            traceback.print_exc()

    def midi_in_wizard(self, force=False):
        port = MidiSelectionDialog().exec()
        if port >= 0:
            monitor.initRtMidi(port=port)
        elif force:
            popup = QMessageBox()
            popup.setWindowTitle("Alert")
            popup.setText("No MIDI input device is selected, which is currently not supported.")
            popup.setIcon(QMessageBox.Icon.Information)
            popup.addButton("Exit", QMessageBox.ButtonRole.AcceptRole)
            popup.exec()
            sys.exit(0)
        else:
            monitor.initRtMidi(port=None)


class MidiSelectionDialog(QDialog):
    def __init__(self):
        super(MidiSelectionDialog, self).__init__()
        self.setWindowTitle("MIDI In Settings")
        vlayout = QVBoxLayout(self)

        hintLabel = QLabel("Plugin your MIDI keyboard (or a virtual one) and select it below:")

        self.midiView = QListWidget(self)
        midiView = self.midiView
        midiView.addItems(self.getListItems())
        midiView.setCurrentRow(0)
        buttons = QDialogButtonBox(self)

        buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.rejected.connect(self.reject)

        refresh_btn = buttons.addButton("Refresh", QDialogButtonBox.ButtonRole.ActionRole)
        refresh_btn.clicked.connect(self.onRefresh)

        ok_btn = buttons.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
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
        return [monitor.midiIn.get_port_name(p) for p in range(ports)]


def main():
    JustChordApp()


if __name__ == "__main__":
    main()
