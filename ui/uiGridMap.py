from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dataBase import DbDataBase
    from dataBase.dbHInst import DbHInst
    from gui import Workspace

import numpy as np
import math
from shapely.geometry import Polygon
from dataBase import DbGridMap
from gui import GridPixMapItem
from PyQt5 import QtWidgets, QtCore, QtGui
from utils import Print, polygonPartitioning


class UiGridMap:

    def __init__(self, map_name: str, grid: np.ndarray, grid_size: float, workspace: Workspace):
        self.__workspace = workspace
        self.__view = workspace.view
        self.__grid_map =DbGridMap(map_name=map_name, grid=grid, grad_colors=self.__view.HEATMAP_COLORS)
        self.__grid_map.updateColorGrid()
        self.__grid_size = grid_size
        self.__initView()

        self.isShowed = False

    def savePicture(self, pic_name: str):
        image_array = np.flip(self.__grid_map.color_grid_image[:, :, 0:3], 0).copy()
        image = QtGui.QImage(image_array, image_array.shape[1], image_array.shape[0], QtGui.QImage.Format_RGBA8888)
        image.save(pic_name)

    def updateGrid(self, grid: np.array):
        if grid.shape != self.grid.shape:
            Print(f'Error, input grid shape {grid.shape} does not match original shape {self.grid.shape}')
        self.__grid_map.grid = grid
        self.__grid_map.updateColorGrid()
        self.__updateView()

    def setUpperValue(self, v: float):
        self.__grid_map.max = v
        self.__grid_map.updateColorGrid()
        self.__updateView()
        self.__workspace.grid_map_panel.color_bar.updateMax(v)

    def setLowerValue(self, v: float):
        self.__grid_map.min = v
        self.__grid_map.updateColorGrid()
        self.__updateView()
        self.__workspace.grid_map_panel.color_bar.updateMin(v)

    def showMap(self):
        if self.isShowed is False:
            self.__view.sceneObj.addItem(self.__pixMapItem)
        self.isShowed = True

    def hideMap(self):
        if self.isShowed is True:
            self.__view.sceneObj.removeItem(self.__pixMapItem)
        self.isShowed = False

    def __initView(self):
        self.__pixMapItem = GridPixMapItem(image_array=self.__grid_map.color_grid_image, grid_size=self.__grid_size)

    def __updateView(self):
        if self.isShowed:
            self.__view.sceneObj.removeItem(self.__pixMapItem)
        self.__pixMapItem = GridPixMapItem(image_array=self.__grid_map.color_grid_image, grid_size=self.__grid_size)
        if self.isShowed:
            self.__view.sceneObj.addItem(self.__pixMapItem)

    @property
    def grid_size(self) -> float:
        return self.__grid_size

    @property
    def grid(self) -> np.ndarray:
        return self.__grid_map.grid

    @property
    def color_grid(self) -> np.ndarray:
        return self.__grid_map.color_grid_image

    @property
    def upper_value(self) -> float:
        return self.__grid_map.max

    @property
    def lower_value(self) -> float:
        return self.__grid_map.min

    @staticmethod
    def grid2Box(ii: int, jj: int, grid_size: float):
        return [(ii * grid_size, jj * grid_size),
                (ii * grid_size, jj * grid_size),
                (ii * grid_size + grid_size, jj * grid_size + grid_size),
                (ii * grid_size, jj * grid_size + grid_size)]












