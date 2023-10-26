from __future__ import annotations

import copy
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5 import QtWidgets, QtCore, QtGui

import numpy as np
from utils import Print
from .dbBaseObj import DbBaseObj


class DbGridMap(DbBaseObj):

    def __init__(self, map_name: str, grid: np.ndarray, grad_colors: List[QtGui.QBrush]):
        super(DbGridMap, self).__init__(map_name)
        self.grid = grid
        self.grid[np.isinf(self.grid)] = np.nan
        self.color_grid = np.zeros(self.grid.shape, dtype=int)
        self.color_grid_image = np.zeros((self.grid.shape[0], self.grid.shape[1], 4), dtype=np.uint8)
        self.grade_color = grad_colors
        self.grade_cnt = len(self.grade_color) - 1
        self.max = np.max(self.grid[~np.isnan(self.grid)])
        self.min = np.min(self.grid[~np.isnan(self.grid)])

    def updateColorGrid(self):

        self.max = round(self.max, 3)
        self.min = round(self.min, 3)

        grid = copy.deepcopy(self.grid)
        grid[grid >= self.max] = self.max
        grid[grid <= self.min] = self.min

        nan = -1234567

        self.color_grid = self.grade_cnt - np.ceil(self.grade_cnt * (grid - self.min) / (self.max - self.min)).astype(int)
        self.color_grid[np.isnan(self.grid)] = nan

        for ii in range(0, self.color_grid.shape[0]):
            for jj in range(0, self.color_grid.shape[1]):
                if self.color_grid[ii][jj] == nan:
                    self.color_grid_image[ii][jj] = np.array([0, 0, 0, 0])
                else:
                    self.color_grid_image[ii][jj][0] = self.grade_color[self.color_grid[ii][jj]].color().red()
                    self.color_grid_image[ii][jj][1] = self.grade_color[self.color_grid[ii][jj]].color().green()
                    self.color_grid_image[ii][jj][2] = self.grade_color[self.color_grid[ii][jj]].color().blue()
                    self.color_grid_image[ii][jj][3] = 150


