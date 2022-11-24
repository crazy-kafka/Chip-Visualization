from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass


class LibertyCell:

    def __init__(self, cell_name: str):
        self.name = cell_name
        self.area = 0.0
        self.footprint = ''
        self.leakage = 0.0
        self.__lkg_cnt = 0

    def setArea(self, area: float):
        self.area = float(area)

    def setFootprint(self, footprint: str):
        self.footprint = footprint

    def setLeakage(self, leakage_power: float):
        leakage_power = float(leakage_power)
        self.leakage = (self.leakage * self.__lkg_cnt + leakage_power) / (self.__lkg_cnt + 1)
        self.__lkg_cnt += 1


