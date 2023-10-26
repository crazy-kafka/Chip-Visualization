from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dataBase import DbChip
    from dataBase import DbMacro
    from dataBase import TechLayer
    from gui import MainView

import os
import sys
import math
import pickle
import time
from glob import glob
import numpy as np

from dataBase import DbDataBase
from gui import MainWindow
from .uiView import UiView
from utils import polygonPartitioning, Print, GlobalVariable, rectMapToPtnLocal
from gui.instItem import InstItem
from gui.wireItem import WireItem
from .uiNlAnalyzer import UiNlAnalyzer


__SCRIPT_DIR__ = os.path.dirname(os.path.realpath(__file__))


class UiDB:

    def __init__(self):
        self.__db = DbDataBase()
        self.__window = MainWindow(self.__db)
        # self.__uiViews: [str, UiView] = {}
        self.__uiView: [None, UiView] = None
        self.__connSignal()

    def __connSignal(self):
        self.__window.sigOpenDb.connect(self.loadDb)

    @property
    def chip(self) -> DbChip:
        return self.__db.chip

    @property
    def cells(self) -> Dict[str, DbMacro]:
        return self.__db.cells

    @property
    def layers(self) -> Dict[str, TechLayer]:
        return self.__db.layers

    @property
    def selected(self) -> List:
        return self.__db.selected_obj

    def addInst(self, inst_name: str, cell_name: str, base_module=None, pt_x=None, pt_y=None, orient=None):
        for inst in self.__db.addInst(inst_name, cell_name, base_module, pt_x, pt_y, orient):
            self.__window.insts[inst.name] = InstItem(inst)

    def addNet(self, net_name: str, base_module=None):
        for net in self.__db.addNet(net_name, base_module):
            self.__window.net_wire_dict[net.name] = []

    def attachToTerm(self, inst_name: str, term_name: str, net_name: str, base_module=None):
        self.__db.attachToTerm(inst_name, term_name, net_name, base_module)

    def attachModulePort(self, inst_name: str, term_name: str, port_name: str, base_module: str):
        self.__db.attachModulePort(inst_name, term_name, port_name, base_module)

    def addRoute(self, net_name: str, layer_name: str, from_pt: Tuple[float, float], to_pt: Tuple[float, float], width: float, begin_ext: float=0.0, end_ext: float=0.0, base_module=None):
        for wire in self.__db.addRoute(net_name, layer_name, from_pt, to_pt, width, begin_ext, end_ext, base_module):
            if wire.net.name not in self.__window.net_wire_dict:
                self.__window.net_wire_dict[wire.net.name] = []
            self.__window.net_wire_dict[wire.net.name].append(WireItem(wire))

    def checkNetLists(self, nl_dict: Dict[str, str]) -> UiNlAnalyzer:
        return UiNlAnalyzer(self.__db, nl_dict)

    '''--------------------------- basic operation head ---------------------------'''
    def saveDb(self, out_path: str, no_pin_loc=False, no_nl_conn=False):
        os.system(f'mkdir -p {out_path}')
        self.__db.saveDataBase(out_path, no_pin_loc=no_pin_loc, no_nl_conn=no_nl_conn)

    def loadDb(self, db_path: str):
        self.__db.loadDataBase(db_path)
        # if self.__db.loadDataBase(db_path):
        #     self.addView('base')

    def setLefList(self, lef_list: List[str]):
        self.__db.LEF_LIST = lef_list

    def setLibList(self, lib_list: List[str]):
        self.__db.LIB_LIST = lib_list

    def setVerilogList(self, verilog_list: List[str]):
        self.__db.VERILOG_LIST = verilog_list

    def setTopName(self, top_name: str):
        self.__db.TOP_NAME = top_name

    def setTechLef(self, tlef: str):
        self.__db.TECH_LEF = tlef

    def initDataBase(self):
        self.__db.initDataBase()

    def definePartitionByDef(self, def_list: List[str], include_pins=False):
        self.__db.definePartitionByDef(def_list, include_pins=include_pins)
        self.__window.addView()
        self.__uiView = UiView(self.__db, self.__window.workspace)
        # self.addView('base')
    '''--------------------------- basic operation tail ---------------------------'''

    '''--------------------------- gui operation head ---------------------------'''
    def win(self):
        self.__window.show()
        self.__window.raise_()

    def winoff(self):
        self.__window.hide()

    # def addView(self, view_name: str):
    #     self.__uiViews[view_name] = UiView(self.__db, self.__window.addView(view_name))

    # @property
    # def views(self) -> Dict[str, UiView]:
    #     return self.__uiViews

    @property
    def view(self) -> UiView:
        return self.__uiView
    '''--------------------------- gui operation tail ---------------------------'''

    '''--------------------------- io timing head ---------------------------'''
    def analyzeInterfaceInfo(self, block_info_yaml: str):
        self.__db.analyzeInterfaceInfo(block_info_yaml)

    def reportRegularInterfaceInfo(self, out_dir: str='regular_interface_info_rpts', target_clock_domains=[], target_module_pair=[]):
        self.__db.reportInterfaceInfo('regular', out_dir, target_clock_domains, target_module_pair)

    def reportFeedthroughInterfaceInfo(self, out_dir: str='ft_interface_info_rpts', target_clock_domains=[], target_module_pair=[]):
        self.__db.reportInterfaceInfo('ft', out_dir, target_clock_domains, target_module_pair)
    '''--------------------------- io timing tail ---------------------------'''

    '''--------------------------- geometry tail ---------------------------'''
    def dumpBlockGlobalLocalBoxMapping(self, block_name: str, out_file: str, mode='max', grid_size=10):
        out_result: List[Tuple[float, float, float, float, float, float, float, float]] = []
        hInsts = [ii for ii in self.__db.chip.hInst.treeHInsts.values() if ii.cell == block_name]
        if block_name == self.__db.TOP_NAME:
            hInsts.append(self.__db.chip.hInst)

        if not hInsts:
            Print(f'Error, cannot find hInst with cell name {block_name}')
            return
        if mode == 'max':
            for hInst in hInsts:
                for rect in polygonPartitioning(_V=hInst.shape):
                    global_grids: List[Tuple[float, float, float, float]] = []
                    x0 = min(rect[0], rect[2])
                    y0 = min(rect[1], rect[3])
                    x1 = max(rect[0], rect[2])
                    y1 = max(rect[1], rect[3])
                    grid_x_0 = math.floor(x0 / grid_size)
                    grid_y_0 = math.floor(y0 / grid_size)
                    grid_x_1 = math.floor(x1 / grid_size)
                    grid_y_1 = math.floor(y1 / grid_size)
                    for xx in range(grid_x_0, grid_x_1):
                        for yy in range(grid_y_0, grid_y_1):
                            global_grids.append((xx * grid_size, yy * grid_size, xx * grid_size + grid_size, yy * grid_size + grid_size))
                    for grid in set(global_grids):
                        out_result.append(tuple(list(grid) + list(rectMapToPtnLocal(hInst, grid))))
        elif mode == 'min':
            for hInst in hInsts:
                shape = hInst.shape
                xmin = min(ii[0] for ii in shape)
                xmax = max(ii[0] for ii in shape)
                ymin = min(ii[1] for ii in shape)
                ymax = max(ii[1] for ii in shape)
                aspect_ratio = (ymax - ymin) / (xmax - xmin)
                if aspect_ratio >= 1:
                    mm = 'hrect'
                else:
                    mm = 'vrect'
                for rect in polygonPartitioning(_V=hInst.shape, mode=mm):
                    out_result.append(tuple(list(rect) + list(rectMapToPtnLocal(hInst, rect))))
        else:
            Print(f'Error, invalid mode {mode}. Choose one of {{ max min }}')

        with open(out_file, 'w') as fh:
            for ii in out_result:
                fh.write(' '.join([str(_i) for _i in ii]) + '\n')

    def dumpGridOffsetFile(self, block_name: str, out_file: str):
        result = []
        with open(out_file, 'w') as fh:
            fh.write(f'# ptn_orient origin_x origin_y\n')
            for hInst in [hInst for hInst in self.__db.allHInsts() if hInst.cell == block_name]:
                if not hInst.is_ptn:
                    continue
                fh.write(f'{hInst.ptn_orient} {hInst.origin[0]} {hInst.origin[1]}\n')
                result.append([hInst.ptn_orient, hInst.origin[0], hInst.origin[1]])
        return result

    def genGridMapArray(self, out_file: str, mode: str, grid_size: int, spec_dict: Dict[str, Dict[str, str]]):
        legal_modes = ['cell_density', 'pin_density', 'setup_slack', 'hold_slack', 'discrete', 'discrete_max', 'discrete_mean', 'density_continuous', 'value_continuous']
        '''
        spec_dict:
            block_name_0: {{'def_file': def_file0, 'mapping_file': mapping_file0}},
            block_name_1: {{'def_file': def_file1, 'mapping_file': mapping_file1}},
            block_name_2: {{'def_file': def_file2, 'mapping_file': mapping_file2}},
                    ... ...
        '''

        if mode not in legal_modes:
            Print(f'Illegal mode "{mode}", please select on in {legal_modes}', level='error')
            return

        workdir = f'genGridArray'
        cwd = os.getcwd()
        os.system(f'mkdir -p {workdir}')
        os.chdir(workdir)
        os.system(f'mkdir -p logs')
        Print(f'Create workdir {workdir} and change current directory to it')

        ptn_info_suffix = '.ptn_info'
        statGrid_dir = f'StatGrid_{out_file.replace(".npy", "")}'

        genStatGrid_script = __SCRIPT_DIR__ + '/../bin/genStatGrid.py'
        mergeGridMap_script = __SCRIPT_DIR__ + '/../bin/mergeGridMap_script'

        cell_info_db = 'cell_info.db'
        if not os.path.isfile(cell_info_db):
            Print(f'Dump cell info db')
            with open(cell_info_db, 'wb') as fh:
                pickle.dump(self.__db.lefParser, fh)

        spec = f'{out_file.replace(".npy", "")}.spec'

        Print(f'Start to generate grid map numpy array, mode {mode}, grid size {grid_size}')
        expected_done_files = []
        with open(spec, 'w') as fh:
            for block_name, info in spec_dict.items():
                hInsts = [ii for ii in list(self.chip.hInst.treeHInsts.values()) + [self.chip.hInst] if ii.cell == block_name]
                if not hInsts:
                    Print(f'Cannot find any partition matched block name {block_name}', level='warning')
                def_file = os.path.abspath(info['def_file'])
                mapping_file = info['mapping_file']
                ptn_info_file = f'{block_name}{ptn_info_suffix}'
                for idx, _ in enumerate(self.dumpGridOffsetFile(block_name, ptn_info_file)):
                    expected_done_files.append(f'{statGrid_dir}/{block_name}_{idx}.done')
                if mapping_file:
                    fh.write(f'{block_name} {def_file} {ptn_info_file} {mapping_file}\n')
                else:
                    fh.write(f'{block_name} {def_file} {ptn_info_file}\n')
        expected_done_files = set(expected_done_files)
        startGrid_cmd = f'{sys.executable} {genStatGrid_script} -m {mode} -s {spec} -l {cell_info_db} -g {grid_size} -o {statGrid_dir}'
        cmd = f'cd {os.path.abspath(os.getcwd())} ; {startGrid_cmd}'
        print(cmd)
        os.system(cmd)
        waiting_period = 30
        timeout = 3600
        t0 = time.time()
        current_done_file = set()
        current_failed_file = set()
        remained_ptns = []
        while True:
            if time.time() - t0 > timeout:
                Print(f'GenGridStats timeout!!!', level='error')
                break
            current_done_file = set(glob(f'{statGrid_dir}/*.done'))
            current_failed_file = set(glob(f'{statGrid_dir}/*.fail'))
            Print(f'Total {len(expected_done_files)} stat grid files, {len(current_done_file)} are done, {len(current_failed_file)} are failed')

            all_ptns = [os.path.basename(ii).split(".")[0] for ii in expected_done_files]
            done_ptns = [os.path.basename(ii).split(".")[0] for ii in current_done_file]
            fail_ptns = [os.path.basename(ii).split(".")[0] for ii in current_failed_file]
            remained_ptns = [ii for ii in all_ptns if ii not in done_ptns and ii not in fail_ptns]
            if len(expected_done_files) - len(current_done_file) - len(current_done_file) < 5:
                Print(f'{remained_ptns} remained')

            if len(current_done_file) + len(current_failed_file) == len(expected_done_files):
                break
            time.sleep(waiting_period)

        for ii in list(current_failed_file) + remained_ptns:
            block_name = os.path.basename(ii).split("_")[0]
            idx = os.path.basename(ii).split("_")[1].split(".")[0]
            Print(f'{block_name} statGrid is not generated successfully. Check related log file in {workdir}/logs/{block_name}_{idx}.{statGrid_dir}.log')

        statGrid_file = glob(f'{statGrid_dir}/*.txt')

        shape_x = math.ceil(max([ii[0] for ii in self.chip.hInst.shape]) / grid_size)
        shape_y = math.ceil(max([ii[1] for ii in self.chip.hInst.shape]) / grid_size)
        GRID = np.zeros((shape_y, shape_x))
        GRID[:, :] = np.nan
        for file in statGrid_file:
            Print(f'Merge {file}')
            for line in [ii.rstrip('\n').split() for ii in open(file).readlines()]:
                xx = int(line[0])
                yy = int(line[1])
                if xx <shape_x and yy < shape_y:
                    value = float(line[2])
                    if np.isnan(GRID[yy, xx]):
                        GRID[yy, xx] = 0
                    GRID[yy, xx] += value
        np.save(out_file, GRID)
        Print(f'Save ndarray to {workdir}/{out_file.replace(".npy", "") + ".npy"}')
        os.chdir(cwd)































