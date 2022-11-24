from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np

from .guiVariable import GuiVariable


class GridPixMapItem(QtWidgets.QGraphicsPixmapItem):

    def __init__(self, image_array: np.ndarray, grid_size: float, parent=None):
        self.array = image_array
        self.image = QtGui.QImage(image_array, image_array.shape[1], image_array.shape[0], QtGui.QImage.Format_RGBA8888)
        self.grid_size = grid_size
        super(GridPixMapItem, self).__init__(QtGui.QPixmap(self.image), parent=parent)
        self.setTransform(QtGui.QTransform(self.grid_size, 0, 0, self.grid_size, 0, 0))
        self.setZValue(GuiVariable.PIX_MAP_ZVALUE)




