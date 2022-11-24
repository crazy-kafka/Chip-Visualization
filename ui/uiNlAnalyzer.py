from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dataBase import DbDataBase


import pickle
import pandas as pd
import networkx as nx
from nlChecker import NlChecker, ReportDumper


class UiNlAnalyzer:

    def __init__(self, dataBase: DbDataBase, nl_dict: Dict[str, str]):
         self.__nlChecker = NlChecker(dataBase, nl_dict)
         self.__reporter = ReportDumper(self.__nlChecker.hierarchy_graph)

    def dumpXlsxReport(self, tag: str, tar_tag='', tar_graph=None):
        self.__reporter.ref_name = tag
        if tar_tag:
            self.__reporter.loadTarDB(tar_graph, tar_tag)
        self.__reporter.dumpXlsx()

    def getNlBaseInfo(self, block_name: str) -> pd.Series:
        return pd.Series(self.__nlChecker.hierarchy_graph.nodes[block_name]['base_info'])

    def getNlInfo(self, block_name: str) -> pd.Series:
        return pd.Series(self.__nlChecker.hierarchy_graph.nodes[block_name]['info'])

    @property
    def graph(self) -> nx.DiGraph:
        return self.__nlChecker.hierarchy_graph

    def saveGraph(self, out_file: str):
        with open(out_file, 'wb') as fh:
            pickle.dump(self.graph, fh)






