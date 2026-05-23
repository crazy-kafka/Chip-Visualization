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


def _generateHeatmapColors(count: int = 128) -> List[QtGui.QBrush]:
    stops = [
        (0.0,   QtGui.QColor(255, 255, 255)),
        (0.1,   QtGui.QColor(255, 0, 0)),
        (0.2,   QtGui.QColor(255, 128, 0)),
        (0.3,   QtGui.QColor(255, 255, 0)),
        (0.4,   QtGui.QColor(128, 255, 0)),
        (0.5,   QtGui.QColor(0, 204, 102)),
        (0.6,   QtGui.QColor(0, 255, 255)),
        (0.7,   QtGui.QColor(0, 128, 255)),
        (0.8,   QtGui.QColor(0, 0, 255)),
        (0.9,   QtGui.QColor(0, 0, 102)),
        (1.0,   QtGui.QColor(0, 0, 0)),
    ]
    colors = []
    for i in range(count):
        t = i / (count - 1)
        for j in range(len(stops) - 1):
            if stops[j][0] <= t <= stops[j + 1][0]:
                t0, c0 = stops[j]
                t1, c1 = stops[j + 1]
                lt = (t - t0) / (t1 - t0)
                r = int(c0.red()   + (c1.red()   - c0.red())   * lt)
                g = int(c0.green() + (c1.green() - c0.green()) * lt)
                b = int(c0.blue()  + (c1.blue()  - c0.blue())  * lt)
                colors.append(QtGui.QBrush(QtGui.QColor(r, g, b, 150)))
                break
    return colors


class MainView(GenericGraphicsView):
    sigSelectOneItem = QtCore.pyqtSignal(object)

    HEATMAP_COLORS: List[QtGui.QBrush] = _generateHeatmapColors(128)

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
                    self.highlighted_items.append(item)
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

