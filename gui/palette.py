from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from PyQt5 import QtGui

class Palette:

    layer_colors = [
        QtGui.QColor(244, 187, 68),  #0
        QtGui.QColor(0, 0, 255),     #1
        QtGui.QColor(255, 0, 0),     #2
        QtGui.QColor(0, 255, 0),     #3
        QtGui.QColor(243, 229, 171), #4
        QtGui.QColor(149, 53, 83),   #5
        QtGui.QColor(255, 192, 0),   #6
        QtGui.QColor(127, 0, 255),   #7
        QtGui.QColor(0, 200, 200),   #8
        QtGui.QColor(114, 47, 55),   #9
        QtGui.QColor(255, 255, 143), #10
        QtGui.QColor(9, 121, 105),   #11
        QtGui.QColor(255, 0, 255),   #12
        QtGui.QColor(243, 207, 198), #13
        QtGui.QColor(0, 255, 255),   #14
        QtGui.QColor(93, 63, 211),   #15
        QtGui.QColor(139, 128, 0),   #16
        QtGui.QColor(255, 170, 51)   #17
    ]


