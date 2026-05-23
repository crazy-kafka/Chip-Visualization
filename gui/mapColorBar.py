from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from PyQt5 import QtWidgets, QtCore, QtGui


class ColorLabel(QtWidgets.QLabel):

    HEIGHT = 30
    WIDTH = 72

    def __init__(self, colors: List[QtGui.QBrush], parent=None):
        super(ColorLabel, self).__init__(parent=parent)
        self.colors = colors
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setStyleSheet("border: 1px solid black;")

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(ColorLabel, self).paintEvent(a0)
        painter = QtGui.QPainter(self)
        gradient = QtGui.QLinearGradient(0, 0, self.WIDTH, 0)
        n = max(len(self.colors) - 1, 1)
        for ii, brush in enumerate(self.colors):
            gradient.setColorAt(ii / n, brush.color())
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawRect(0, 0, self.WIDTH, self.HEIGHT)


class MapColorBar(QtWidgets.QWidget):

    def __init__(self, colors: List[QtGui.QBrush], parent=None):
        super(MapColorBar, self).__init__(parent=parent)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.max_line_edit = QtWidgets.QLineEdit()
        self.min_line_edit = QtWidgets.QLineEdit()
        self.color_label = ColorLabel(colors)

        self.max_v = 1.0
        self.min_v = 0.0

        self.initUi()
        self.updateMax(1.0)
        self.updateMin(1.0)

    def initUi(self):
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.max_line_edit)
        self.main_layout.addWidget(self.color_label)
        self.main_layout.addWidget(self.min_line_edit)

        self.max_line_edit.setReadOnly(True)
        self.max_line_edit.setFixedSize(60, 25)
        self.max_line_edit.setAlignment(QtCore.Qt.AlignRight)

        self.min_line_edit.setReadOnly(True)
        self.min_line_edit.setFixedSize(60, 25)
        self.min_line_edit.setAlignment(QtCore.Qt.AlignRight)

    def updateMax(self, max_v: float):
        self.max_v = max_v
        self.max_line_edit.setText(str(self.max_v))

    def updateMin(self, min_v: float):
        self.min_v = min_v
        self.min_line_edit.setText(str(self.min_v))








