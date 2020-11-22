from JustChord.gui.imports import *
from . import widget

black_key_length_ratio = 0.6
keyboard_offsets = [
    0,
    - 5 / 7,
    2 / 7,
    -4 / 7,
    3 / 7,
    -1 / 7,
    -1 / 7,
    1 / 7,
    -3 / 7,
    3 / 7
]

light_gray_brush = QBrush(Qt.lightGray, Qt.SolidPattern)
gray_brush = QBrush(Qt.darkGray, Qt.SolidPattern)
white_brush = QBrush(Qt.white, Qt.SolidPattern)
green_brush = QBrush(QColor(0x32, 0xf0, 0x80), Qt.SolidPattern)
dark_green_brush = QBrush(QColor(0x11, 0xc1, 0x57), Qt.SolidPattern)


def is_black(pitch):
    return pitch % 12 in [1, 3, 6, 8, 10]


def is_white(pitch):
    return pitch % 12 not in [1, 3, 6, 8, 10]


_is_white = [int(is_white(x)) for x in range(12)]
_accumulated_white = [sum(_is_white[0:i + 1]) for i in range(12)]


def argmax(lst):
    return sorted(reversed(list(enumerate(lst))))[-1][0]


def argmin(lst):
    return sorted(reversed(list(enumerate(lst))))[0][0]


def accumulated_white_keys(pitch):
    return pitch // 12 * 7 + _accumulated_white[pitch % 12]


def count_accumulated_white_keys(lo, hi):
    """[lo, hi)"""
    return accumulated_white_keys(hi) - accumulated_white_keys(lo)


class KeyboardWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.min_pitch = 60
        self.max_pitch = 37 + 60
        self.pressed_notes = set()
        self.sustained_notes = set()
        self.is_sustain_down = False
        self.mouse_current_pitch = None
        self.keyboardHeight = 200  # height of the white key
        # self.setStyleSheet('.KeyboardWidget { padding: 20px; }')

        self.strokeWidth = 3
        self.pen = QPen(Qt.darkGray, self.strokeWidth, Qt.SolidLine)
        self.painter = QPainter(self)
        self.painter.setPen(self.pen)
        self.initUI()

    def send_midi_msg_to_monitor(self, channel, pitch, velocity):
        with widget.Widget.monitor.lock:
            widget.Widget.monitor.append_message([channel, pitch, velocity])

    def note_on(self, pitch, velocity=100):
        self.send_midi_msg_to_monitor(0x90, pitch, velocity)

    def note_off(self, pitch):
        self.send_midi_msg_to_monitor(0x80, pitch, 0)

    def midi_reset(self):
        # TODO: reset msg
        pass

    def range(self):
        return self.max_pitch - self.min_pitch

    def black_step(self):
        return self.horizontal_unit()

    def white_step(self):
        return self.horizontal_unit() * 12 / 7

    def horizontal_unit(self):
        return self.keyboardHeight / 10

    def initUI(self):
        self.resize(int((self.range() + 1) * self.horizontal_unit()), int(self.keyboardHeight))
        self.setWindowTitle('Virtual Keyboard')
        self.show()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setPen(self.pen)

        # painter.drawRect(0, 0, int(self.range() * self.horizontal_unit()), int(self.keyboardHeight))
        self.update()

        for i in range(self.range()):  # white keys
            p = self.min_pitch + i
            if is_black(p):
                continue
            else:
                if p in self.pressed_notes:
                    painter.setBrush(green_brush)
                elif p in self.sustained_notes:
                    # painter.setBrush(light_gray_brush)
                    painter.setBrush(green_brush)
                else:
                    painter.setBrush(Qt.NoBrush)
                x = count_accumulated_white_keys(self.min_pitch, p) * self.white_step()
                painter.drawRect(
                    int(x), 0,
                    int(self.white_step()), self.keyboardHeight
                )

        for i in range(self.range()):  # black keys
            p = self.min_pitch + i
            if is_black(p):
                if p in self.pressed_notes:
                    painter.setBrush(green_brush)
                elif p in self.sustained_notes:
                    # painter.setBrush(light_gray_brush)
                    painter.setBrush(dark_green_brush)
                else:
                    painter.setBrush(gray_brush)
                x = i * self.black_step()
                painter.drawRect(
                    int(x), 0,
                    int(self.black_step()), int(self.keyboardHeight * black_key_length_ratio)
                )

    def resizeEvent(self, e):
        # self.resize(int(self.horizontal_unit() * self.range()), int(self.keyboardHeight))
        self.keyboardHeight = self.height()
        self.update()

    def keyPressEvent(self, e: QKeyEvent):
        if e.isAutoRepeat():
            return
        if e.key() == Qt.Key_Space:  # hold sustain pedal
            self.is_sustain_down = True
            print('sustain')

    def keyReleaseEvent(self, e: QKeyEvent):
        if e.isAutoRepeat():
            return
        if e.key() == Qt.Key_Space:  # release sustain pedal
            self.is_sustain_down = False
            for p in list(self.sustained_notes):
                if p not in self.pressed_notes:
                    self.note_off(p)
                self.sustained_notes.discard(p)
            print('released')

    def mousePressEvent(self, e: QMouseEvent):
        x = e.pos().x()
        y = e.pos().y()
        pitch = self.posToPitch(x, y)
        if self.min_pitch <= pitch <= self.max_pitch:
            self.addNote(pitch)

    def removeNote(self, pitch):
        if pitch in self.pressed_notes:
            self.pressed_notes.discard(pitch)
        if self.is_sustain_down:
            self.sustained_notes.add(pitch)
        else:
            self.note_off(pitch)

    def addNote(self, pitch):
        self.mouse_current_pitch = pitch
        self.note_on(pitch)
        self.pressed_notes.add(pitch)
        if self.is_sustain_down:
            self.sustained_notes.add(pitch)

    def mouseMoveEvent(self, e):  # Glissing notes
        x = e.pos().x()
        y = e.pos().y()
        pitch = self.posToPitch(x, y)
        if pitch < self.min_pitch or pitch > self.max_pitch:
            return
        if pitch != self.mouse_current_pitch:
            self.removeNote(self.mouse_current_pitch)
            self.addNote(pitch)

    def mouseReleaseEvent(self, e):
        pitch = self.posToPitch(e.pos().x(), e.pos().y())
        if pitch in self.pressed_notes:
            self.removeNote(pitch)

    def posToPitch(self, x, y):
        i = int(x // self.horizontal_unit())
        if is_white(i):
            return i + self.min_pitch
        if y < self.keyboardHeight * black_key_length_ratio:
            return i + self.min_pitch
        else:
            x2 = (1 + count_accumulated_white_keys(self.min_pitch, i + self.min_pitch)) * self.white_step()
            if x2 < x:
                return i + 1 + self.min_pitch
            else:
                return i - 1 + self.min_pitch


if __name__ == '__main__':
    app = QApplication(sys.argv)
    kb = KeyboardWidget()
    sys.exit(app.exec_())
