import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from . import monitor


def debug(func):
    def foo(*args, **kwargs):
        print(func.__name__, args, kwargs)
        return func(*args, **kwargs)
    return foo
