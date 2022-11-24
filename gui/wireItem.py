from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from dataBase.dbWire import DbWire

from PyQt5 import QtWidgets, QtCore, QtGui
from .palette import Palette
from .guiVariable import GuiVariable


class WireItem(QtWidgets.QGraphicsRectItem):

    brush_style = QtCore.Qt.BDiagPattern
    pen_width = 2

    highlight_pen = QtGui.QPen(QtGui.QColor(255, 255, 255))
    highlight_pen.setWidth(1)
    highlight_pen.setCosmetic(True)

    def __init__(self, wire: DbWire, parent=None):
        super(WireItem, self).__init__(parent=parent)
        self.db_obj = wire
        self.__initUi()

    def __initUi(self):
        color = Palette.layer_colors[self.db_obj.layer.idx]
        self.pen = QtGui.QPen(color)
        self.pen.setCosmetic(True)
        self.brush = QtGui.QBrush(color)
        self.brush.setStyle(self.brush_style)
        self.setBrush(self.brush)
        x0 = min([pt[0] for pt in self.db_obj.shape])
        y0 = min([pt[1] for pt in self.db_obj.shape])
        x1 = max([pt[0] for pt in self.db_obj.shape])
        y1 = max([pt[1] for pt in self.db_obj.shape])
        self.setRect(x0, y0, round(x1 - x0, 4), round(y1 - y0, 4))
        self.setZValue(GuiVariable.WIRE_BASE_ZVALUE + 0.01 * self.db_obj.layer.idx)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: Optional[QtWidgets.QWidget] = ...) -> None:
        self.brush.setTransform(painter.transform().inverted()[0])
        self.setBrush(self.brush)
        super(WireItem, self).paint(painter, option, widget)

    def highlight(self):
        self.setPen(self.highlight_pen)

    def deHighlight(self):
        self.setPen(self.pen)







