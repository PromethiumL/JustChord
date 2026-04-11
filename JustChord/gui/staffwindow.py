import re
import sys
from dataclasses import dataclass
from itertools import product

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QApplication

import JustChord.gui.monitor as monitor
from JustChord.core import chord, config
from JustChord.core.constants import KEY_LIST, NATURAL_SCALES, PITCH_INDEX
from JustChord.core.utils import getPitchOctaveNumber
from JustChord.gui.imports import resource_path
from JustChord.gui.widget import Widget

_accidental_widget_vertical_offsets = {
    None: 0,
    "sharp": -0.5,
    "flat": -1,
    "double_sharp": 0,
    "double_flat": -1,
    "natural": -0.5,
}

accidental_scaling_factors = {
    # order: (width_factor, height_factor)
    None: (1, 1),
    "sharp": (0.85, 1),
    "flat": (0.85, 1),
    "double_sharp": (1, 0.5),
    "double_flat": (1.2, 1),
    "natural": (0.7, 1),
}


CLEFS = ["G", "F"]
ACCIDENTAL_TYPES = ["sharp", "flat"]
KEY_SIGNATURE_SLOTS = 7

# Reference notes for where key signature accidentals begin on each clef
KEY_SIG_START_NOTES = {
    ("G", "sharp"): "G5",
    ("G", "flat"): "C5",
    ("F", "sharp"): "G3",
    ("F", "flat"): "C3",
}

# Y-step zigzag patterns (in multiples of line_gap) for laying out key signatures
KEY_SIG_Y_STEPS = {
    "sharp": [1.5, -2, 1.5, 1.5, -2, 1.5, -2],
    "flat": [-1.5, 2, -1.5, 2, -1.5, 2, -1.5],
}

STAFF_LINES_PER_CLEF = 5
STAFF_LINE_MARGIN = 0.1  # Extra line extends beyond note by this fraction of note width
NOTE_OVERLAP_SHIFT = 1.1  # Horizontal shift when notes are a 2nd apart (in line_gaps)


@dataclass
class StaffWindowConfig:
    default_key_name: str = "C"
    key_signature_horizontal_gap: float = 0.75
    key_signature_horizontal_start: float = 0.2
    line_gap: float = 20
    staff_width_in_gaps: float = 20
    default_stroke_width: float = 0.1
    staff_horizontal_center_offset_in_gaps: float = 2
    note_width_scalar: float = 12 / 7
    accidental_horizontal_offset_scalar: float = -1

    # Clef positioning (in multiples of line_gap)
    g_clef_x_offset: float = -0.25
    g_clef_y_offset: float = -6.5
    g_clef_width: float = 4.5
    g_clef_height: float = 7.5
    f_clef_x_offset: float = 0.8
    f_clef_y_offset: float = 1.0
    f_clef_width: float = 3.0
    f_clef_height: float = 3.2

    @property
    def staff_width(self):
        return self.staff_width_in_gaps * self.line_gap

    @property
    def staff_horizontal_center_offset(self):
        return self.staff_horizontal_center_offset_in_gaps * self.line_gap

    @classmethod
    def from_config(cls):
        core = config.section("core")
        staff = config.section("staff")
        return cls(
            default_key_name=core.get("default_key", "C"),
            line_gap=staff.get("line_gap", 20),
            staff_width_in_gaps=staff.get("staff_width_in_gaps", 20),
            default_stroke_width=staff.get("stroke_width", 0.1),
            staff_horizontal_center_offset_in_gaps=staff.get("center_offset_in_gaps", 2),
            note_width_scalar=staff.get("note_width_scalar", 12 / 7),
            accidental_horizontal_offset_scalar=staff.get("accidental_horizontal_offset_scalar", -1),
            key_signature_horizontal_gap=staff.get("key_signature_horizontal_gap", 0.75),
            key_signature_horizontal_start=staff.get("key_signature_horizontal_start", 0.2),
        )

    @property
    def staff_horizontal_center_offset(self):
        return self.staff_horizontal_center_offset_in_gaps * self.line_gap


class NoteWidget(QSvgWidget):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.config: StaffWindowConfig = self.parent().config
        self.load(resource_path("./assets/whole_note.svg"))
        self.accidentalWidget = QSvgWidget()
        self.accidentalWidget.setParent(self.parent())
        self.accidentalType = None
        self.accidentalOffsetX = self.config.accidental_horizontal_offset_scalar * self.config.line_gap
        x = self.parent().width() / 2
        y = self.parent().height() / 2
        self.w = self.parent().config.line_gap * self.parent().config.note_width_scalar
        self.h = self.parent().config.line_gap
        self.show()
        self.setGeometry(int(x), int(y), int(self.w), int(self.h))

    def setAccidentalType(self, t=None):
        if t in {"sharp", "flat", "double_sharp", "double_flat", "natural"}:
            widget = self.accidentalWidget
            widget.load(resource_path("./assets/{}.svg".format(t)))
            widget.setFixedWidth(int(self.parent().config.line_gap * accidental_scaling_factors[t][0]))
            widget.setFixedHeight(int(self.parent().config.line_gap * 2 * accidental_scaling_factors[t][1]))
            self.accidentalType = t
        elif t is None:
            self.accidentalType = None
            self.accidentalWidget.setVisible(False)

    def setCenterPosition(self, x=None, y=None, w=None, h=None):
        if x is None:
            x = self.pos().x() + self.width() / 2
        if y is None:
            y = self.pos().y() + self.height() / 2
        if w is None:
            w = self.width()
        if h is None:
            h = self.height()
        self.resize(w, h)
        self.move(int(x - w / 2), int(y - h / 2))

        # Here, for the accidentals, the x and y are the top left corner of the noteWidget.
        self.accidentalWidget.setGeometry(
            int(self.pos().x() + self.accidentalOffsetX),
            int(self.pos().y() - 1.0 * self.parent().config.line_gap),
            int(self.parent().config.line_gap * accidental_scaling_factors[self.accidentalType][0]),
            int(2 * self.parent().config.line_gap * accidental_scaling_factors[self.accidentalType][1]),
        )

    def move_accidental_widget_with_x_offset(self, offset=0):
        self.accidentalWidget.move(
            int(self.pos().x() + self.accidentalOffsetX + offset),
            int(
                self.pos().y()
                + _accidental_widget_vertical_offsets[self.accidentalType] * self.parent().config.line_gap
            ),
        )

    def show(self):
        self.update()
        super().show()
        if self.accidentalType is None:
            self.accidentalWidget.setVisible(False)
        else:
            self.accidentalWidget.setVisible(True)
            self.accidentalWidget.show()


class StaffWindow(Widget):
    def __init__(self, parent, config=None):
        super().__init__()
        self.config = config or StaffWindowConfig.from_config()
        self.setParent(parent)
        self.keyName = self.config.default_key_name
        self.vacant_components = set()  # recycling useless components for less reloading
        self.initUI()
        if __name__ != "__main__":
            Widget.monitor.trigger.connect(self.updateNotes)

    def _resolve_note_names(self, pitches):
        """Map sounding pitches to spelled note names using chord context."""
        if not monitor.currentChords or monitor.currentChords[0].isBlank:
            return {chord.getPitchName(p, with_octave=True, key=self.keyName) for p in pitches}

        names = set()
        thisChord = monitor.currentChords[0]
        thisChord.updateName(key=self.keyName)
        for name, pitch in product(thisChord.noteNames, pitches):
            if pitch % 12 != chord.getPitchNumber(name) % 12:
                continue
            octave = getPitchOctaveNumber(pitch)
            # Adjust octave for enharmonic spellings that cross octave boundaries
            if PITCH_INDEX[name] < 0:
                octave += 1
            elif PITCH_INDEX[name] > 11:
                octave -= 1
            names.add(name + str(octave))
        return names

    def updateNotes(self):
        self.keyName = monitor.KeyDetector.currentKey
        self.setKeySignatures(self.keyName)

        pitches = monitor.pressedNotes | monitor.sustainedNotes
        names = self._resolve_note_names(pitches)

        # Remove old notes
        for noteName in list(self.noteWidgets.keys()):
            if noteName not in names:
                self.removeNote(noteName)

        # Add new notes
        for noteName in names:
            if noteName not in self.noteWidgets:
                self.addNote(noteName)

        self.drawNotes()
        self.update()

    def _layoutKeySigRow(self, clef, acc_type, begin_x, begin_y, is_sharp_key, num_accidentals):
        """Position and show/hide one row of key signature accidentals."""
        gap = self.config.line_gap
        x_gap = self.config.key_signature_horizontal_gap
        show = is_sharp_key == (acc_type == "sharp")
        w = int(gap * accidental_scaling_factors[acc_type][0])
        h = int(gap * 2 * accidental_scaling_factors[acc_type][1])

        x = begin_x
        y = begin_y + _accidental_widget_vertical_offsets[acc_type] * gap
        for i in range(KEY_SIGNATURE_SLOTS):
            svg = self.keySignatures[clef][acc_type][i]
            svg.setGeometry(int(x), int(y), w, h)
            svg.setVisible(show and i < num_accidentals)
            x += svg.width() * x_gap
            y += gap * KEY_SIG_Y_STEPS[acc_type][i]

    def setKeySignatures(self, keyName="C"):
        if keyName not in NATURAL_SCALES:
            raise Exception("invalid keyName{}".format(keyName))
        if keyName == "C":
            for clef, acc_type in product(CLEFS, ACCIDENTAL_TYPES):
                for svg in self.keySignatures[clef][acc_type]:
                    svg.setVisible(False)
            return

        is_sharp_key = keyName in KEY_LIST[0]
        num_accidentals = KEY_LIST[0 if is_sharp_key else 1].index(keyName) + 1
        begin_x = self.width() / 2 - self.config.staff_width / 2
        begin_x += self.config.key_signature_horizontal_start * self.config.staff_width

        for clef, acc_type in product(CLEFS, ACCIDENTAL_TYPES):
            begin_y = self.calcNoteHeight(KEY_SIG_START_NOTES[(clef, acc_type)])
            self._layoutKeySigRow(clef, acc_type, begin_x, begin_y, is_sharp_key, num_accidentals)

    def initUI(self):
        self.staffWidth = self.config.staff_width
        self.strokeWidth = self.config.line_gap * self.config.default_stroke_width
        self.pen = QPen(Qt.GlobalColor.black, self.strokeWidth, Qt.PenStyle.SolidLine)
        self.staffCenterY = self.height() / 2
        self.noteWidgets = {}
        self.notes = set()  # set of note name: str
        self.keySignatures = []

        self.gClef = QSvgWidget(self)
        self.gClef.load(resource_path("./assets/G_clef.svg"))

        self.fClef = QSvgWidget(self)
        self.fClef.load(resource_path("./assets/F_clef.svg"))
        self.drawStaff()
        self.drawNotes()
        self.drawAllKeySignatures()
        self.show()

    def drawStaff(self):
        cfg = self.config
        staff_left = (self.width() - self.staffWidth) / 2
        center_y = self.height() / 2
        self.gClef.setGeometry(
            int(staff_left + cfg.g_clef_x_offset * cfg.line_gap),
            int(center_y + cfg.g_clef_y_offset * cfg.line_gap),
            int(cfg.line_gap * cfg.g_clef_width),
            int(cfg.line_gap * cfg.g_clef_height),
        )
        self.fClef.setGeometry(
            int(staff_left + cfg.f_clef_x_offset * cfg.line_gap),
            int(center_y + cfg.f_clef_y_offset * cfg.line_gap),
            int(cfg.line_gap * cfg.f_clef_width),
            int(cfg.line_gap * cfg.f_clef_height),
        )

    def drawAllKeySignatures(self):
        self.keySignatures = {
            "G": {"sharp": [], "flat": []},  # G clef
            "F": {"sharp": [], "flat": []},  # F clef
        }  # There should be 6 * 2 * 2 == 24 accidentals.
        for clef in ["G", "F"]:
            for name in ["sharp", "flat"]:
                for _ in range(7):
                    svg = QSvgWidget(self)
                    svg.load(resource_path("./assets/{}.svg".format(name)))
                    svg.setVisible(False)
                    self.keySignatures[clef][name].append(svg)
        self.setKeySignatures(self.keyName)

    def calcNoteHeight(self, name):
        degree = "CDEFGAB".index(name[0])
        try:
            octave = int(re.match(r"(.*?)(\d+)", name).groups()[1])
        except Exception:
            raise Exception("Note name without octave info! '{}'".format(name))
        octave = int(octave)
        return self.staffCenterY - ((octave - 4) * 7 + degree) * self.config.line_gap / 2

    def addNote(self, name):
        if name in self.notes:
            pass
        # print("name: {}".format(name))
        self.notes.add(name)
        if len(self.vacant_components) > 0:
            n = list(self.vacant_components)[0]
            self.vacant_components.discard(n)  # so it's not vacant any more
        else:
            n = NoteWidget(self)  # create new one if no vacant note widget exists
        n.setCenterPosition(x=self.width() / 2, y=self.height() / 2, w=n.width(), h=n.height())
        self.noteWidgets[name] = n

    def removeNote(self, name):
        note = self.noteWidgets[name]
        note.setVisible(False)
        note.accidentalWidget.setVisible(False)
        self.vacant_components.add(note)
        del self.noteWidgets[name]
        self.notes.discard(name)

    @staticmethod
    def _parse_accidental_type(accidental_str):
        """Convert accidental info string to accidental type name."""
        if "bb" in accidental_str:
            return "double_flat"
        if "b" in accidental_str:
            return "flat"
        if "#" in accidental_str:
            return "sharp"
        if "x" in accidental_str:
            return "double_sharp"
        if "n" in accidental_str:
            return "natural"
        return None

    def _resolve_accidental_overlap(self, current_note, sorted_names, index):
        """Shift accidental left if it overlaps with notes/accidentals below."""
        acc = current_note.accidentalWidget
        overlapped = False
        for j in range(index):
            other = self.noteWidgets[sorted_names[j]]
            check_widget = other.accidentalWidget if other.accidentalType is not None else other
            if acc.pos().y() + acc.height() > check_widget.pos().y():
                if acc.pos().x() < check_widget.pos().x() + check_widget.width():
                    overlapped = True
                    break

        if not overlapped:
            return

        offset_x = 0
        j = index - 1
        while j >= 0:
            note_below = self.noteWidgets[sorted_names[j]]
            if note_below.accidentalType is not None:
                bx = note_below.accidentalWidget.pos().x()
                by = note_below.accidentalWidget.pos().y()
                if acc.pos().x() + acc.width() >= bx and acc.pos().y() + acc.height() >= by:
                    offset_x += bx - acc.pos().x() - acc.width()
                current_note.move_accidental_widget_with_x_offset(offset_x)
                break  # Only check the nearest accidental below
            j -= 1

    def drawNotes(self):
        sorted_names = sorted(self.notes, key=lambda name: chord.getPitchNumber(name))
        center_x = self.width() / 2 + self.config.staff_horizontal_center_offset
        gap = self.config.line_gap

        for i, name in enumerate(sorted_names):
            if name not in self.noteWidgets:
                self.addNote(name)
            current_note = self.noteWidgets[name]
            pos_y = self.calcNoteHeight(name)

            # Position the note
            current_note.setCenterPosition(x=center_x, y=pos_y)

            # Determine and apply accidental
            accidental_str = self.getAccidentalInfoInKey(name, self.keyName)
            accidental_type = self._parse_accidental_type(accidental_str)
            current_note.setAccidentalType(accidental_type)
            if accidental_type:
                current_note.move_accidental_widget_with_x_offset()

            # Note head overlap: shift right when notes are a 2nd apart
            if i > 0:
                prev_note = self.noteWidgets[sorted_names[i - 1]]
                if (prev_note.pos().y() - pos_y) < 1 and prev_note.pos().x() <= current_note.pos().x():
                    current_note.move(
                        int(current_note.pos().x() + NOTE_OVERLAP_SHIFT * gap),
                        int(current_note.pos().y()),
                    )
                    current_note.accidentalOffsetX = -2 * NOTE_OVERLAP_SHIFT * gap
            current_note.move_accidental_widget_with_x_offset(0)

            # Accidental overlap detection
            if accidental_type:
                self._resolve_accidental_overlap(current_note, sorted_names, i)

            current_note.show()

    def getAccidentalInfoInKey(self, noteName, keyName):
        """This deals with the accidentals."""
        if keyName not in NATURAL_SCALES:
            raise Exception("invalid keyName: {}".format(keyName))

        letter = noteName[0]
        index = "CDEFGAB".index(letter)

        def removeDigits(s):
            return "".join(list(filter(lambda ch: not (ord("0") <= ord(ch) <= ord("9")), s)))

        currentAccidental = removeDigits(noteName[1:])
        actualAccidental = NATURAL_SCALES[keyName][index][1:]

        if currentAccidental == "" and actualAccidental != "":
            return "n"  # 'n' for 'natural'
        if currentAccidental != "" and currentAccidental == actualAccidental:
            return ""
        if currentAccidental == "n" and actualAccidental == "":
            return ""
        return currentAccidental

    def resizeEvent(self, e):
        self.staffCenterY = self.height() / 2
        self.drawStaff()
        self.drawNotes()
        self.setKeySignatures(self.keyName)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setPen(self.pen)
        gap = self.config.line_gap
        y0 = self.height() / 2 - STAFF_LINES_PER_CLEF * gap
        x1 = (self.width() - self.staffWidth) / 2
        x2 = x1 + self.staffWidth

        # Draw 5 lines for treble clef, then 5 for bass (with 1-gap space between)
        total_lines = 2 * STAFF_LINES_PER_CLEF
        for i in range(total_lines):
            y = y0 + i * gap
            if i >= STAFF_LINES_PER_CLEF:
                y += gap  # gap between treble and bass staves
            painter.drawLine(int(x1), int(y), int(x2), int(y))

        if self.noteWidgets:
            topLineY = y0
            bottomLineY = topLineY + total_lines * gap
            self._drawLedgerLines(painter, topLineY, bottomLineY)

    def _drawLedgerLines(self, painter, topLineY, bottomLineY):
        """Draw ledger lines for notes above/below the staff or on middle C."""
        gap = self.config.line_gap
        margin = STAFF_LINE_MARGIN

        notes_to_check = sorted(self.noteWidgets.items(), key=lambda pair: chord.getPitchNumber(pair[0]))
        if len(notes_to_check) > 2:
            notes_to_check = [notes_to_check[0], notes_to_check[-1]]
        # Also check notes shifted right (due to overlapping)
        notes_to_check += [
            (name, note)
            for name, note in self.noteWidgets.items()
            if note.pos().x() > self.width() / 2 + self.config.staff_horizontal_center_offset
        ]

        for _name, note in notes_to_check:
            ledger_y = None

            # Middle C line
            if int(note.pos().y() + 0.5 * note.height()) == int(self.height() / 2):
                ledger_y = self.height() / 2

            # Ledger lines below staff
            if note.pos().y() > bottomLineY:
                ledger_y = bottomLineY + gap * int((note.pos().y() - bottomLineY) / gap + 0.5)

            # Ledger lines above staff
            if note.pos().y() + note.height() < topLineY:
                ledger_y = topLineY - gap * int((topLineY - note.pos().y() - note.height()) / gap + 0.5)

            if ledger_y is None:
                continue

            # Draw intermediate ledger lines between staff and the note
            center_x = self.width() / 2 + self.config.staff_horizontal_center_offset
            line_half_width = (0.5 + margin) * note.width()
            if note.pos().y() + note.height() < topLineY:
                y = topLineY - gap
                step = -gap
            else:
                y = bottomLineY + gap
                step = gap

            while not ((step < 0) ^ (y > ledger_y)):
                painter.drawLine(
                    int(center_x - line_half_width),
                    int(y),
                    int(center_x + line_half_width),
                    int(y),
                )
                y += step

            # Draw the final ledger line at the note position
            painter.drawLine(
                int(note.pos().x() - margin * note.width()),
                int(ledger_y),
                int(note.pos().x() + (1 + margin) * note.width()),
                int(ledger_y),
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    staffWidget = StaffWindow(parent=None)
    staffWidget.addNote("C4")
    staffWidget.addNote("E4")
    staffWidget.addNote("Ab4")
    staffWidget.addNote("B4")
    staffWidget.removeNote("B4")
    staffWidget.drawNotes()
    # staffWidget.addNote(71)
    sys.exit(app.exec())
