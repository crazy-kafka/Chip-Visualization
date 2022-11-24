from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    pass

from PyQt5 import QtWidgets, QtCore, QtGui
from .guiVariable import GuiVariable
from dataBase.dbHInst import DbHInst
from dataBase.dbInst import DbInst
from utils import Print


class InstItem(QtWidgets.QGraphicsPolygonItem):

    ptn_pen = QtGui.QPen(QtGui.QColor(72, 72, 72))
    ptn_pen.setWidthF(0.5)
    ptn_pen.setCosmetic(True)
    ptn_brush = QtGui.QBrush(QtGui.QColor(128, 128, 128))

    obs_pen = QtGui.QPen(QtGui.QColor(192, 192, 192))
    obs_pen.setWidthF(0.5)
    obs_pen.setCosmetic(True)
    obs_brush = QtGui.QBrush(QtGui.QColor(33, 33, 33))
    obs_brush.setStyle(QtCore.Qt.Dense4Pattern)

    inst_pen = QtGui.QPen(QtGui.QColor(28, 79, 114))
    inst_pen.setWidthF(0.5)
    inst_pen.setCosmetic(True)
    inst_brush = QtGui.QBrush(QtGui.QColor(27, 79, 114))
    inst_brush.setStyle(QtCore.Qt.Dense2Pattern)

    highlight_pen = QtGui.QPen(QtGui.QColor(255, 255, 255))
    highlight_pen.setWidthF(2.0)
    highlight_pen.setStyle(QtCore.Qt.DashLine)
    highlight_pen.setCosmetic(True)

    def __init__(self, db_obj: Union[DbHInst, DbInst], parent=None):
        super(InstIterm, self).__init__(parent=parent)
        self.db_obj = db_obj
        if type(db_obj) == DbHInst:
            self.toPtn()
        elif type(db_obj) == DbInst:
            self.toInst()
        self.zvalue = self.zValue()
        self.setShape(self.db_obj.shape)

    def setShape(self, polygon: List[Tuple]):
        point_list = []
        for point in polygon:
            point_list.append(QtCore.QPointF(point[0], point[1]))
        self.setPolygon(QtGui.QPolygonF(point_list))

    def highlight(self):
        self.setPen(self.highlight_pen)
        self.setZValue(1)

    def deHighlight(self):
        self.setPen(self.pen())
        self.setZValue(self.zvalue)

    def toPtn(self):
        self.pen = self.ptn_pen
        self.brush = self.ptn_brush
        self.setPen(self.ptn_pen)
        self.setBrush(self.ptn_brush)
        self.setZValue(self.db_obj.name.count('/') * GuiVariable.PTN_BASE_ZVALUE)

    def toObs(self):
        self.pen = self.obs_pen
        self.brush = self.obs_brush
        self.setPen(self.obs_pen)
        self.setBrush(self.obs_brush)

    def toInst(self):
        self.pen = self.inst_pen
        self.brush = self.inst_brush
        self.setPen(self.inst_pen)
        self.setBrush(self.inst_brush)
        self.setZValue((self.db_obj.name.count('/') + 1) * GuiVariable.INST_BASE_ZVALUE)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: Optional[QtWidgets.QWidget] = ...) -> None:
        self.brush.setTransform(painter.transform().inverted()[0])
        self.setBrush(self.brush)
        super().paint(painter, option, widget)

