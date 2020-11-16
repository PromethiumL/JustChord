from JustChord.gui.imports import *

black_key_length_ratio = 0.6

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
        self.initUI()
        self.min_pitch = 0
        self.max_pitch = 60
        self.horizontal_unit = 10
        self.pressed_notes = set()
        self.painter = QPainter()

    def range(self):
        return self.max_pitch - self.min_pitch

    def black_step(self):
        return self.horizontal_unit

    def white_step(self):
        return self.horizontal_unit * 12 / 7

    def initUI(self):
        self.resize(500, 500)
        self.show()

    def paintEvent(self, QPaintEvent):
        pass


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     kb = KeyboardWidget()
#     sys.exit(app.exec_())
