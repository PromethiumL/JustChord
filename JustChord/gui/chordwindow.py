# coding:utf-8
from JustChord.gui.widget import *
from JustChord.core import chord
import copy

CHORDLABEL_TIP = """
Usage:
    Move: Arrow keys
    Color: 'C' (computer keyboard)
    Quit: Esc
    # Font: 'F'
    # Toggle Flat or Sharp: S
    Toggle Roman style chord: N
    Clear all notes: R
    Show/Hidden rest chords: H
    Show/Hidden current mode label: L
"""


@dataclass
class ChordWindowConfig:
    allow_slash_chord: bool = True
    chord_font_size: int = 40
    chord_name_gap: int = 10
    chord_type_font_scalar: float = 0.7
    show_rest_chords: bool = True
    max_rest_chords: int = 5
    rest_chords_font_scalar: float = 0.5
    rest_chords_type_font_scalar: float = 0.8
    default_key_name: str = 'C'
    use_roman_notation: bool = False
    show_key_label: bool = True
    auto_key_detection: bool = True


class ChordWindow(Widget):
    def __init__(self, parent, config=None):
        super().__init__()
        self.setParent(parent)
        self.config = config
        if self.config is None:
            self.config = ChordWindowConfig()
        self.keyName = self.config.default_key_name
        self.isSharpKey = (self.keyName in chord.KEY_LIST[0])
        self.connectMonitor()
        self.initUI()
        self.show()

    def connectMonitor(self):
        Widget.monitor.trigger.connect(self.updateChordLabel)

    def toggleMoreResults(self, flag=None):
        if flag is not None:
            self.config.show_rest_chords = True if flag else False
        if not self.config.show_rest_chords:
            for i in range(1, self.config.max_rest_chords + 1):
                self.chord_labels[i][0].setText('')
                self.chord_labels[i][1].setText('')
        self.updateKeyLabel()

    def toggleKeyLabel(self):
        self.config.show_key_label ^= True  # Toggle
        self.updateKeyLabel()

    def toggleRomanNotation(self):
        self.config.use_roman_notation ^= True  # Toggle
        self.updateKeyLabel()

    def fontDialog(self):
        font: QFont
        font, valid = QFontDialog.getFont()
        font_name = font.toString().split(',')[0]
        if valid:
            print(font.pixelSize())
            for idx, lbs in enumerate(self.chord_labels):
                lbs[0].setStyleSheet('font-size: {}pt;'.format(
                    self.config.chord_font_size * (1 if idx == 0 else self.config.rest_chords_font_scalar)))
                lbs[1].setStyleSheet('font-size: {}pt;'.format(
                    self.config.chord_font_size * self.config.chord_type_font_scalar * (
                        1 if idx == 0 else self.config.rest_chords_type_font_scalar)))
            self.key_label.setStyleSheet(
                'font-size: {}pt;'.format(int(self.config.chord_font_size * self.config.rest_chords_font_scalar)))
            self.setStyleSheet('QLabel {{ font-family: "{}"; }}'.format(font_name))

    def textColorSettingsDialog(self):
        col = QColorDialog.getColor()
        if col.isValid():
            pl = QPalette()
            pl.setColor(QPalette.WindowText, col)
            for l in self.chord_labels:
                l[0].setPalette(pl)
                l[1].setPalette(pl)
            pl.setColor(QPalette.WindowText, col.darker(150))
            self.key_label.setPalette(pl)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.instance().quit()

        if event.key() == Qt.Key_N:
            self.config.use_roman_notation = not self.config.use_roman_notation

    def setKey(self, n):
        self.keyName = chord.getKeyName(n, self.isSharpKey)

    def updateKeyLabel(self):
        self.key_label.move(0,
                            self.chord_labels[-1 if self.config.show_rest_chords else 0][0].pos().y()
                            + self.chord_labels[-1 if self.config.show_rest_chords else 0][0].height() + 10
                            )
        self.key_label.setVisible(self.config.show_key_label)
        self.key_label.setText('Current Key: ' + self.keyName)
        self.key_label.adjustSize()

    def updateChordLabel(self):
        try:
            self.keyName = monitor.KeyDetector.currentKey
            self.updateKeyLabel()
            l = len(monitor.currentChords)
            for i in range(1 + self.config.max_rest_chords):
                if i < l:
                    chordObj = copy.deepcopy(monitor.currentChords[i])
                    # chordObj = monitor.currentChords[i]
                    chordObj.updateName(self.keyName, self.config.use_roman_notation)
                lbs = self.chord_labels[i]
                # lbs[0].setText('' if i >= l else ((c.name[0]) if ALLOW_SLASH_CHORD else c.get_base_name()))
                lbs[0].setText('' if i >= l else (
                    chordObj.name[0] if self.config.allow_slash_chord else chordObj.get_base_name()))
                lbs[0].adjustSize()
                lbs[1].move(lbs[0].x() + lbs[0].width() + self.config.chord_name_gap,
                            lbs[0].y() - 5 if self.config.use_roman_notation else lbs[0].y() + lbs[0].height() - lbs[
                                1].height())
                lbs[1].setText('' if i >= l else chordObj.name[1])
                lbs[1].adjustSize()
                if not self.config.show_rest_chords:
                    break

            self.update()
        except Exception as e:
            print(e)

    def initUI(self):
        self.resize(800, 600)
        self.center()
        # self.setWindowOpacity(0.7)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)
        # self.setStyleSheet('border: 1px solid white')
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # self.setStyleSheet("background:transparent;")
        self.pl = QPalette()
        self.pl.setColor(QPalette.WindowText, QColor(50, 50, 50))
        self.pl_darker = QPalette()
        self.pl_darker.setColor(QPalette.WindowText,
                                QColor(50, 50, 50).darker(200))
        self.setPalette(self.pl)
        self.chord_labels = []

        for i in range(self.config.max_rest_chords + 1):
            lb = QLabel('', self)
            lb2 = QLabel('', self)
            self.chord_labels.append([lb, lb2])

        for lbs in self.chord_labels:
            # the best chord's labels
            if self.chord_labels.index(lbs) == 0:
                lbs[0].setText('Chord...')
                lbs[0].setStyleSheet(f'font-size: {self.config.chord_font_size}pt;')
                lbs[0].setAlignment(Qt.AlignLeft)
                lbs[0].adjustSize()
                lbs[0].setPalette(self.pl)
                # lbs[0].setToolTip(CHORDLABEL_TIP)

                lbs[1].setStyleSheet(
                    f'font-size: {self.config.chord_font_size * self.config.chord_type_font_scalar}pt;')
                lbs[1].setAlignment(Qt.AlignLeft)
                lbs[1].adjustSize()
                # lbs[1].setToolTip(CHORDLABEL_TIP)
                lbs[1].setPalette(self.pl)
                lbs[1].move(
                    lbs[0].x() + lbs[0].width() + self.config.chord_name_gap,
                    lbs[0].y() + lbs[0].height() - lbs[1].height()
                )
            else:
                idx = self.chord_labels.index(lbs)
                prev_lbs = self.chord_labels[idx - 1]
                font_size = self.config.chord_font_size * self.config.rest_chords_font_scalar
                lbs[0].setStyleSheet(f'font-size: {font_size}pt;')
                lbs[0].setAlignment(Qt.AlignLeft)
                lbs[0].adjustSize()
                lbs[0].setToolTip(CHORDLABEL_TIP)
                lbs[0].setPalette(self.pl)
                lbs[0].move(0, prev_lbs[0].y() +
                            prev_lbs[0].height() + (10 if idx == 1 else 0))
                lbs[1].setStyleSheet(f'font-size: {font_size * self.config.rest_chords_type_font_scalar}pt;')
                lbs[1].setAlignment(Qt.AlignLeft)
                lbs[1].adjustSize()
                lbs[1].setToolTip(CHORDLABEL_TIP)
                lbs[1].setPalette(self.pl)
                lbs[1].move(
                    lbs[0].x() + lbs[0].width() + self.config.chord_name_gap,
                    lbs[0].y() + lbs[0].height() - lbs[1].height()
                )
            # lbs[1].setFrameShape(QFrame.Panel)
            # lbs[1].setFrameShadow(QFrame.Sunken)
            # lbs[1].setLineWidth(1)

        self.key_label = QLabel(self.keyName, self)
        self.updateKeyLabel()
        self.key_label.setStyleSheet(
            f'font-size: {int(self.config.chord_font_size * self.config.rest_chords_font_scalar)}pt;')
        self.key_label.setPalette(self.pl)
        self.key_label.adjustSize()

        # self.setStyleSheet('.ChordWindow {border: 2px solid black;background-color: #333}')
        # self.setBackgroundRole(QPalette.Background)
        self.show()

    def keyNameClicked(self, keyName):
        self.keyName = keyName
        self.config.auto_key_detection = False
        self.updateKeyLabel()

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)
        # Color settings
        colorAction = contextMenu.addAction("Text Color...")
        colorAction.triggered.connect(self.textColorSettingsDialog)

        # Font
        fontAction = contextMenu.addAction("Font...")
        fontAction.triggered.connect(self.fontDialog)

        contextMenu.addSeparator()

        # Results
        moreResultsAction = contextMenu.addAction(
            "Hide More Results" if self.config.show_rest_chords else "Show More Results"
        )
        moreResultsAction.triggered.connect(lambda: self.toggleMoreResults(not self.config.show_rest_chords))

        # Key Label
        toggleKeyLabel = QAction('Show Key Label', parent=contextMenu, checkable=True,
                                 checked=self.config.show_key_label)
        contextMenu.addAction(toggleKeyLabel)
        toggleKeyLabel.triggered.connect(self.toggleKeyLabel)

        toggleRomanNotation = QAction('Use Roman Notation', parent=contextMenu, checkable=True,
                                 checked=self.config.use_roman_notation)
        contextMenu.addAction(toggleRomanNotation)
        toggleRomanNotation.triggered.connect(self.toggleRomanNotation)

        contextMenu.addSeparator()

        # KeySettings
        keyMenu = contextMenu.addMenu("Key Settings")
        autoDetection = QAction("Auto Detection", keyMenu, checkable=True, checked=self.config.auto_key_detection)
        autoDetection.triggered.connect(lambda: self.__setattr__("config.auto_key_detection", True))
        keyMenu.addAction(autoDetection)

        for k in "Gb,Db,Ab,Eb,Bb,F,C,G,D,A,E,B,F#".split(','):
            action = QAction(k, keyMenu, checkable=True,
                             checked=(k == self.keyName and not self.config.auto_key_detection))
            action.triggered.connect(lambda checked, name=k: self.keyNameClicked(name))
            keyMenu.addAction(action)

        contextMenu.addSeparator()

        midi_settings = contextMenu.addAction('Midi in Device...')
        midi_settings.triggered.connect(lambda: QApplication.instance().midi_in_wizard())

        # Quit
        quit_btn = contextMenu.addAction('Quit')
        quit_btn.triggered.connect(lambda: QApplication.instance().quit())

        action = contextMenu.exec_(self.mapToGlobal(event.pos()))

    # ---------------
    #
    #
    # # if action == colorAction:
    # #     self.textColorSettingsDialog()
    # # if action == moreResultsAction:
    # #     self.toggleMoreResults(not self.config.show_rest_chords)
    # if action in keyMenu.actions():
    #     if action.text() == "Auto Detection":
    #         self.config.auto_key_detection = True
    #     else:
    #         self.keyName = action.text()
    #         self.config.auto_key_detection = False
    #         self.updateKeyLabel()
