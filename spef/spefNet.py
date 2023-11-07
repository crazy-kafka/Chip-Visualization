from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING, Match

if TYPE_CHECKING:
    pass

from utils import Print
import networkx as nx


class SpefNet(nx.DiGraph):

    def __init__(self, net_name: AnyStr, total_cap: float):
        super().__init__()
        self.net_name = net_name
        self.total_cap = total_cap
        self.pts = {}

    def setCNode(self, idx: int, cap: float, couple_cap: float):
        if idx in self.nodes:
            if cap is None and isinstance(couple_cap, float):
                self.nodes[idx]['couple_cap'] += couple_cap
            else:
                self.nodes[idx]['cap'] = cap
        else:
            if cap is None and isinstance(couple_cap, float):
                self.add_node(idx, cap=0.0, couple_cap=couple_cap)
            else:
                self.add_node(idx, cap=cap, couple_cap=0.0)

    def setREdge(self, idx_from: int, idx_to: int, res: float):
        self.add_edge(idx_from, idx_to, res=res)

    def __repr__(self):
        return f'''Spef Net
  net name: {self.net_name}
  total cap: {self.total_cap}
  node count: {self.number_of_nodes()}
  edge count: {self.number_of_edges()}
'''


