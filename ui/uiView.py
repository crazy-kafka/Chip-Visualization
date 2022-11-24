from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from gui import Workspace
    from dataBase import DbDataBase

import numpy as np
import math
from shapely.geometry import Polygon
from .uiGridMap import UiGridMap
from utils import Print, PSTATUS


class UiView:

    def __init__(self, db: DbDataBase, workspace: Workspace):
        self.__db = db
        self.__workspace = workspace
        self.__workspace.setUiView(self)
        self.__view = workspace.view
        self.__initializeView()
        self.__gridmaps: Dict[str, UiGridMap] = {}
        self.__workspace.grid_map_panel.stateSig.connect(self.__showHideMap)

    def __showHideMap(self, map_name: str, flag: bool):
        if map_name in self.__gridmaps:
            if flag is True:
                self.__gridmaps[map_name].showMap()
                self.__workspace.grid_map_panel.color_bar.updateMax(self.__gridmaps[map_name].upper_value)
                self.__workspace.grid_map_panel.color_bar.updateMin(self.__gridmaps[map_name].lower_value)
            else:
                self.__gridmaps[map_name].hideMap()
        else:
            Print(f'Error, {map_name} does not exist')

    def __initializeView(self):
        self.__view.addPtn(self.__db.chip.hInst)
        for hInst_name, hInst in self.__db.chip.hInst.treeHInsts.items():
            if hInst.is_ptn:
                self.__view.addPtn(hInst)
        self.__view.updateBoundingRect()
        self.__view.fit()

    def addItem(self, item):
        self.__view.sceneObj.removeItem(item)

    def viewBox(self) -> Tuple[float, float, float, float]:
        rect = self.__view.range
        x = rect.x()
        y = rect.y()
        width = rect.width()
        height = rect.height()
        return round(x, 3), round(y, 3), round(width + x , 3), round(height + y, 3)

    def zoomBox(self, box: Tuple[float, float, float, float]):
        self.__view.zoomBox(b=box)

    @property
    def viewTag(self):
        return self.__view.view_tag

    '''----------------- database head -----------------'''
    def showInst(self, inst_name: str):
        if isinstance(inst_name, list):
            for ii in inst_name:
                self.showInst(ii)
        inst_item = self.__workspace.parent_window.insts[inst_name]
        if inst_item.scene() is None and inst_item.db_obj.pstatus != PSTATUS.UNPLACED:
            self.__view.sceneObj.addItem(inst_item)

    def hideInst(self, inst_name: str):
        if isinstance(inst_name, list):
            for ii in inst_name:
                self.hideInst(ii)
        inst_item = self.__workspace.parent_window.insts[inst_name]
        if inst_item.scene() is not None:
            self.__view.sceneObj.removeItem(inst_item)

    def showNet(self, net_name: str):
        if isinstance(net_name, list):
            for ii in net_name:
                self.showNet(ii)
        if net_name in self.__workspace.parent_window.net_wire_dict:
            wire_items = self.__workspace.parent_window.net_wire_dict[net_name]
            for wire in wire_items:
                if wire.scene() is None:
                    self.__view.sceneObj.addItem(wire)

    def hideNet(self, net_name: str):
        if isinstance(net_name, list):
            for ii in net_name:
                self.hideNet(ii)
        if net_name in self.__workspace.parent_window.net_wire_dict:
            wire_items = self.__workspace.parent_window.net_wire_dict[net_name]
            for wire in wire_items:
                if wire.scene() is not None:
                    self.__view.sceneObj.removeItem(wire)

    def selectInst(self, inst_name: str):
        if isinstance(inst_name, list):
            for ii in inst_name:
                self.selectInst(ii)
        inst_item  = self.__workspace.parent_window.insts[inst_name]
        self.__view.highlighted_items([inst_item], append=True)

    def selectNet(self, net_name: str):
        if isinstance(net_name, list):
            for ii in net_name:
                self.selectNet(ii)
        if net_name in self.__workspace.parent_window.net_wire_dict:
            wire_items = self.__workspace.parent_window.net_wire_dict[net_name]
            self.__view.highlighted_items(wire_items, append=True)

    def deselectAll(self):
        self.__view.deselectAll()
    '''----------------- database tail -----------------'''

    '''----------------- grid map head -----------------'''
    @property
    def gridMaps(self) -> Dict[str, UiGridMap]:
        return self.__gridmaps

    def createGridMap(self, map_name: str, grid: np.ndarray, grid_size: int) -> UiGridMap:
        if map_name not in self.__gridmaps:
            self.__workspace.grid_map_panel.stateSig.disconnect(self.__showHideMap)

            Print(f'Create grid map {map_name} with grid {grid.shape[0]} X {grid.shape[1]} grid size {grid_size}')
            self.__gridmaps[map_name] = UiGridMap(map_name=map_name, grid=grid, grid_size=grid_size, workspace=self.__workspace)
            self.__workspace.grid_map_panel.addGridMap(map_name)

            self.__workspace.grid_map_panel.stateSig.connect(self.__showHideMap)
            return self.__gridmaps[map_name]
        else:
            Print(f'grid map "{map_name}" already exists, failed to create', level='error')
            return None







