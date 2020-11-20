from JustChord.gui.imports import *

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
        self.min_pitch = 0
        self.max_pitch = 60
        self.pressed_notes = set()

        self.keyboardHeight = 100  # height of the white key
        # self.setStyleSheet('.KeyboardWidget { padding: 20px; }')

        self.strokeWidth = 3
        self.pen = QPen(Qt.darkGray, self.strokeWidth, Qt.SolidLine)
        self.painter = QPainter(self)
        self.painter.setPen(self.pen)
        self.initUI()

    def range(self):
        return self.max_pitch - self.min_pitch

    def black_step(self):
        return self.horizontal_unit()

    def white_step(self):
        return self.horizontal_unit() * 12 / 7

    def horizontal_unit(self):
        return self.keyboardHeight / 10

    def initUI(self):
        self.resize(int(self.range() * self.horizontal_unit()), int(self.keyboardHeight))
        self.show()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setPen(self.pen)
        painter.drawRect(0, 0, int(self.range() * self.horizontal_unit()), int(self.keyboardHeight))
        self.update()

        for i in range(self.range()):  # white keys
            p = self.min_pitch + i
            if is_black(p):
                continue
            else:
                x = count_accumulated_white_keys(self.min_pitch, p) * self.white_step()
                painter.drawRect(
                    int(x), 0,
                    int(self.white_step()), self.keyboardHeight
                )

        painter.setBrush(QBrush(Qt.darkGray, Qt.SolidPattern))
        for i in range(self.range()):  # black keys
            p = self.min_pitch + i
            if is_black(p):
                x = i * self.black_step()
                painter.drawRect(
                    int(x), 0,
                    int(self.black_step()), int(self.keyboardHeight * black_key_length_ratio)
                )

    def resizeEvent(self, e):
        # self.resize(int(self.horizontal_unit() * self.range()), int(self.keyboardHeight))
        self.keyboardHeight = self.height()
        self.update()

    def mousePressEvent(self, e: QMouseEvent):
        x = e.pos().x()
        y = e.pos().y()
        print(self.posToPitch((x, y)))

    def posToPitch(self, pos):
        x, y = pos
        i = int(x // self.horizontal_unit())
        if is_white(i):
            return i
        if y < self.keyboardHeight * black_key_length_ratio:
            return i
        else:
            x2 = (1 + count_accumulated_white_keys(self.min_pitch, i + self.min_pitch)) * self.white_step()
            if x2 < x:
                return i + 1
            else:
                return i - 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    kb = KeyboardWidget()
    sys.exit(app.exec_())
