import sys
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from JustChord.gui import monitor


def debug(func):
    def foo(*args, **kwargs):
        print(func.__name__, args, kwargs)
        return func(*args, **kwargs)

    return foo


# @debug
def resource_path(path):  # convert path for pyinstaller
    path = path.replace('/', os.sep)
    if hasattr(sys, '_MEIPASS'):
        # print('has,', os.path.join(sys._MEIPASS, path))
        return os.path.join(sys._MEIPASS, path)
    # print('no,', os.path.join(os.path.abspath('.'), path))
    return os.path.join(os.path.abspath('.'), path)
