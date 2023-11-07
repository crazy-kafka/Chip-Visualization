from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from utils import Print, readFileLines
from .compileRe import CompileRe
from .spefNet import SpefNet


class SpefParser:

    def __init__(self, spef_file: AnyStr):
        self.spef_file = spef_file
        self.name_map: Dict[AnyStr, AnyStr] = {}
        self.ports: Dict[AnyStr, AnyStr] = {}
        self.nets: Dict[AnyStr, SpefNet] = {}
        self.cursor = 0

        self.parseStart()

    def parseStart(self):
        allLines = readFileLines(self.spef_file)
        line_cnt = len(allLines)
        Print(f'Start parsing spef file {self.spef_file}, total {line_cnt} lines')
        # 0 -> name_map mode
        # 1 -> port mode
        # 2 -> net mode
        flag = 0
        while self.cursor < line_cnt:

            if match := CompileRe.re_NET.search(allLines[self.cursor]):
                flag = 2
                try:
                    net_name = self.name_map[match['id']]
                except KeyError:
                    net_name = match['id']
                    print(match['id'])
                net = SpefNet(net_name, float(match['total_cap']))
                while CompileRe.END_FLAG not in allLines[self.cursor]:
                    #print(allLines[self.cursor])
                    self.cursor += 1
                    if CompileRe.CONN_flag in allLines[self.cursor]:
                        self.__parseConn(net, allLines)
                    elif CompileRe.RES_flag in allLines[self.cursor]:
                        self.__parseRes(net, allLines)
                    elif CompileRe.CAP_flag in allLines[self.cursor]:
                        self.__parseCap(net, allLines)
                self.nets[net.net_name] = net
            elif flag == 0:
                if match := CompileRe.re_map.search(allLines[self.cursor]):
                    self.name_map[match['to']] = match['from']
                    self.cursor += 1
                    continue
            elif flag == 1:
                if match := CompileRe.re_port.search(allLines[self.cursor]):
                    self.ports[match['idx']] = match['direction']
                    self.cursor += 1
                    continue
            if CompileRe.NAME_MAP_FLAG in allLines[self.cursor]:
                flag = 0
            elif CompileRe.PORTS_FLAG in allLines[self.cursor]:
                flag = 1

            self.cursor += 1

    def __parseConn(self, net: SpefNet, allLines: List[AnyStr]):
        self.cursor += 1
        # while CompileRe.END_FLAG not in allLines[self.cursor] \
        #         and CompileRe.CAP_flag not in allLines[self.cursor] \
        #         and CompileRe.RES_flag not in allLines[self.cursor]:
        while match := CompileRe.re_conn.search(allLines[self.cursor]):
            name = match['name']
            if ':' in name:
                ii, jj = name.split(':')
                name = self.name_map[ii] + '/' + jj
            else:
                name = self.name_map[name]
            pt_type = match['pt_type']
            direction = match['direction']
            x = float(match['x'])
            y = float(match['y'])
            cell = match['ref_name']
            net.pts[name] = {
                'pt_type': pt_type,
                'direction': direction,
                'x': x,
                'y': y,
                'ref_name': cell
            }
            self.cursor += 1

    def __parseCap(self, net: SpefNet, allLines: List[AnyStr]):
        self.cursor += 1
        while match := CompileRe.re_cap.search(allLines[self.cursor]):
            node = match['node']
            couple_node = match['couple_node']
            value = float(match['value'])
            if couple_node:
                net.setCNode(node, cap=None, couple_cap=value)
            else:
                net.setCNode(node, cap=value, couple_cap=None)
            self.cursor += 1

    def __parseRes(self, net: SpefNet, allLines: List[AnyStr]):
        self.cursor += 1
        while match := CompileRe.re_res.search(allLines[self.cursor]):
            node_0 = match['node_0']
            node_1 = match['node_1']
            value = float(match['value'])
            net.setREdge(node_0, node_1, value)
            self.cursor += 1

    def __repr__(self):
        return f'''SpefParer
  spef file: {self.spef_file}
  net count: {len(self.nets)}
  port count： {len(self.ports)}
'''

