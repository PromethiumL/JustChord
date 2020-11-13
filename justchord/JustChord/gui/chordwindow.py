# coding:utf-8
from .mainwidget import *
from ..core import chord
import copy

# import sys
# import os
# sys.path.insert(1, os.path.join(sys.path[0], '..'))

CHORDLABEL_TIP = """
Usage:
    Move: Arrow keys
    Color: 'C' (computer keyboard)
    Quit: Esc
    Font: 'F'
    Toggle Flat or Sharp: S
    Toggle Roman style chord: N
    Clear all notes: R
    Show/Hidden rest chords: H
    Show/Hidden current mode label: L
"""


class ChordWindow(MainWidget):
    DEFAULT_CONFIG = {
        'allowSlashChord': True,
        'chordFontSize': 40,
        'chordNameGap': 10,
        'chordTypeScaleFactor': 0.7,
        'showRestChords': True,
        'maxRestChords': 5,
        'restChordsScaleFactor': 0.5,
        'restChordsTypeFScaleFactor': 0.8,
        'keyName': 'C',
        'useRomanNotation': False,
        'showKeyLabel': True,
        'autoKeyDetection': True
    }

    def __init__(self, config=DEFAULT_CONFIG):
        super().__init__()
        for conf in ChordWindow.DEFAULT_CONFIG.items():
            self.__setattr__(*conf)
        if config != ChordWindow.DEFAULT_CONFIG:
            for conf in config.items():
                self.__setattr__(*conf)
        self.isSharpKey = (self.keyName in chord.KEY_LIST[0])
        self.connectMonitor()
        self.initUI()
        self.show()

    def connectMonitor(self):
        MainWidget.monitor.trigger.connect(self.updateChordLabel)

    def toggleMoreResults(self, flag=None):
        if flag is not None:
            self.showRestChords = True if flag else False
        if not self.showRestChords:
            for i in range(1, self.maxRestChords + 1):
                self.chordlabels[i][0].setText('')
                self.chordlabels[i][1].setText('')
        self.updateKeyLabel()

    def textColorSettingsDialog(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.pl = QPalette()
            self.pl.setColor(QPalette.WindowText, col)
            for l in self.chordlabels:
                l[0].setPalette(self.pl)
                l[1].setPalette(self.pl)
            self.pl.setColor(QPalette.WindowText, col.darker(200))
            self.keyLabel.setPalette(self.pl)

    def keyPressEvent(self, event):

        # if event.key() == Qt.Key_Tab:
        #   global WINDOW_INDEX
        #   global OPEN_WINDOWS
        #   WINDOW_INDEX += 1
        #   WINDOW_INDEX %= len(OPEN_WINDOWS)
        #   print(WINDOW_INDEX)
        #   # OPEN_WINDOWS[WINDOW_INDEX].setFocus(Qt.ActiveWindowFocusReason)
        #   OPEN_WINDOWS[WINDOW_INDEX].raise_()
        #   OPEN_WINDOWS[WINDOW_INDEX].activateWindow()

        if event.key() == Qt.Key_Escape:
            QApplication.instance().quit()

        if event.key() == Qt.Key_Q:
            QApplication.instance().quit()

        if event.key() == Qt.Key_L:
            self.showKeyLabel = not self.showKeyLabel
            self.updateKeyLabel()

        if event.key() == Qt.Key_C:
            pass

        if event.key() == Qt.Key_F:
            font, valid = QFontDialog.getFont()
            if valid:
                for lbs in self.chordlabels:
                    lbs[0].setFont(font)
                    lbs[1].setFont(font)
                self.keyLabel.setFont(font)

        if event.key() == Qt.Key_S:
            self.isSharpKey = not self.isSharpKey
            self.setKey(chord.getAccidentalNumber(self.keyName))
            self.updateKeyLabel()

        if event.key() == Qt.Key_R:
            MainWidget.sustained_notes = set([])
            MainWidget.pressed_notes = set([])

        if event.key() == Qt.Key_N:
            self.useRomanNotation = not self.useRomanNotation

        if event.key() == Qt.Key_Right:
            if QApplication.keyboardModifiers() == (Qt.ShiftModifier):
                self.moveWindows(2, 0)
            else:
                self.moveWindows(10, 0)
        if event.key() == Qt.Key_Left:
            if QApplication.keyboardModifiers() == (Qt.ShiftModifier):
                self.moveWindows(-2, 0)
            else:
                self.moveWindows(-10, 0)
        if event.key() == Qt.Key_Up:
            if QApplication.keyboardModifiers() == (Qt.ShiftModifier):
                self.moveWindows(0, -2)
            else:
                self.moveWindows(0, -10)
        if event.key() == Qt.Key_Down:
            if QApplication.keyboardModifiers() == (Qt.ShiftModifier):
                self.moveWindows(0, 2)
            else:
                self.moveWindows(0, 10)

        if event.key() == Qt.Key_0:
            self.setKey(0)
            self.updateKeyLabel()
        if event.key() == Qt.Key_1:
            self.setKey(1)
            self.updateKeyLabel()
        if event.key() == Qt.Key_2:
            self.setKey(2)
            self.updateKeyLabel()
        if event.key() == Qt.Key_3:
            self.setKey(3)
            self.updateKeyLabel()
        if event.key() == Qt.Key_4:
            self.setKey(4)
            self.updateKeyLabel()
        if event.key() == Qt.Key_5:
            self.setKey(5)
            self.updateKeyLabel()
        if event.key() == Qt.Key_6:
            self.setKey(6)
            self.updateKeyLabel()
        if event.key() == Qt.Key_7:
            self.setKey(7)
            self.updateKeyLabel()

    def setKey(self, n):
        self.keyName = chord.getKeyName(n, self.isSharpKey)

    def updateKeyLabel(self):
        self.keyLabel.move(0,
                           self.chordlabels[-1 if self.showRestChords else 0][0].pos().y()
                           + self.chordlabels[-1 if self.showRestChords else 0][0].height() + 10
                           )
        self.keyLabel.setVisible(self.showKeyLabel)
        self.keyLabel.setText('Current Key: ' + self.keyName)
        self.keyLabel.adjustSize()

    def updateChordLabel(self):
        try:
            self.keyName = monitor.KeyDetector.currentKey
            self.updateKeyLabel()
            l = len(monitor.currentChords)
            for i in range(1 + self.maxRestChords):
                if i < l:
                    chordObj = copy.deepcopy(monitor.currentChords[i])
                    # chordObj = monitor.currentChords[i]
                    chordObj.updateName(self.keyName, self.useRomanNotation)
                lbs = self.chordlabels[i]
                # lbs[0].setText('' if i >= l else ((c.name[0]) if ALLOW_SLASH_CHORD else c.get_base_name()))
                lbs[0].setText('' if i >= l else (
                    chordObj.name[0] if self.allowSlashChord else chordObj.get_base_name()))
                lbs[0].adjustSize()
                lbs[1].move(lbs[0].x() + lbs[0].width() + self.chordNameGap,
                            lbs[0].y() - 5 if self.useRomanNotation else lbs[0].y() + lbs[0].height() - lbs[1].height())
                lbs[1].setText('' if i >= l else chordObj.name[1])
                lbs[1].adjustSize()
                if not self.showRestChords:
                    break

            self.repaint()
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
        self.chordlabels = []

        for i in range(self.maxRestChords + 1):
            lb = QLabel('', self)
            lb2 = QLabel('', self)
            self.chordlabels.append([lb, lb2])

        for lbs in self.chordlabels:
            # the best chord's labels
            if self.chordlabels.index(lbs) == 0:
                lbs[0].setText('Chord...')
                lbs[0].setFont(QFont("Century Gothic", self.chordFontSize))
                lbs[0].setAlignment(Qt.AlignLeft)
                lbs[0].adjustSize()
                lbs[0].setPalette(self.pl)
                lbs[0].setToolTip(CHORDLABEL_TIP)
                # lbs[0].setFrameShape(QFrame.Panel)
                # lbs[0].setFrameShadow(QFrame.Sunken)
                # lbs[0].setLineWidth(1)

                lbs[1].setFont(QFont("Century Gothic", int(
                    self.chordFontSize * self.chordTypeScaleFactor)))
                lbs[1].setAlignment(Qt.AlignLeft)
                lbs[1].adjustSize()
                lbs[1].setToolTip(CHORDLABEL_TIP)
                lbs[1].setPalette(self.pl)
                lbs[1].move(
                    lbs[0].x() + lbs[0].width() + self.chordNameGap,
                    lbs[0].y() + lbs[0].height() - lbs[1].height()
                )
            # lbs[1].setFrameShape(QFrame.Panel)
            # lbs[1].setFrameShadow(QFrame.Sunken)
            # lbs[1].setLineWidth(1)
            # the rest chords' labels
            else:
                idx = self.chordlabels.index(lbs)
                prev_lbs = self.chordlabels[idx - 1]

                font_size = self.chordFontSize * self.restChordsScaleFactor
                lbs[0].setFont(QFont("Century Gothic", font_size))
                lbs[0].setAlignment(Qt.AlignLeft)
                lbs[0].adjustSize()
                lbs[0].setToolTip(CHORDLABEL_TIP)
                lbs[0].setPalette(self.pl)
                # lbs[0].setFrameShape(QFrame.Panel)
                # lbs[0].setFrameShadow(QFrame.Sunken)
                # lbs[0].setLineWidth(1)
                lbs[0].move(0, prev_lbs[0].y() +
                            prev_lbs[0].height() + (10 if idx == 1 else 0))

                lbs[1].setFont(QFont("Century Gothic", int(
                    font_size * self.restChordsTypeFScaleFactor)))
                lbs[1].setAlignment(Qt.AlignLeft)
                lbs[1].adjustSize()
                lbs[1].setToolTip(CHORDLABEL_TIP)
                lbs[1].setPalette(self.pl)
                lbs[1].move(
                    lbs[0].x() + lbs[0].width() + self.chordNameGap,
                    lbs[0].y() + lbs[0].height() - lbs[1].height()
                )
            # lbs[1].setFrameShape(QFrame.Panel)
            # lbs[1].setFrameShadow(QFrame.Sunken)
            # lbs[1].setLineWidth(1)

        self.keyLabel = QLabel(self.keyName, self)
        self.updateKeyLabel()
        self.keyLabel.setFont(QFont("Century Gothic", int(
            self.chordFontSize * self.restChordsScaleFactor)))
        self.keyLabel.setPalette(self.pl)
        self.keyLabel.adjustSize()
        self.show()

    # @debug
    def keyNameClicked(self, keyName):
        self.keyName = keyName
        self.autoKeyDetection = False
        self.updateKeyLabel()

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)
        # Color settings
        colorAction = contextMenu.addAction("Text Color...")
        colorAction.triggered.connect(self.textColorSettingsDialog)

        # Results
        moreResultsAction = contextMenu.addAction(
            "Hide More Results" if self.showRestChords else "Show More Results"
        )
        moreResultsAction.triggered.connect(lambda: self.toggleMoreResults(not self.showRestChords))

        # KeySettings
        keyMenu = contextMenu.addMenu("Key Settings")
        autoDetection = QAction("Auto Detection", keyMenu, checkable=True, checked=self.autoKeyDetection)
        autoDetection.triggered.connect(lambda: self.__setattr__("autoKeyDetection", True))
        keyMenu.addAction(autoDetection)

        for k in "Gb,Db,Ab,Eb,Bb,F,C,G,D,A,E,B,F#".split(','):
            action = QAction(k, keyMenu, checkable=True, checked=(k == self.keyName and not self.autoKeyDetection))
            action.triggered.connect(lambda checked, name=k: self.keyNameClicked(name))
            keyMenu.addAction(action)
        #
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))

    # ---------------
    #
    #
    # # if action == colorAction:
    # #     self.textColorSettingsDialog()
    # # if action == moreResultsAction:
    # #     self.toggleMoreResults(not self.showRestChords)
    # if action in keyMenu.actions():
    #     if action.text() == "Auto Detection":
    #         self.autoKeyDetection = True
    #     else:
    #         self.keyName = action.text()
    #         self.autoKeyDetection = False
    #         self.updateKeyLabel()
