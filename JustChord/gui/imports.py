import sys
import os
from functools import *
from typing import *
from dataclasses import *
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pyqt5_material import apply_stylesheet

from JustChord.gui import monitor


def cache(func):
    _cache = dict()

    def cached_func(*args):
        if args in _cache:
            return _cache[args]
        result = func(*args)
        _cache[args] = result
        return result
    return cached_func

def debug(func):
    def foo(*args, **kwargs):
        print(func.__name__, args, kwargs)
        return func(*args, **kwargs)

    return foo


def resource_path(path):  # convert path for pyinstaller
    path = path.replace('/', os.sep)
    if hasattr(sys, '_MEIPASS'):
        # print('has,', os.path.join(sys._MEIPASS, path))
        return os.path.join(sys._MEIPASS, path)
    # print('no,', os.path.join(os.path.abspath('.'), path))
    return os.path.join(os.path.abspath('.'), path)
