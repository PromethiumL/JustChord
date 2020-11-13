import os
import re
import sys

from PyQt5 import QtCore, QtWidgets, QtSvg
from PyQt5.QtGui import *

from ..core import chord
from .mainwidget import MainWidget, monitor

DEFAULT_LINE_GAP = 30
DEFAULT_WIDTH = 20 * DEFAULT_LINE_GAP
DEFAULT_WIDTH_HEIGHT_RATIO = 1
DEFAULT_HEIGHT = DEFAULT_WIDTH / DEFAULT_WIDTH_HEIGHT_RATIO
DEFAULT_STROKE_WIDTH = 0.1

STAFF_HORIZONTAL_CENTER_OFFSET = 2 * DEFAULT_LINE_GAP

_accidental_widget_vertical_offsets = {
    None: 0,
    'sharp': -0.5,
    'flat': -1,
    'double_sharp': -0.5,
    'double_flat': -0.9,
    'natural': -0.5
}
# _accidental_widget_vertical_offsets = {
#     None: 0,
#     'sharp': 0,
#     'flat': 0,
#     'double_sharp': 0,
#     'double_flat': 0,
#     'natural': 0
# }


class NoteWidget(QtSvg.QSvgWidget):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.load('./assets/whole_note.svg')
        self.accidentalWidget = QtSvg.QSvgWidget()
        self.accidentalWidget.setParent(self.parent())
        self.accidentalType = None
        self.accidentalOffsetX = -1 * self.parent().lineGap
        x = self.parent().width() / 2
        y = self.parent().height() / 2
        self.w = self.parent().lineGap * 12 / 7
        self.h = self.parent().lineGap
        self.show()
        self.setGeometry(
            x,
            y,
            self.w,
            self.h
        )
        # self.setStyleSheet("border: 1px solid red;")

    def setAccidentalType(self, t=None):
        if t in {'sharp', 'flat', 'double_sharp', 'double_flat', 'natural'}:
            self.accidentalWidget.load('./assets/{}.svg'.format(t))
            self.accidentalType = t
            # self.accidentalWidget.setStyleSheet("border: 1px solid red;")

    def setCenterPosition(self, x=None, y=None, w=None, h=None):
        if x is None:
            x = self.pos().x() + self.width() / 2
        if y is None:
            y = self.pos().y() + self.height() / 2
            # print(self.pos().y(), self.height() / 2)
        if w is None:
            w = self.width()
        if h is None:
            h = self.height()
        self.resize(w, h)
        self.move(x - w / 2, y - h / 2)

        # Here, for the accidentals, the x and y are the top left corner of the noteWidget.
        self.accidentalWidget.setGeometry(
            self.pos().x() + self.accidentalOffsetX,
            self.pos().y() - 1.0 * self.parent().lineGap,
            self.parent().lineGap,
            2 * self.parent().lineGap
        )

    def move_accidental_widget_with_x_offset(self, offset=0):
        self.accidentalWidget.move(
            self.pos().x() + self.accidentalOffsetX + offset,
            self.pos().y() + _accidental_widget_vertical_offsets[self.accidentalType] * self.parent().lineGap
        )

    def show(self):
        self.update()
        super().show()
        if self.accidentalType is None:
            self.accidentalWidget.setVisible(False)
        else:
            self.accidentalWidget.setVisible(True)
            self.accidentalWidget.show()


class StaffWindow(MainWidget):
    DEFAULT_CONFIG = {
        'keyName': 'C'
    }

    def __init__(self, config=DEFAULT_CONFIG):
        super().__init__()
        for conf in StaffWindow.DEFAULT_CONFIG.items():
            self.__setattr__(*conf)
        if config != StaffWindow.DEFAULT_CONFIG:
            for conf in config.items():
                self.__setattr__(*conf)
        self.initUI()
        self.setGeometry(800, 400, 500, 500)
        # self.show()
        if __name__ != '__main__':
            MainWidget.monitor.trigger.connect(self.updateNotes)


    def updateNotes(self):
        self.keyName = monitor.KeyDetector.currentKey
        self.setKeySignatures(self.keyName)
        names = set()
        pitches = monitor.pressedNotes | monitor.sustainedNotes
        if monitor.currentChords and monitor.currentChords[0].isBlank == False:
            thisChord = monitor.currentChords[0]
            thisChord.updateName(key=self.keyName)
            for name in thisChord.noteNames:
                for pitch in pitches:
                    if pitch % 12 == chord.getPitchNumber(name) % 12:
                        octave = chord.getPitchOctaveNumber(pitch)
                        if chord.PITCH_INDEX[name] < 0:
                            octave += 1
                        if chord.PITCH_INDEX[name] > 11:
                            octave -= 1
                        names.add(name + str(octave))
            # print('staff notes list: {}'.format(names))


        else:
            for pitch in pitches:
                noteName = chord.getPitchName(pitch, with_octave=True, key=self.keyName)
                names.add(noteName)
        # print(names)

        # Remove old notes
        for noteName in list(self.noteWidgets.keys()):
            if noteName not in names:
                self.removeNote(noteName)

        # Add new notes
        for noteName in names:
            if noteName not in self.noteWidgets:
                self.addNote(noteName)

        self.drawNotes()


    def setKeySignatures(self, keyName='C'):
        if keyName not in chord.NATURAL_SCALES:
            raise Exception('invalid keyName{}'.format(keyName))
        if keyName == 'C':
            for clef in ['G', 'F']:
                for name in ['sharp', 'flat']:
                    for svg in self.keySignatures[clef][name]:
                        svg.setVisible(False)
            return
        isSharpKey = keyName in chord.KEY_LIST[0]
        number = chord.KEY_LIST[0 if isSharpKey else 1].index(keyName) + 1
        beginX = self.width() / 2 - DEFAULT_WIDTH * 0.2
        gapX = 0.6 * self.lineGap
        sharp_beginY1 = self.calcNoteHeight('G5')
        sharp_beginY2 = self.calcNoteHeight('G3')
        flat_beginY1 = self.calcNoteHeight('C5')
        flat_beginY2 = self.calcNoteHeight('C3')  # offset 1 upwards
        for clef in ['G', 'F']:
            for name, beginYs in [('sharp', (sharp_beginY1, sharp_beginY2)), ('flat', (flat_beginY1, flat_beginY2))]:
                beginY = beginYs[0] if clef == 'G' else beginYs[1]
                x = beginX
                y = beginY + _accidental_widget_vertical_offsets[name] * self.lineGap
                for i in range(7):
                    self.keySignatures[clef][name][i].setGeometry(
                        x,
                        y,
                        self.lineGap,
                        2 * self.lineGap
                    )
                    visible = isSharpKey ^ (name != 'sharp') and i < number
                    # visible = True
                    self.keySignatures[clef][name][i].setVisible(visible)
                    x += gapX
                    if name == 'sharp':
                        deltaY = 1.5 if i % 2 == (1 if i > 2 else 0) else -2
                    else:
                        deltaY = -1.5 if i % 2 == 0 else 2
                    y += self.lineGap * deltaY


    def initUI(self):
        print(sys.path)
        self.lineGap = 20
        self.staffWidth = 20 * self.lineGap
        self.strokeWidth = self.lineGap * 0.1
        self.pen = QPen(QtCore.Qt.black, self.strokeWidth, QtCore.Qt.SolidLine)
        self.staffCenterY = self.height() / 2;
        self.noteWidgets = {}
        self.notes = set()
        self.keySignatures = []

        self.gClef = QtSvg.QSvgWidget(self)
        self.gClef.load('./assets/G_clef.svg')
        # self.gClef.setStyleSheet("border: 1px solid red;")

        self.fClef = QtSvg.QSvgWidget(self)
        self.fClef.load('./assets/F_clef.svg')
        # self.fClef.setStyleSheet("border: 1px solid red;")
        self.drawStaff()
        self.drawNotes()
        self.drawAllKeySignatures()


    def drawStaff(self):
        self.gClef.setGeometry(
            (self.width() - self.staffWidth) / 2 - .25 * self.lineGap,
            self.height() / 2 - 6.5 * self.lineGap,
            self.lineGap * 4.5,
            self.lineGap * 7.5
        )
        self.fClef.setGeometry(
            (self.width() - self.staffWidth) / 2 + .8 * self.lineGap,
            self.height() / 2 + self.lineGap,
            self.lineGap * 3,
            self.lineGap * 3.2
        )


    def drawAllKeySignatures(self):
        self.keySignatures = {
            'G': {  # G clef
                'sharp': [],
                'flat': []
            },
            'F': {  # F clef
                'sharp': [],
                'flat': []
            }
        }  # There should be 6 * 2 * 2 == 24 accidentals.
        for claf in ['G', 'F']:
            for name in ['sharp', 'flat']:
                for i in range(7):
                    svg = QtSvg.QSvgWidget(self)
                    svg.load('./assets/{}.svg'.format(name))
                    svg.setVisible(False)
                    self.keySignatures[claf][name].append(svg)
        self.setKeySignatures(self.keyName)


    def calcNoteHeight(self, name):
        degree = "CDEFGAB".index(name[0])
        try:
            octave = int(re.match(r'(.*?)(\d+)', name).groups()[1])
            # print(re.match(r'(.*?)(\d+)', name).groups()[1])
        except Exception as e:
            raise Exception("Note name missing octave info! '{}'".format(name))
        octave = int(octave)
        return self.staffCenterY - ((octave - 4) * 7 + degree) * self.lineGap / 2


    def addNote(self, name):
        if name in self.notes:
            pass
        # print("name: {}".format(name))
        self.notes.add(name)
        n = NoteWidget(self)
        n.setCenterPosition(
            x=self.width() / 2,
            y=self.height() / 2,
            w=n.width(),
            h=n.height()
        )
        self.noteWidgets[name] = n


    def removeNote(self, name):
        if self.noteWidgets[name].accidentalType != None:
            self.noteWidgets[name].accidentalWidget.deleteLater()
        self.noteWidgets[name].deleteLater()
        del self.noteWidgets[name]
        self.notes.discard(name)


    def drawNotes(self):
        l = list(self.notes)
        l.sort(key=lambda name: chord.getPitchNumber(name))
        for i in range(len(l)):
            name = l[i]
            if name not in self.noteWidgets:
                self.addNote(name)
            positionY = self.calcNoteHeight(name)
            acdlString = self.getAccidentalInfoInKey(name, self.keyName)
            hasAccidental = '#' in acdlString or 'b' in acdlString or 'x' in acdlString or 'n' in acdlString
            acdt_offsetX = 0
            currentNote = self.noteWidgets[name]
            prevNote = None
            if i > 0:
                prevNote = self.noteWidgets[l[i - 1]]
            currentNote.setCenterPosition(x=self.width() / 2 + STAFF_HORIZONTAL_CENTER_OFFSET, y=positionY)
            if hasAccidental:
                if 'bb' in acdlString:
                    currentNote.setAccidentalType('double_flat')
                elif 'b' in acdlString:
                    currentNote.setAccidentalType('flat')
                elif '#' in acdlString:
                    currentNote.setAccidentalType('sharp')
                elif 'x' in acdlString:
                    currentNote.setAccidentalType('double_sharp')
                elif 'n' in acdlString:
                    currentNote.setAccidentalType('natural')
                currentNote.move_accidental_widget_with_x_offset()

            # Note head overlapping detection
            if i > 0 and (prevNote.pos().y() - positionY) < 1:  # 'm2/M2' intervals
                if prevNote.pos().x() <= currentNote.pos().x():  # this note not having been shifted to the right yet
                    currentNote.move(
                        currentNote.pos().x() + 1.1 * self.lineGap,
                        currentNote.pos().y()
                    )
                    currentNote.accidentalOffsetX = -2.2 * self.lineGap
            currentNote.move_accidental_widget_with_x_offset(0)  # update position

            # Accidental overlapping detection
            if hasAccidental:
                overlapped = False
                for j in range(i):
                    widget = self.noteWidgets[l[j]]
                    acdl_widget = widget.accidentalWidget
                    if widget.accidentalType is not None:
                        widget = widget.accidentalWidget
                    if currentNote.accidentalWidget.pos().y() + currentNote.accidentalWidget.height() > widget.pos().y():
                        if currentNote.accidentalWidget.pos().x() < widget.pos().x() + widget.width():
                            overlapped = True
                            break

                if overlapped:
                    N = 1  # Number of notes below to check to avoid accidental signature overlapping
                    inf = 99999
                    numOfNotesChecked = 0
                    j = i - 1
                    while numOfNotesChecked < N and j >= 0:
                        note_below = self.noteWidgets[l[j]]
                        x = note_below.pos().x()
                        y = note_below.pos().y()
                        if note_below.accidentalType is not None:
                            numOfNotesChecked += 1
                            x = note_below.accidentalWidget.pos().x()
                            y = note_below.accidentalWidget.pos().y()
                        if currentNote.accidentalWidget.pos().x() + currentNote.accidentalWidget.width() >= x and \
                                currentNote.accidentalWidget.pos().y() + currentNote.accidentalWidget.height() >= y:
                            acdt_offsetX += x - currentNote.accidentalWidget.pos().x()
                            acdt_offsetX -= currentNote.accidentalWidget.width()
                        currentNote.move_accidental_widget_with_x_offset(acdt_offsetX)
                        j -= 1

            currentNote.show()


    def respellNotes(self):
        pass


    def getAccidentalInfoInKey(self, noteName, keyName):
        """This deals with the accidentals."""
        if keyName not in chord.NATURAL_SCALES:
            raise Exception('invalid keyName: {}'.format(keyName))

        letter = noteName[0]
        index = 'CDEFGAB'.index(noteName[0])

        def removeDigits(s):
            return ''.join(list(filter(lambda ch: not (ord('0') <= ord(ch) <= ord('9')), s)))

        currentAccidental = removeDigits(noteName[1:])
        actualAccidental = chord.NATURAL_SCALES[keyName][index][1:]

        if currentAccidental == '' and actualAccidental != '':
            return 'n'  # 'n' for 'natural'
        if currentAccidental != '' and currentAccidental == actualAccidental:
            return ''
        if currentAccidental == 'n' and actualAccidental == '':
            return ''
        return currentAccidental


    def resizeEvent(self, e):
        self.staffCenterY = self.height() / 2
        self.drawStaff()
        self.drawNotes()
        self.setKeySignatures(self.keyName)


    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setPen(self.pen)
        y0 = self.height() / 2 - 5 * self.lineGap;
        x1 = (self.width() - self.staffWidth) / 2
        x2 = x1 + self.staffWidth
        for i in range(10):
            y = y0 + i * self.lineGap
            if i >= 5:
                y += self.lineGap
            painter.drawLine(x1, y, x2, y)

        topLineY = y0
        bottomLineY = topLineY + 10 * self.lineGap

        def ceil(x):
            return int(x + 0.5)

        if len(self.noteWidgets) < 1:
            return

        notes_to_check = sorted(self.noteWidgets.items(), key=lambda pair: chord.getPitchNumber(pair[0]))
        if len(notes_to_check) > 2:
            notes_to_check = [notes_to_check[0], notes_to_check[-1]]
        notes_to_check += [(name, note) for name, note in self.noteWidgets.items() if
                           note.pos().x() > self.width() / 2 + STAFF_HORIZONTAL_CENTER_OFFSET]

        for name, note in notes_to_check:
            hasExtraLines = False
            if int(note.pos().y() + 0.5 * note.height()) == int(self.height() / 2):
                additionalLineY = self.height() / 2
                hasExtraLines = True

            # Additional lines beneath
            if note.pos().y() > bottomLineY:
                additionalLineY = bottomLineY + self.lineGap * ceil((note.pos().y() - bottomLineY) / self.lineGap)
                hasExtraLines = True

            # Above
            if note.pos().y() + note.height() < topLineY:
                additionalLineY = topLineY - self.lineGap * ceil(
                    (topLineY - note.pos().y() - note.height()) / self.lineGap)
                hasExtraLines = True

            if hasExtraLines:
                y = topLineY - self.lineGap if note.pos().y() + note.height() < topLineY else bottomLineY + self.lineGap
                step = -self.lineGap if y < topLineY else self.lineGap
                while not ((step < 0) ^ (y > additionalLineY)):
                    painter.drawLine(
                        self.width() / 2 + STAFF_HORIZONTAL_CENTER_OFFSET - (0.5 + 0.1) * note.width(),
                        # note.pos().x() - (0.1) * note.width(),
                        y,
                        self.width() / 2 + STAFF_HORIZONTAL_CENTER_OFFSET + (0.5 + 0.1) * note.width(),
                        # note.pos().x() + (1 + 0.1) * note.width(),
                        y
                    )
                    y += step
                painter.drawLine(
                    # self.width() / 2 + STAFF_HORIZONAL_CENTER_OFFSET - (0.5 + 0.1) * note.width(),
                    note.pos().x() - (0.1) * note.width(),
                    additionalLineY,
                    # self.width() / 2 + STAFF_HORIZONAL_CENTER_OFFSET + (0.5 + 0.1) * note.width(),
                    note.pos().x() + (1 + 0.1) * note.width(),
                    additionalLineY
                )
        self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    staffWidget = StaffWindow()
    staffWidget.addNote('C4')
    staffWidget.addNote('E4')
    staffWidget.addNote('Ab4')
    staffWidget.addNote('B4')
    staffWidget.removeNote('B4')

    staffWidget.drawNotes()
    # staffWidget.addNote(71)
    sys.exit(app.exec_())
