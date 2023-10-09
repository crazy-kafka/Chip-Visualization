from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

import pickle
import networkx as nx
import xlsxwriter
import copy
import pandas as pd
from utils import Print


class ReportDumper:
    '''support single report comparision report'''
    hier_info_label = 'info'
    base_info_label = 'base_info'
    info_types = ['block_name',
                  'total_cnt',
                  'total_area',
                  'pin_cnt',
                  'pin_cnt/cell_cnt',
                  'comb_cell(>4pins)_cnt',
                  'comb_cell(>4pins)_ratio',
                  'stdcell_cnt',
                  'stdcell_area',
                  'stdcell_bit',
                  'reg_cnt',
                  'reg_area',
                  'mbcell_bit',
                  'mb_ratio',
                  'bit/reg',
                  'mem_cnt',
                  'mem_bits',
                  'mem_area',
                  'leakage',
                  'SVT_RATIO',
                  'SVT_AREA',
                  'LVTLL_RATIO',
                  'LVTLL_AREA',
                  'LVT_RATIO',
                  'LVT_AREA',
                  'ULVTLL_RATIO',
                  'ULVTLL_AREA',
                  'ULVT_RATIO',
                  'ULVT_AREA',
                  'ELVT_RATIO',
                  'ELVT_AREA'
                  ]

    def __init__(self, ref_graph: nx.DiGraph, tar_graph=nx.DiGraph()):
        self.ref_graph = ref_graph
        self.tar_graph = tar_graph
        self.ref_name = ''
        self.tar_name = ''
        self.output_dict = {}

    def loadRefDB(self, db_file: str, db_name: str, custom_info_file=''):
        with open(db_file, 'rb') as fh:
            self.ref_graph = pickle.load(fh)
        self.ref_name = db_name
        Print(f'Loaded ref info {db_name} - {self.tar_name}')

    def __genVirtualCsv(self):
        dump_mode = 1
        if self.ref_graph.number_of_nodes() > 0 and self.tar_graph.number_of_nodes() > 0:
            dump_mode = 0
            Print('Dumping in comparision report mode')
        elif self.ref_graph.number_of_nodes() > 0 and self.tar_graph.number_of_nodes() == 0:
            Print(f'Dumping in single report mode')
        else:
            Print(f'Reference DB is not loaded')
        self.output_dict['base_info'] = []
        self.output_dict['hierarchical_info'] = []
        if dump_mode == 1:
            self.output_dict['base_info'].append(self.info_types)
            for node in self.ref_graph.nodes:
                line = [node]
                info = self.ref_graph.nodes[node][self.base_info_label]
                for info_type in self.info_types[1:]:
                    line.append(info[info_type])
                self.output_dict['base_info'].append(line)
            #extract hierarchy info
            root_list = []
            for node in self.ref_graph.nodes:
                if self.ref_graph.in_degree[node] == 0:
                    root_list.append(node)
            graph_depth = nx.dag.dag_longest_path_length(self.ref_graph)
            self.output_dict['hierarchical_info'].append(['*'] * graph_depth + self.info_types)
            for root in root_list:
                lines = []
                self.buildHierarchyLine(self.ref_graph, root, graph_depth, graph_depth, lines)
                self.output_dict['hierarchical_info'] += lines
        elif dump_mode == 0:
            header = [self.info_types[0]]
            for info_type in self.info_types[1:]:
                header += [self.ref_name + info_type, self.tar_name + info_type, info_type + '_diff']
            self.output_dict['base_info'].append(header)
            for node in self.ref_graph.nodes:
                line = [node]
                ref_info = self.ref_graph.nodes[node][self.base_info_label]
                if node in self.tar_graph:
                    tar_info = self.tar_graph.nodes[node][self.base_info_label]
                else:
                    tar_info = copy.deepcopy(ref_info)
                    for k in tar_info:
                        tar_info[k] = 'nan'
                for info_type in self.info_types[1:]:
                    ref_data = ref_info[info_type]
                    tar_data = tar_info[info_type]
                    if tar_data != 'nan':
                        if tar_data == 0:
                            diff = 'nan'
                        else:
                            diff = f'{round((ref_data - tar_data)/tar_data*100, 3)}%'
                    else:
                        diff = 'nan'
                    line += [ref_data, tar_data, diff]
                self.output_dict['base_info'].append(line)
            root_list = []
            for node in self.ref_graph.nodes:
                if self.ref_graph.in_degree[node] == 0:
                    root_list.append(node)
            graph_depth = nx.dag.dag_longest_path_length(self.ref_graph)
            header = ['*'] * graph_depth + [self.info_types[0]]
            for info_type in self.info_types[1:]:
                header += [self.ref_name + info_type, self.tar_name + info_type, info_type + '_diff']
            self.output_dict['hierarchical_info'].append(header)
            for root in root_list:
                lines = []
                self.buildDiffHierarchyLine(self.ref_graph, self.tar_graph, root, graph_depth, graph_depth, lines)
                self.output_dict['hierarchical_info'].append(header)
        for _, lines in self.output_dict.items():
            for line in lines:
                for idx, data in enumerate(line):
                    if isinstance(data, float):
                        line[idx] = round(data, 3)

    def dumpXlsx(self):
        self.__genVirtualCsv()
        outfile_name = f'{self.ref_name}{"_" + self.tar_name + ".compare" if self.tar_name else ""}.xlsx'
        workbook = xlsxwriter.Workbook(filename=outfile_name)
        bias_format = workbook.add_format()
        bias_format.set_bg_color('block')

        for sheet_name, content in self.output_dict.items():
            worksheet = workbook.add_worksheet(name=sheet_name)
            for row, line in enumerate(content):
                for col, cell in enumerate(line):
                    worksheet.write(row, col, cell)
                bias_merge_left = 0
                bias_merge_right = 0
                for col, cell in enumerate(line):
                    if cell != "*":
                        bias_merge_right = col
                        if bias_merge_right > bias_merge_left + 1:
                            worksheet.merge_range(row, bias_merge_left, row, bias_merge_right - 1, '', bias_format)
                        elif bias_merge_right == bias_merge_left + 1:
                            worksheet.write(row, bias_merge_left, '', bias_format)
                        break
                name_merge_right = bias_merge_right
                for col, cell in enumerate(line):
                    if col >= name_merge_right + 1:
                        if cell != '*':
                            name_merge_right = col
                            if name_merge_right > bias_merge_right + 1:
                                worksheet.merge_range(row, bias_merge_right, row, name_merge_right - 1, line[bias_merge_right])
                            break
        Print(f'Dump report xlsx file {outfile_name}')
        workbook.close()

    @staticmethod
    def buildHierarchyLine(graph: nx.DiGraph, root: str, bias: int, _bias: int, lines: list):
        line = ['*'] * (bias - _bias) + [root] + ['*'] * _bias
        info = graph.nodes[root][ReportDumper.hier_info_label]
        for info_type in ReportDumper.info_types[1:]:
            line.append(info[info_type])
        lines.append(line)
        for node in graph.neighbors(root):
            ReportDumper.buildHierarchyLine(graph, node, bias, _bias-1, lines)

    @staticmethod
    def buildDiffHierarchyLine(ref_graph: nx.DiGraph, tar_graph: nx.DiGraph, root: str, bias: int, _bias: int, lines: list):
        line = ['*'] * (bias - _bias) + [root] + ['*'] * _bias
        ref_info = ref_graph.nodes[root][ReportDumper.hier_info_label]
        if root in tar_graph:
            tar_info = tar_graph.nodes[root][ReportDumper.hier_info_label]
        else:
            tar_info = copy.deepcopy(ref_info)
            for k in tar_info:
                tar_info[k] = 'nan'
        for info_type in ReportDumper.info_types[1:]:
            ref_data = ref_info[info_type]
            tar_data = tar_info[info_type]
            if tar_data != 'nan':
                if tar_data == 0:
                    diff = 'nan'
                else:
                    diff = f'{round((ref_data - tar_data) / tar_data * 100 , 3)}%'
            else:
                diff = 'nan'
            line += [ref_data, tar_data, diff]

        lines.append(line)
        for node in ref_graph.neighbors(root):
            ReportDumper.buildDiffHierarchyLine(ref_graph, tar_graph, node, bias, _bias - 1, lines)












