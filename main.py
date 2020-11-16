import os
import sys

curpath = os.path.abspath(os.path.dirname(__file__))

from JustChord.gui.app import JustChordApp

if __name__ == '__main__':
    app = JustChordApp()
