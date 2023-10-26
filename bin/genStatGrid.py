from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

import pickle
import gzip
import argparse
import re
import os
import sys
import math
import copy
import traceback
import pathlib
from glob import glob
import yaml
import numpy as np
from shapely.geometry import Polygon
import time

SCRIPT_DIR = os.path.dirname(os.path.relpath(__file__))
sys.path.append(f'{SCRIPT_DIR}/..')

from LEF import LefParser
from DEF import DefParser
from utils import CoordinateProcess, readFile, Orient
from dataBase import DbMacro


class Inst:

    def __init__(self):
        self.name = ''
        self.cell_name = ''
        self.pt_x = 0.0
        self.pt_y = 0.0
        self.shape = []
        self.area = 0.0
        self.orient = 'N'
        self.pstatus = 'UNPLACED'
        self.hold_slack = 0.0
        self.setup_slack = 0.0
        self.power = 0.0
        self.custom_value = 0.0
        self.pin_locs: List[Tuple[float, float]] = []


class Block:

    def __init__(self, defParser: DefParser, lefParser: LefParser, ptn_orient: str, origin: Tuple[float, float]):
        self.block_name = ''
        self.shape = []
        self.defParser = defParser
        self.lefParser = lefParser
        self.ptn_orient = ptn_orient
        self.ptn_origin = origin
        self.insts: Dict[str, Inst] = {}
        self.readDef()

    def readDef(self):
        self.block_name = self.defParser.designName
        shape = [(i / self.defParser.dbUnit(), j / self.defParser.dbUnit()) for i, j in self.defParser.getDieArea()]
        if len(shape) == 2:
            x0 = shape[0][0]
            y0 = shape[0][1]
            x1 = shape[1][0]
            y1 = shape[1][1]
            shape = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
        for pt in shape:
            self.shape.append(CoordinateProcess.dbTransform(trans_type='to_global', pt=pt, orient_name=self.ptn_orient, origin=self.ptn_origin))
        for comp in self.defParser.getAllComponents():
            if comp.model_name not in self.lefParser.getMacros():
                print(f'Ignore {comp.comp_name}({comp.model_name}) which is not lib cell')
                continue
            if self.lefParser.getMacro(comp.model_name).macroClass() == 'COVER':
                continue
            inst_obj = Inst()
            inst_obj.name = comp.comp_name
            inst_obj.cell_name = comp.model_name
            inst_obj.pt_x = comp.pos_x / self.defParser.dbUnit()
            inst_obj.pt_y = comp.pos_y / self.defParser.dbUnit()
            inst_obj.orient = comp.orient
            inst_obj.pstatus = comp.pstatus
            inst_obj.area = self.lefParser.getMacro(comp.model_name).size()[0] * self.lefParser.getMacro(comp.model_name).size()[1]
            if inst_obj.area == 0:
                print(f'Warning, found cell {comp.model_name} with zero area')
            inst_obj.shape = self.calInstAbsShape(cell_name=inst_obj.cell_name, orient=inst_obj.orient, pt_x=inst_obj.pt_x, pt_y=inst_obj.pt_y)
            inst_obj.pin_locs = self.calInstPinLoc(cell_name=inst_obj.cell_name, orient=inst_obj.orient, pt_x=inst_obj.pt_x, pt_y=inst_obj.pt_y)
            self.insts[inst_obj.name] = inst_obj
        print(self.defParser)

    def calInstAbsShape(self, cell_name: str, orient: str, pt_x: float, pt_y: float) -> List[Tuple[float, float]]:
        macro = self.lefParser.getMacro(cell_name)
        height = macro.size()[1]
        width = macro.size()[0]
        origin = CoordinateProcess.calculateOriginByOrient(ll_pt=(pt_x, pt_y), orient_name=orient, height=height, width=width)
        origin = CoordinateProcess.dbTransform(trans_type='to_global', pt=origin, orient_name=self.ptn_orient, origin=self.ptn_origin)
        orient = Orient.mergeOrient(self.ptn_orient, orient)
        macro_shape = [(0, 0), (width, 0), (width, height), (0, height)]
        inst_shape = []
        for pt in macro_shape:
            inst_shape.append(CoordinateProcess.dbTransform(trans_type='to_global', pt=pt, orient_name=orient, origin=origin))
        return inst_shape

    def calInstPinLoc(self, cell_name: str, orient: str, pt_x: float, pt_y: float) -> List[Tuple[float, float]]:
        pin_locs = []
        macro = self.lefParser.getMacro(cell_name)
        height = macro.size()[1]
        width = macro.size()[0]
        origin = CoordinateProcess.calculateOriginByOrient(ll_pt=(pt_x, pt_y), orient_name=orient, height=height, width=width)
        origin = CoordinateProcess.dbTransform(trans_type='to_global', pt=origin, orient_name=self.ptn_orient, origin=self.ptn_origin)
        for pin in macro.pins():
            if pin.use != 'POWER' and pin.use != 'GROUND':
                pt = (pin.shape[0][0] + pin.shape[1][0]) / 2, (pin.shape[0][1] + pin.shape[1][1]) / 2
                pin_locs.append(CoordinateProcess.dbTransform(trans_type='to_global', pt=pt, orient_name=orient, origin=origin))
        return pin_locs


class GenStatGrid:

    LOG_DIR = 'logs'

    def __init__(self, lef_db_file: str, def_file: str, out_dir: str, value_mapping_file=''):
        os.system(f'mkdir -p {self.LOG_DIR}')
        os.system(f'mkdir -p {out_dir}')

        self.lefParser: LefParser = pickle.load(open(lef_db_file, 'rb'))
        DefParser.IGNORE_COVER = True
        DefParser.IGNORE_FILLER = True
        self.defParser = DefParser(def_file)

        self.value_mapping = {}

        if value_mapping_file:
            print(f'Detected value mapping file {value_mapping_file}')
            idx = 0
            for line in [ii.strip('\n').split() for ii in open(value_mapping_file).readlines()]:
                idx += 1
                try:
                    value = float(line[1])
                    self.value_mapping[line[0]] = value
                except ValueError:
                    print(f'Warning: In line {idx} ({line}), {line[1]} is not float')
        self.out_dir = out_dir

    def analyze(self, ptn_orient: str, origin_x: float, origin_y: float, grid_size: float, out_file: str, mode: str):
        print(f'Analyze Stat Grid with parameter \n ptn_orient {ptn_orient} \n origin_x {origin_x} \n origin_y {origin_y} \n grid_size {grid_size} \n out_file {out_file} \n mode {mode}')
        blockObj = Block(defParser=self.defParser, lefParser=self.lefParser, ptn_orient=ptn_orient, origin=(origin_x, origin_y))
        print(f'\nInitialize power density base grid with grid size {grid_size}')

        ll_x = min([ii[0] for ii in blockObj.shape])
        ll_y = min([ii[1] for ii in blockObj.shape])
        grid_x0 = math.floor(ll_x / grid_size)
        grid_y0 = math.floor(ll_y / grid_size)

        ur_x = max([ii[0] for ii in blockObj.shape])
        ur_y = max([ii[1] for ii in blockObj.shape])
        grid_x1 = math.floor(ur_x / grid_size)
        grid_y1 = math.floor(ur_y / grid_size)

        GRID: Dict[Tuple[int, int], float] = {}
        GRID_POLYGON: Dict[Tuple[int, int], Polygon] = {}
        block_polgon = Polygon(blockObj.shape)
        print(f'Set initial value from {grid_x0} to {grid_x1}, {grid_y0} to {grid_y1}')
        for ii in range(grid_x0, grid_x1 + 1):
            for jj in range(grid_y0, grid_y1 + 1):
                grid_polygon = Polygon(self.grid2Box(ii, jj, grid_size))
                if grid_polygon.intersection(block_polgon).area > 0:
                    GRID[(ii, jj)] = 0.0
                    GRID_POLYGON[(ii, jj)] = grid_polygon
        _CNT_GRID = copy.deepcopy(GRID)

        for inst_name, value in self.value_mapping.items():
            try:
                blockObj.insts[inst_name].custom_value = value
            except KeyError:
                print(f'Warning: Cannot find {inst_name} in def file, Please remove it from mapping file')

        inst_cnt = len(blockObj.insts)
        print(f'Fill grid with instance value, total {inst_cnt} instances.')
        step = int(inst_cnt / 10)
        cnt = 0
        for inst_name, instObj in blockObj.insts.items():
            cnt += 1
            if cnt % step == 0:
                print(f'{cnt} | {cnt//step}0% finished')

            inst_polygon = Polygon(instObj.shape)
            inst_area = inst_polygon.area
            bbox = inst_polygon.bounds

            if mode == 'cell_density':
                grid_x0 = math.floor(bbox[0] / grid_size)
                grid_y0 = math.floor(bbox[1] / grid_size)
                grid_x1 = math.ceil(bbox[2] / grid_size)
                grid_y1 = math.ceil(bbox[3] / grid_size)
                for ii in range(grid_x0, grid_x1):
                    for jj in range(grid_y0, grid_y1):
                        GRID[(ii, jj)] += GRID_POLYGON[(ii, jj)].intersection(inst_polygon).area
            elif mode == 'cell_density':
                grid_x0 = math.floor(bbox[0] / grid_size)
                grid_y0 = math.floor(bbox[1] / grid_size)
                grid_x1 = math.ceil(bbox[2] / grid_size)
                grid_y1 = math.ceil(bbox[3] / grid_size)
                for ii in range(grid_x0, grid_x1):
                    for jj in range(grid_y0, grid_y1):
                        GRID[(ii, jj)] += GRID_POLYGON[(ii, jj)].intersection(inst_polygon).area
            elif mode == 'pin_density':
                for loc in instObj.pin_locs:
                    grid_x0 = math.floor(loc[0] / grid_size)
                    grid_y0 = math.floor(loc[1] / grid_size)
                    GRID[(grid_x0, grid_y0)] += 1
            elif mode == 'setup_slack':
                GRID[(math.floor((bbox[0] + bbox[2])/(2 * grid_size)), math.floor((bbox[1] + bbox[3])/(2 * grid_size)))] += instObj.custom_value
            elif mode == 'hold_slack':
                GRID[(math.floor((bbox[0] + bbox[2])/(2 * grid_size)), math.floor((bbox[1] + bbox[3])/(2 * grid_size)))] += instObj.custom_value
            elif mode == 'discrete':
                GRID[(math.floor((bbox[0] + bbox[2])/(2 * grid_size)), math.floor((bbox[1] + bbox[3])/(2 * grid_size)))] += instObj.custom_value
            elif mode == 'discrete_max':
                v = GRID[(math.floor((bbox[0] + bbox[2]) / (2 * grid_size)), math.floor((bbox[1] + bbox[3]) / (2 * grid_size)))]
                GRID[(math.floor((bbox[0] + bbox[2]) / (2 * grid_size)), math.floor((bbox[1] + bbox[3]) / (2 * grid_size)))] = max(instObj.custom_value, v)
            elif mode == 'discrete_mean':
                v = GRID[(math.floor((bbox[0] + bbox[2])/(2 * grid_size)), math.floor((bbox[1] + bbox[3])/(2 * grid_size)))]
                cnt = _CNT_GRID[(math.floor((bbox[0] + bbox[2])/(2 * grid_size)), math.floor((bbox[1] + bbox[3])/(2 * grid_size)))]
                GRID[(math.floor((bbox[0] + bbox[2]) / (2 * grid_size)), math.floor((bbox[1] + bbox[3]) / (2 * grid_size)))] = (v * cnt + instObj.custom_value) / (cnt + 1)
                _CNT_GRID[(math.floor((bbox[0] + bbox[2]) / (2 * grid_size)), math.floor((bbox[1] + bbox[3]) / (2 * grid_size)))] += 1
            elif mode == 'density_continuous':
                grid_x0 = math.floor(bbox[0] / grid_size)
                grid_y0 = math.floor(bbox[1] / grid_size)
                grid_x1 = math.ceil(bbox[2] / grid_size)
                grid_y1 = math.ceil(bbox[3] / grid_size)
                for ii in range(grid_x0, grid_x1):
                    for jj in range(grid_y0, grid_y1):
                        GRID[(ii, jj)] += GRID_POLYGON[(ii, jj)].intersection(inst_polygon).area * instObj.custom_value
            elif mode == 'value_continuous':
                grid_x0 = math.floor(bbox[0] / grid_size)
                grid_y0 = math.floor(bbox[1] / grid_size)
                grid_x1 = math.ceil(bbox[2] / grid_size)
                grid_y1 = math.ceil(bbox[3] / grid_size)
                for ii in range(grid_x0, grid_x1):
                    for jj in range(grid_y0, grid_y1):
                        GRID[(ii, jj)] += GRID_POLYGON[(ii, jj)].intersection(inst_polygon).area * instObj.custom_value / instObj.area
            else:
                print(f'Error, invalid mode {mode}')
                raise ValueError

        print(f'Grid Summary')
        print(f'  Grid_cnt {len(GRID)}')
        print(f'  Max {max(GRID.values())}')
        print(f'  Mean {sum(GRID.values()) / len(GRID)}')
        print(f'  Min {min(GRID.values())}')

        print(f'Write box file by base grid to {out_file}')
        with open(out_file, 'w') as fh:
            for coord, value in GRID.items():
                fh.write(f'{coord[0]} {coord[1]} {value}\n')

    @staticmethod
    def grid2Box(ii: int, jj: int, grid_size: float):
        return [(ii * grid_size, jj * grid_size),
                (ii * grid_size + grid_size, jj * grid_size),
                (ii * grid_size + grid_size, jj * grid_size + grid_size),
                (ii * grid_size, jj * grid_size + grid_size)]

if __name__ == '__main__':
    lsf_cmd = 'bsub -q me_pd -n1 -R "rusage[mem=20GB]"'
    legal_modes = ['cell_density', 'pin_density', 'setup_slack', 'hold_slack', 'discrete', 'discrete_max', 'discrete_min', 'discrete_mean', 'density_continuous', 'value_continuous']

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--run', action='store_true', help=argparse.SUPPRESS)
    argparser.add_argument('--target_block', type=str, default='', help=argparse.SUPPRESS)
    argparser.add_argument('--ptn_orient', type=str, default='N', help=argparse.SUPPRESS)
    argparser.add_argument('--origin_x', type=float, default=0.0, help=argparse.SUPPRESS)
    argparser.add_argument('--origin_y', type=float, default=0.0, help=argparse.SUPPRESS)
    argparser.add_argument('--idx', type=int, default=0, help=argparse.SUPPRESS)

    argparser.add_argument('-m', '--mode', required=True, choices=legal_modes, type=str)
    argparser.add_argument('-s', '--spec_file', required=True, type=str, help='block_name def_file grid_offset <mapping_file>')
    argparser.add_argument('-l', '--lef_db_file', required=True, type=str)
    argparser.add_argument('-o', '--out_dir', default='', type=str)
    argparser.add_argument('-g', '--grid_size', default=10, type=int, help='default = 10')

    args = argparser.parse_args()

    if args.out_dir == '':
        out_dir = f'StatGrid_{args.mode}'
    else:
        out_dir = args.out_dir

    os.system(f'mkdir -p {out_dir}')
    os.system(f'rm -f {out_dir}/*done {out_dir}/*fail')

    for line in open(args.spec_file, 'r').readlines():
        line_content = line.rstrip('\n').split()
        block_name = line_content[0]
        def_file = line_content[1]
        ptn_info_file = line_content[2]

        if args.run and block_name == args.target_block:
            done_file = f'{out_dir}/{block_name}_{args.idx}.done'
            fail_file = f'{out_dir}/{block_name}_{args.idx}.fail'
            try:
                ptn_orient = args.ptn_orient
                origin_x = args.origin_x
                origin_y = args.origin_y
                if len(line_content) >= 4:
                    mapping_file = line_content[3]
                    checker = GenStatGrid(args.lef_db_file, def_file, out_dir, mapping_file)
                else:
                    checker = GenStatGrid(args.lef_db_file, def_file, out_dir)
                checker.analyze(ptn_orient=args.ptn_orient, origin_x=args.origin_x, origin_y=args.origin_y, grid_size=args.grid_size, out_file=f'{out_dir}/{block_name}_{args.idx}.txt', mode=args.mode)
                time.sleep(30)
                with open(done_file, 'w') as fh:
                    pass
                print(f'touch {done_file}')
            except:
                print(traceback.format_exc())
                print(f'Something wrong, failed to generate correct stat grid')
                time.sleep(30)
                with open(fail_file, 'w') as fh:
                    pass
                print(f'touch {fail_file}')
        elif not args.run:
            for idx, grid_offset_line in enumerate([ii.rstrip('\n').split() for ii in open(ptn_info_file).readlines() if '#' not in ii]):
                ptn_orient = grid_offset_line[0]
                origin_x = float(grid_offset_line[1])
                origin_y = float(grid_offset_line[2])
                if args.out_dir == '':
                    log_name = f'{GenStatGrid.LOG_DIR}/{block_name}_{idx}.{args.mode}.log'
                else:
                    log_name = f'{GenStatGrid.LOG_DIR}/{block_name}_{idx}.{args.out_dir}.log'
                if args.out_dir:
                    final_shell_cmd = f'/bin/bash -c \' {lsf_cmd} "{sys.executable} {__file__} --idx {idx} --target_block {block_name} --run --ptn_orient {ptn_orient} --origin_x {origin_x} --origin_y {origin_y} -g {args.grid_size} -l {args.lef_db_file} -m {args.mode} -s {args.spec_file} -o {args.out_dir} &> {log_name}" \''
                else:
                    final_shell_cmd = f'/bin/bash -c \' {lsf_cmd} "{sys.executable} {__file__} --idx {idx} --target_block {block_name} --run --ptn_orient {ptn_orient} --origin_x {origin_x} --origin_y {origin_y} -g {args.grid_size} -l {args.lef_db_file} -m {args.mode} -s {args.spec_file} &> {log_name}" \''

                print(final_shell_cmd)
                os.system(final_shell_cmd)












