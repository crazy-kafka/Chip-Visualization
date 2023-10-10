from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dataBase.dbInst import DbInst
    from dataBase import DbDataBase

from .genericView import GenericGraphicsView
from .instItem import InstItem
from .wireItem import WireItem
from PyQt5 import QtWidgets, QtCore, QtGui
from dataBase.dbHInst import DbHInst
# from .attribuetPanel import AttributePanel
# from .attribuetPanel import AttributePanel


class MainView(GenericGraphicsView):
    sigSelectOneItem = QtCore.pyqtSignal(object)

    HEATMAP_COLORS: List[QtGui.QBrush] = [QtGui.QBrush(QtGui.QColor(255, 255, 255, 150)),
                                          QtGui.QBrush(QtGui.QColor(255, 0, 0, 155)),
                                          QtGui.QBrush(QtGui.QColor(255, 128, 0, 150)),
                                          QtGui.QBrush(QtGui.QColor(255, 255, 0, 150)),
                                          QtGui.QBrush(QtGui.QColor(128, 255, 0, 150)),
                                          QtGui.QBrush(QtGui.QColor(0, 204, 102, 150)),
                                          QtGui.QBrush(QtGui.QColor(0, 255, 255, 150)),
                                          QtGui.QBrush(QtGui.QColor(0, 128, 255, 150)),
                                          QtGui.QBrush(QtGui.QColor(0, 0, 255, 150)),
                                          QtGui.QBrush(QtGui.QColor(0, 0, 102, 150)),
                                          QtGui.QBrush(QtGui.QColor(0, 0, 52, 150)),
                                          QtGui.QBrush(QtGui.QColor(0, 0, 0, 150))]

    def __init__(self, db: DbDataBase, view_tag: str, parent=None):
        super(MainView, self).__init__(parent=parent)
        self.db = db
        self.view_tag = view_tag
        self.enableFitKet()
        self.setAntialiasing(True)
        self.flipY()
        self.highlighted_items: List[Union[InstItem, WireItem]] = []
        self.__connectSignal()
        self.__attributePanel = None

    def addPtn(self, inst_obj: DbHInst):
        inst_item = InstItem(inst_obj)
        self.sceneObj.addItem(inst_item)

    def __connectSignal(self):
        self.sigSelectPos.connect(self.highlightItemAt)

    def highlightItemAt(self, pos: QtCore.QPoint):
        items = self.items(pos)
        items = sorted(items, key=lambda  x: x.zValue(), reverse=True)
        if items:
            self.highlightItem([items[0]])
        else:
            self.highlightItem([])

    def highlightItem(self, items, append=False):
        if append is False:
            self.deselectAll()
        if items:
            for item in items:
                if hasattr(item, 'highlight') and hasattr(item, 'db_obj'):
                    item.highlight()
                    self.highlight_item.append(item)
                    self.sigSelectOneItem.emit(item.db_obj)

    def deselectAll(self):
        while self.highlighted_items:
            self.highlighted_items.pop(-1).deHighlight()
            self.sigSelectOneItem.emit(None)

    def zoomBox(self, b: Tuple[float, float, float, float]):
        rect = QtCore.QRectF(b[0], b[1], b[2] - b[0], b[3] - b[1])
        self.setRange(newRect=rect, padding=0)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super(MainView, self).keyPressEvent(event)

        rect = self.viewRect()
        x = rect.x()
        y = rect.y()
        width = rect.width()
        height = rect.height()
        factor = 0.25

        if event.key() == QtCore.Qt.Key_Up:
            x0 = x
            y0 = y + height * factor
            self.zoomBox((round(x0, 3), round(y0, 3), round(width + x0, 3), round(height + y0, 3)))
        elif event.key() == QtCore.Qt.Key_Down:
            x0 = x
            y0 = y - height * factor
            self.zoomBox((round(x0, 3), round(y0, 3), round(width + x0, 3), round(height + y0, 3)))
        elif event.key() == QtCore.Qt.Key_Left:
            x0 = x - width * factor
            y0 = y
            self.zoomBox((round(x0, 3), round(y0, 3), round(width + x0, 3), round(height + y0, 3)))
        elif event.key() == QtCore.Qt.Key_Right:
            x0 = x + width * factor
            y0 = y
            self.zoomBox((round(x0, 3), round(y0, 3), round(width + x0, 3), round(height + y0, 3)))
        elif event.key() == QtCore.Qt.Key_R:
            self.zoomBox(self.range)

