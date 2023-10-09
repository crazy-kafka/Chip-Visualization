from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dataBase import DbDataBase
    from dataBase import DbMacro

import time
import re
import networkx as nx
import copy
from collections import Counter
from utils import Print, ConcurrentProcess
from verilog import InstExtractor


class NlChecker:

    cell_info_db = 'cell_info.db'
    mem_patt = 'memory'
    mem_bits_patt = r'(\d+)(?:x|X)(\d+)'
    reg_patt = '(mb)?.*sdf'

    def __init__(self, dataBase: DbDataBase, nl_dict: Dict[str, str]):
        Print(f'Netlist Checker Initialize')
        self.db = dataBase
        self.nl_dict = nl_dict
        self.nl_cell_dict: Dict[str, Counter] = {}
        self.nl_info_dict = {}
        self.module_list = []
        self.hierarchy_graph = nx.DiGraph()
        self.graph_level_dict = {}
        self.parseStart()
        #self.analyzeNlInfo()
        #self.constructHGraph()

    def __assignLevel(self, root, current_node):
        path_list = list(nx.all_simple_paths(self.hierarchy_graph, root, current_node))
        if path_list == []:
            self.graph_level_dict[current_node] = 0
        else:
            level = max([len(i) for i in path_list]) - 1
            if self.graph_level_dict[current_node] is not None:
                if level > self.graph_level_dict[current_node]:
                    self.graph_level_dict[current_node] = level
            else:
                self.graph_level_dict[current_node] = level
        for neighbor in self.hierarchy_graph.neighbors(current_node):
            self.__assignLevel(root, neighbor)

    def constructHGraph(self):
        Print(f'Construct hierarchy graph')
        for module, v in self.nl_info_dict.items():
            Print(f'  Add node {module}')
            self.hierarchy_graph.add_node(module,
                cell_list=copy.deepcopy(self.nl_cell_dict[module]),
                base_cell_list=copy.deepcopy(self.nl_cell_dict[module]),
                info=copy.deepcopy(v['info']),
                base_info=copy.deepcopy(v['info']))
            self.graph_level_dict[module] = None
        for this_module, v in self.nl_info_dict.items():
            for other_module in self.module_list:
                if other_module in self.nl_cell_dict[this_module]:
                    Print(f'  Add edge {this_module} -> {other_module}')
                    self.hierarchy_graph.add_edge(this_module, other_module)
        Print(f'  Assigning level to graph node')

        root_list = []
        for node in self.hierarchy_graph.nodes:
            if self.hierarchy_graph.in_degree[node] == 0:
                root_list.append(node)
        Print(f'  Assigning level to graph node.')
        root_list = []
        for node in self.hierarchy_graph.nodes:
            if self.hierarchy_graph.in_degree[node] == 0:
                root_list.append(node)
        print(f'  Find {root_list.__len__()} root node(s) {root_list}')
        for root in root_list:
            self.__assignLevel(root, root)
        graph_depth = nx.dag.dag_longest_path_length(self.hierarchy_graph)
        Print(f'  Bottom iterating')
        #bottom up iterate
        for level in range(graph_depth, -1 , -1):
            target_modules = [module for module, v in self.graph_level_dict.items() if v == level]
            Print(f'    Level {level} -> {target_modules}')
            for module in target_modules:
                for neighbor in self.hierarchy_graph.neighbors(module):
                    instantiate_cnt = self.nl_cell_dict[module][neighbor]
                    for k, v in self.hierarchy_graph.nodes[neighbor]['info'].items():
                        self.hierarchy_graph.nodes[module]['info'][k] += v * instantiate_cnt
                    for ii in range(0, instantiate_cnt):
                        self.hierarchy_graph.nodes[module]['cell_list'] += self.hierarchy_graph.nodes[neighbor]['cell_list']

        for module in self.hierarchy_graph.nodes:
            nl_info = self.hierarchy_graph.nodes[module]['info']
            vt_sum = sum(nl_info[ii] for ii in nl_info if ii.endswith('_RATIO'))
            for vt_type in [ii for ii in nl_info if ii.endswith('_RATIO')]:
                if vt_sum == 0:
                    nl_info[vt_type] = 0.0
                else:
                    nl_info[vt_type] = round(nl_info[vt_type] / vt_sum, 4)
            if nl_info['stdcell_bit'] == 0:
                nl_info['mb_ratio'] = 0.0
            else:
                nl_info['mb_ratio'] = round(nl_info['mbcell_bit'] / nl_info['stdcell_bit'], 4)
            if nl_info['reg_cnt'] == 0:
                nl_info['bit/reg'] = 0.0
            else:
                nl_info['bit/reg'] = round(nl_info['stdcell_bit'] / nl_info['reg_cnt'], 4)
            if nl_info['total_cnt'] == 0:
                nl_info['pin_cnt/cell_cnt'] = 0.0
            else:
                nl_info['pin_cnt/cell_cnt'] = round(nl_info['pin_cnt'] / nl_info['total_cnt'], 4)
            if nl_info['total_cnt'] == 0:
                nl_info['comb_cell(>4pins)_ratio'] = 0.0
            else:
                nl_info['comb_cell(>4pins)_ratio'] = round(nl_info['comb_cell(>4pins)_cnt'] / nl_info['total_cnt'], 4)

            for module in self.hierarchy_graph.nodes:
                nl_info = self.hierarchy_graph.nodes[module]['base_info']
                vt_sum = sum(nl_info[ii] for ii in nl_info if ii.endswith('_RATIO'))
                for vt_type in [ii for ii in nl_info if ii.endswith('_RATIO')]:
                    if vt_sum == 0:
                        nl_info[vt_type] = 0.0
                    else:
                        nl_info[vt_type] = round(nl_info[vt_type] / vt_sum, 4)
                if nl_info['stdcell_bit'] == 0:
                    nl_info['mb_ratio'] = 0.0
                else:
                    nl_info['mb_ratio'] = round(nl_info['mbcell_bit'] / nl_info['stdcell_bit'], 4)
                if nl_info['reg_cnt'] == 0:
                    nl_info['bit/reg'] = 0.0
                else:
                    nl_info['bit/reg'] = round(nl_info['stdcell_bit'] / nl_info['reg_cnt'], 4)
                if nl_info['pin_cnt'] == 0:
                    nl_info['pin_cnt/cell_cnt'] = 0.0
                else:
                    nl_info['pin_cnt/cell_cnt'] = round(nl_info['pin_cnt'] / nl_info['total_cnt'], 4)
                if nl_info['total_cnt'] == 0:
                    nl_info['comb_cell(>4pins)_ratio'] = 0.0
                else:
                    nl_info['comb_cell(>4pins)_ratio'] = round(nl_info['comb_cell(>4pins)_cnt'] / nl_info['total_cnt'], 4)

    def analyzeNlInfo(self):
        for module, v in self.nl_info_dict.items():
            self.module_list.append(module)
        Print(f'Start to analyze netlists')
        t0 = time.time()
        args_iterable = []
        for block in self.nl_info_dict:
            arguments = []
            arguments.append(block)
            arguments.append(self.nl_cell_dict[block])
            arguments.append(self.db.cells)
            arguments.append(self.mem_patt)
            arguments.append(self.mem_bits_patt)
            arguments.append(self.reg_patt)
            arguments.append(self.module_list)
            args_iterable.append(arguments)
        with ConcurrentProcess.MP_POOL(ConcurrentProcess.PROCESS_CNT) as pool:
            for block, nl_info in pool.map(self.analyzeNlWorker, args_iterable):
                self.nl_info_dict[block]['info'] = nl_info

        Print(f'Netlist analysis is done in {round(time.time() - t0, 2)}s')

    @staticmethod
    def analyzeNlWorker(args):
        top_name = args[0]
        cell_dict = args[1]
        db_cells = args[2]
        mem_patt = args[3]
        mem_bit_patt = args[4]
        reg_patt = args[5]
        module_list = args[6]
        Print(f'  Analyzing {top_name} netlist information, total {sum(list(cell_dict.values()))} instances')
        nl_info = {
            'pin_cnt': 0,
            'pin_cnt/cell_cnt': 0,
            'comb_cell(>4pins)_cnt': 0,
            'comb_cell(>4pins)_ratio': 0,
            'stdcell_bit': 0,
            'mbcell_bit': 0,
            'mb_ratio': 0,
            'bit/reg': 0,
            'mem_cnt': 0,
            'mem_bits': 0,
            'mem_area': 0,
            'stdcell_cnt': 0,
            'stdcell_area': 0,
            'reg_cnt': 0,
            'reg_area': 0,
            'total_cnt': 0,
            'total_area': 0,
            'leakage': 0,
            'SVT_RATIO': 0,
            'SVT_AREA': 0,
            'LVTLL_RATIO': 0,
            'LVTLL_AREA': 0,
            'LVT_RATIO': 0,
            'LVT_AREA': 0,
            'ULVTLL_RATIO': 0,
            'ULVTLL_AREA': 0,
            'ULVT_RATIO': 0,
            'ULVT_AREA': 0,
            'ELVT_RATIO': 0,
            'ELVT_AREA': 0
        }
        for cell, cnt in cell_dict.items():
            if cell not in db_cells:
                continue
            lib_info: DbMacro = db_cells[cell]
            if cell in db_cells:
                cell_pin_cnt = len([t for t in lib_info.terms.values() if t.use != 'GROUND' and t.use != 'POWER'])
                nl_info['pin_cnt'] += cnt * cell_pin_cnt
                nl_info['total_cnt'] += cnt
                nl_info['leakage'] += cnt * lib_info.leakage
                nl_info['total_area'] += cnt * lib_info.area
                if lib_info.footprint == '':
                    continue
                if re.search(mem_patt, lib_info.footprint):
                    nl_info['mem_cnt'] += cnt
                    nl_info['mem_area'] += cnt * lib_info.area
                    bits_match = re.search(mem_bit_patt, cell)
                    if bits_match:
                        nl_info['mem_bits'] += cnt * int(bits_match.group(1)) * int(bits_match.group(2))
                    else:
                        Print(f' Unrecognized memory bits for cell {cell} in {top_name}', level='error')
                    continue
                else:
                    nl_info['stdcell_cnt'] += cnt
                    nl_info['stdcell_area'] += cnt * lib_info.area
                if re.search(reg_patt, lib_info.footprint):
                    nl_info['reg_cnt'] += cnt
                    nl_info['reg_area'] += cnt * lib_info.area
                    mb_match = re.match(r'MB(\d+)', cell)
                    bit_num = 1
                    if mb_match:
                        bit_num = int(mb_match.group(1))
                        nl_info['mbcell_bit'] += cnt * bit_num
                    nl_info['stdcell_bit'] += cnt * bit_num
                else:
                    if cell_pin_cnt > 4:
                        nl_info['comb_cell(>4pins)_cnt'] += cnt
                vt_type = NlChecker.inferCellVtType(cell, lib_info)
                nl_info[f'{vt_type}_RATIO'] += cnt
                nl_info[f'{vt_type}_AREA'] += cnt * lib_info.area
            else:
                if cell not in module_list:
                    Print(f'  Cannot find [{cell}] in cell info dict. ({top_name})', level='error')

        Print(f'  Finish analyzing {top_name} netlist information')
        return top_name, nl_info

    def parseStart(self):
        args = []
        for k, v in self.nl_dict.items():
            args.append((k, v))
        with ConcurrentProcess.MP_POOL(ConcurrentProcess.PROCESS_CNT) as pool:
            for top_name, cell_dict in pool.map(nlParseWorker, args):
                self.nl_cell_dict[top_name] = cell_dict
                self.nl_info_dict[top_name] = {
                    'mem_cnt': 0,
                    'mem_area': 0,
                    'stdcell_cnt': 0,
                    'stdcell_area': 0,
                    'reg_cnt': 0,
                    'reg_area': 0,
                    'total_cnt': 0,
                    'total_area': 0,
                    'leakage': 0
                }

    @staticmethod
    def inferCellVtType(cell_name: str, lib_info: DbMacro):
        if lib_info.footprint == 'memory':
            match = re.search('s0g4(\w)', cell_name)
            if match:
                t = match.group(1)
                if t == 'u':
                    return 'ULVT'
                elif t == 'l':
                    return 'LVT'
                elif t == 's':
                    return 'SVT'
                elif t == 'e':
                    return 'ELVT'
            elif cell_name.startswith('TS3N05LVT'):
                return 'LVT'
        else:
            for vt_type in ['ULVTLL', 'ULVT', 'LVTLL', 'LVT', 'SVT', 'ELVT']:
                if cell_name.endswith(vt_type):
                    return vt_type
        Print(f'Unrecognized vt type for cell < {cell_name} > lib_info', level='error')

def nlParseWorker(args: List[str, str]) -> Tuple[str, Counter]:
    top_name = args[0]
    nl_file = args[1]
    cell_dict = Counter(InstExtractor(nl_file, top_name).insts.values())
    return top_name, cell_dict