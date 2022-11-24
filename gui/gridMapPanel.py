from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from PyQt5 import QtWidgets, QtCore, QtGui
from .mapColorBar import MapColorBar


class GridMapPanel(QtWidgets.QGroupBox):

    stateSig = QtCore.pyqtSignal(str, bool)

    def __init__(self, colors: List[QtGui.QBrush], parent=None):
        super(GridMapPanel, self).__init__(parent=parent)
        self.setTitle('Grid Map Control Panel')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.list_widget = QtWidgets.QListWidget()
        self.color_bar = MapColorBar(colors)

        self.__initUi()
        self.__connSig()

    def __initUi(self):
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.list_widget)
        self.main_layout.addWidget(self.color_bar)

    def __connSig(self):
        self.list_widget.itemChanged.connect(self.__sendSig)

    def addGridMap(self, map_name: str):
        item = QtWidgets.QListWidgetItem(map_name)
        item.setCheckState(QtCore.Qt.Unchecked)
        self.list_widget.addItem(item)

    def __sendSig(self, item: QtWidgets.QListWidgetItem):
        self.stateSig.emit(item.text(), item.checkState() == QtCore.Qt.Checked)





