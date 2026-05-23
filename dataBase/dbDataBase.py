from __future__ import annotations
from typing import List, Tuple, Dict, Union, Iterable, TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    from verilog import Module
    from gui import MainWindow

import os
import sys
import time
import pickle
import copy
import numpy as np
import yaml
from shapely.geometry import Polygon
from .dbChip import DbChip
from .dbMacro import DbMacro
from .techLayer import TechLayer
from .dbHInst import DbHInst
from .dbInst import DbInst
from .dbNet import DbNet
from .dbHNet import DbHNet
from .dbWire import DbWire
from .dbAttribute import DbAttribute
from LEF import LefParser, TlefParser
from DEF import DefParser
from timingLib import LibertyParser
from verilog import VerilogParser
from ioTiming import IOChecker
from utils import CoordinateProcess, readFile, Orient, PSTATUS, Print


class DbDataBase:
    TECH_LEF = None
    LEF_LIST: List[str] = []
    LIB_LIST: List[str] = []
    VERILOG_LIST: List[str] = []
    TOP_NAME = None
    IGNORE_LOGICAL_CONNECTION = False

    def __init__(self):
        self.chip: Union[DbChip, None] = None
        self.cells: Dict[str, DbMacro] = {}
        self.modules: Dict[str, Module] = {}
        self.layers: Dict[str, TechLayer] = {}
        self.is_initialized = False
        self.selected_obj = []
        self.techLayerParser = None
        self.lefParser = None
        self.libParser = None
        self.module_def_dict: Dict[str, DefParser] = {}
        self.module_attribute: Dict[str, List[DbAttribute]] = {}

        self.gui_window: [None, MainWindow] = None

        self.ft_db = None

        self.io_checker: Union[IOChecker, None] = None

        self.__CONFIG_FILE = 'config.db'
        self.__VERILOG_FILE = 'verilog.db'
        self.__LEF_FILE = 'cell_info.db'
        self.__LIB_FILE = 'lib_info.db'
        self.__DEF_FILE = 'floorplan.db'
        self.__TECH_FILE = 'tech.db'
        self.__FT_FILE = 'ft.db'

    def _rebuildLayersFromParser(self):
        if self.techLayerParser is not None:
            idx = 1
            for layer in self.techLayerParser.layers.values():
                if layer.type == 'ROUTING' and layer.region is None:
                    _idx = idx
                    idx += 1
                else:
                    _idx = 0
                self.createLayer(name=layer.name,
                                 layer_type=layer.type,
                                 direction=layer.direction,
                                 pitch_x=layer.pitch_x,
                                 pitch_y=layer.pitch_y,
                                 width=layer.width,
                                 spacing=layer.spacing,
                                 area=layer.area,
                                 region=layer.region,
                                 based_layer=layer.based_layer,
                                 idx=_idx)

    def _rebuildCellsFromParsers(self):
        if self.lefParser is not None:
            if self.libParser:
                lib_macro_dict = self.libParser.getMacros()
            else:
                lib_macro_dict = {}
            for macro in self.lefParser.getMacros().values():
                params = {
                    'macro_name': macro.macroName(),
                    'classType': macro.macroClass(),
                    'width': macro.size()[0],
                    'height': macro.size()[1],
                    'pins': macro.pins(),
                    'footprint': '',
                    'leakage': 0.0
                }
                if macro.macroName() in lib_macro_dict:
                    params['footprint'] = lib_macro_dict[macro.macroName()].footprint
                    params['leakage'] = lib_macro_dict[macro.macroName()].leakage
                self.cells[macro.macroName()] = DbMacro(**params)

    def initDataBase(self):
        self.chip = DbChip(top_name=self.TOP_NAME)
        self.__initTechLef()
        self.__initMacro()
        self.__initNetList()
        self.__initModuleAttribute()
        # self.__initFtDb()

    def allHInsts(self) -> List[DbHInst]:
        return [self.chip.hInst] + list(self.chip.hInst.treeHInsts.values())

    def setModuleAttribute(self, module: str, group_name: str, attr_name: str, value, mode: str):
        attr = DbAttribute(group_name=group_name, attr_name=attr_name, value=value, mode=mode)
        self.module_attribute[module].append(attr)

    # def __initFtDb(self):
    #     if self.ft_db is None:
    #         self.ft_db = FtDbAlpha()

    def __initModuleAttribute(self):
        if not self.module_attribute:
            for cell in set([hInst.cell for hInst in self.allHInsts()]):
                self.module_attribute[cell] = []

    def __initTechLef(self):
        if self.techLayerParser is None and self.TECH_LEF is not None:
            self.techLayerParser = TlefParser(self.TECH_LEF)
            idx = 1
            for layer in self.techLayerParser.layers.values():
                if layer.type == 'ROUTING' and layer.region is None:
                    _idx = idx
                    idx += 1
                else:
                    _idx = 0
                self.createLayer(name=layer.name,
                                 layer_type=layer.type,
                                 direction=layer.direction,
                                 pitch_x=layer.pitch_x,
                                 pitch_y=layer.pitch_y,
                                 width=layer.width,
                                 spacing=layer.spacing,
                                 area=layer.area,
                                 region=layer.region,
                                 based_layer=layer.based_layer,
                                 idx=_idx)

    def createLayer(self, name: str, layer_type='custom', direction='', pitch_x=0.0, pitch_y=0.0, width=0.0, spacing=0.0, area=0.0, region=None, based_layer=None, idx=0):
        self.layers[name] = TechLayer(name=name, layer_type=layer_type, direction=direction, pitch_x=pitch_x, pitch_y=pitch_y, width=width, spacing=spacing, area=area, region=region, based_layer=based_layer, idx=idx)

    def __initMacro(self):
        if self.lefParser is None and self.LEF_LIST:
            self.lefParser = LefParser(lef_list=self.LEF_LIST)
        if self.libParser is None and self.LIB_LIST:
            self.libParser = LibertyParser(lib_files=self.LIB_LIST)
        if self.libParser:
            lib_macro_dict = self.libParser.getMacros()
        else:
            lib_macro_dict = {}
        for macro in self.lefParser.getMacros().values():
            params = {
                'macro_name': macro.macroName(),
                'classType': macro.macroClass(),
                'width': macro.size()[0],
                'height': macro.size()[1],
                'pins': macro.pins(),
                'footprint': '',
                'leakage': 0.0
            }
            if macro.macroName() in lib_macro_dict:
                params['footprint'] = lib_macro_dict[macro.macroName()].footprint
                params['leakage'] = lib_macro_dict[macro.macroName()].leakage
            self.cells[macro.macroName()] = DbMacro(**params)

    def __initNetList(self):
        if self.modules == {}:
            for verilogParser in map(VerilogParser, self.VERILOG_LIST):
                for module_name, module in verilogParser.allModules().items():
                    # remove leaf cell
                    for inst in module.allInsts.values():
                        if inst.name in self.cells:
                            module.deleteInst(inst.name)
                    self.modules[module_name] = module
        if self.modules == {}:
            Print(f'Netlist is not initialized in database')
            return
        for _, term in self.modules[self.TOP_NAME].allPorts.items():
            for ii in term.granulate():
                hInstTerm = self.chip.hInst.addHInstTerm(ii, term.direction)
                self.chip.hInst.addHNet(ii)._DbHNet__attachToHTerm(hInstTerm.hTerm)

        Print(f'Constructing netlist hierarchy')
        t0 = time.time()
        self.__constructHierarchy(self.chip.hInst)
        self.__setInitNets(self.chip.hInst)
        self.is_initialized = True
        Print(f'End netlist hierarchy construction in {round(time.time() - t0, 3)}s')

    def __constructHierarchy(self, current_hInst: DbHInst, level=0):
        Print('--' * level + current_hInst.cell + '|' + current_hInst.name)
        # print(current_hInst.hNets)
        current_module = self.modules[current_hInst.cell]
        for _, net in current_module.allNets.items():
            for ii in net.granulate():
                current_hInst.addHNet(ii)
        if current_hInst.name:
            current_hierarchy = current_hInst.name + '/'
        else:
            current_hierarchy = current_hInst.name
        for inst_name, inst in current_module.allInsts.items():
            if inst.cell_name in self.modules:
                child_module = self.modules[inst.cell_name]
                child_hInst = DbHInst(name=current_hierarchy + inst_name, cell=inst.cell_name, pHInst=current_hInst)
                current_hInst.addHInst(child_hInst)
                local_hierarchy = current_hierarchy + inst_name

                if self.IGNORE_LOGICAL_CONNECTION is False:
                    for term_name, term in child_module.allPorts.items():
                        for ii in term.granulate():
                            hInstTerm = child_hInst.addHInstTerm(ii, term.direction)
                            child_hInst.addHNet(ii)._DbHNet__attachToHTerm(hInstTerm.hTerm)
                    for _, term in inst.allTerms.items():
                        #print(term.name)
                        for term_name, net_name in term.granulate(pModule=current_module, cModule=child_module):
                            #print(child_hInst.name, net_name, term_name)
                            if type(net_name) == str:
                                current_hInst.hNets[current_hierarchy + net_name]._DbHNet__attachToHInstTerm(child_hInst.hInstTerms[local_hierarchy + '/' + term_name])
                            elif net_name == 0:
                                child_hInst.hInstTerms[local_hierarchy + '/' + term_name]._DbHInstTerm__setTieLo()
                            elif net_name == 1:
                                child_hInst.hInstTerms[local_hierarchy + '/' + term_name]._DbHInstTerm__setTieHi()

                self.__constructHierarchy(child_hInst, level + 1)
        if self.IGNORE_LOGICAL_CONNECTION is False:
            for lvalue, rvalue in current_module.assigns.items():
                l_hNet = current_hInst.hNets[current_hierarchy + lvalue]
                r_hNet = current_hInst.hNets[current_hierarchy + rvalue]
                for hInstTerm in r_hNet.hInstTerms.values():
                    l_hNet._DbHNet__attachToHInstTerm(hInstTerm)

    def __setNetToHNet(self, current_hNet: DbHNet, net=None):
        if net is None:
            net = DbNet(current_hNet.name)
        current_hNet._DbHNet__setNet(net)
        self.chip._DbChip__nets[net.name] = net
        for hInstTerm in current_hNet.hInstTerms.values():
            self.__setNetToHNet(hInstTerm.downHNet, net)

    def __setInitNets(self, current_hInst: DbHInst):
        #Print(f'Set initial net for {current_hInst.cell} | {current_hInst.name}')
        for hNet in current_hInst.hNets.values():
            if hNet.net is None:
                self.__setNetToHNet(hNet)
        for child_hInst in current_hInst.hInsts.values():
            self.__setInitNets(child_hInst)

    def definePartitionByDef(self, def_file_list: List[str], include_pins=False):
        if self.is_initialized is False:
            Print(f'Error, design is not initialized.')
            sys.exit(-1)

        if self.module_def_dict == {}:
            module_dict = {self.TOP_NAME: {'is_leaf': False, 'hInst': ['']}}
            for hInst_name, hInst in self.chip.hInst.treeHInsts.items():
                if hInst.cell not in module_dict:
                    module_dict[hInst.cell] = {'is_leaf': False, 'hInsts': []}
                module_dict[hInst.cell]['hInsts'].append(hInst_name)
                if not hInst.hInsts:
                    module_dict[hInst.cell]['is_leaf'] = True

        for def_file in def_file_list:
            defParser = DefParser(def_file=def_file, skip_comp=True, parse_pin=include_pins)
            design_name = defParser.designName
            if design_name in module_dict:
                if module_dict[design_name]['is_leaf'] is False:
                    defParser = DefParser(def_file=def_file, parse_pin=include_pins)
                self.module_def_dict[design_name] = defParser

        if self.module_def_dict:
            self.__derivePtnPhysicalInfo(module_def_dict=self.module_def_dict, p_block=self.TOP_NAME)

        module_pin_loc_dict = {}
        for module, def_parser in self.module_def_dict.items():
            loc_xs = np.array([pin.pos_x for pin in def_parser.getAllPins()]) / def_parser.dbUnit()
            loc_ys = np.array([pin.pos_y for pin in def_parser.getAllPins()]) / def_parser.dbUnit()
            module_pin_loc_dict[module] = {'pos': (loc_xs, loc_ys), 'pin_names': [pin.pin_name for pin in def_parser.getAllPins()]}

        for hInst in self.allHInsts():
            if hInst.is_ptn:
                module = hInst.cell
                orient = hInst.ptn_orient
                origin = hInst.origin
                pin_names = [f'{hInst.name}/{name}'.rstrip('/') for name in module_pin_loc_dict[module]['pin_names']]
                xs, ys = CoordinateProcess.dbTransformBatch(trans_type='to_global', pt=module_pin_loc_dict[module]['pos'], orient_name=orient, origin=origin)
                for pin_name, x, y in zip(pin_names, xs, ys):
                    hInst.hInstTerms[pin_name].setPt(x, y)

    def __derivePtnPhysicalInfo(self, module_def_dict: Dict[str, DefParser], p_block: str, p_origin=(0, 0), p_orient='N', current_hierarchy=''):
        p_db_unit = module_def_dict[p_block].dbUnit()

        if current_hierarchy == '':
            shape = []
            for ii in module_def_dict[self.chip.hInst.cell].shape():
                shape.append((round(ii[0] / p_db_unit, 3), round(ii[1] / p_db_unit, 3)))

            self.chip.hInst.definePartition(
                shape=shape,
                pt_x=0.0,
                pt_y=0.0,
                origin_x=0.0,
                origin_y=0.0,
                orient=p_orient,
                area=round(Polygon(shape).area, 6)
            )

        for comp in module_def_dict[p_block].getAllComponents():
            if comp.model_name not in module_def_dict:
                continue
            defParser = module_def_dict[comp.model_name]
            c_db_unit = defParser.dbUnit()
            hInst_name = current_hierarchy + '/' + comp.comp_name if current_hierarchy else comp.comp_name

            scale = p_db_unit / c_db_unit
            scaled_p_origin = (p_origin[0] * scale, p_origin[1] * scale)

            origin = CoordinateProcess.calculateOriginByOrient(
                ll_pt=(comp.pos_x * scale, comp.pos_y * scale),
                orient_name=comp.orient,
                height=defParser.getHeight(),
                width=defParser.getWidth()
            )
            origin = CoordinateProcess.dbTransform(trans_type='to_global', pt=origin, orient_name=p_orient, origin=scaled_p_origin)
            orient = Orient.mergeOrient(p_orient, comp.orient)

            shape = []
            for ii in defParser.shape():
                new_ii = CoordinateProcess.dbTransform(trans_type='to_global', pt=ii, orient_name=orient, origin=origin)
                shape.append((round(new_ii[0] / c_db_unit, 3), round(new_ii[1] / c_db_unit, 3)))
            pt = (min(ii[0] for ii in shape), min(ii[1] for ii in shape))

            self.chip.hInst.treeHInsts[hInst_name].definePartition(
                shape=shape,
                pt_x=round(pt[0], 3),
                pt_y=round(pt[1], 3),
                origin_x=round(origin[0] / c_db_unit, 3),
                origin_y=round(origin[1] / c_db_unit, 3),
                orient=orient,
                area=round(Polygon(shape).area, 4)
            )
            self.__derivePtnPhysicalInfo(module_def_dict=module_def_dict, p_block=comp.model_name, p_origin=origin, p_orient=orient, current_hierarchy=hInst_name)

    def appendSelected(self, obj):
        self.selected_obj.append(obj)

    def removeSelected(self, obj):
        self.selected_obj.remove(obj)

    def clearSelected(self):
        self.selected_obj = []

    def saveDataBase(self, out_path: str, no_pin_loc=False, no_nl_conn=False):
        Print(f'Saving database to {out_path}')
        Print(f'  Save config file')
        config_file = f'{out_path}/{self.__CONFIG_FILE}'
        config = {
            'LEF_LIST': self.LEF_LIST,
            'LIB_LIST': self.LIB_LIST,
            'VERILOG_LIST': self.VERILOG_LIST,
            'TOP_NAME': self.TOP_NAME,
            'TECH_FILE': self.TECH_LEF
        }
        with open(config_file, 'wb') as fh:
            pickle.dump(config, fh)
        #verilog
        Print(f'  Save netlist')
        verilog_file = f'{out_path}/{self.__VERILOG_FILE}'
        if no_nl_conn is True:
            modules = copy.deepcopy(self.modules)
            for ii in modules.values():
                ii._Module__nets.clear()
                ii._Module__ports.clear()
                ii._Module__assigns.clear()
                for inst in ii.allInsts.values():
                    inst._ModuleInst__term.clear()
            with open(verilog_file, 'wb') as fh:
                pickle.dump(modules, fh)
        else:
            with open(verilog_file, 'wb') as fh:
                pickle.dump(self.modules, fh)
        #tlef
        Print(f'    Save tech info')
        tlef = f'{out_path}/{self.__TECH_FILE}'
        with open(tlef, 'wb') as fh:
            pickle.dump(self.techLayerParser, fh)
        #LEF
        Print(f'    Save cell info')
        lef_file = f'{out_path}/{self.__LEF_FILE}'
        with open(lef_file, 'wb') as fh:
            pickle.dump(self.lefParser, fh)
        #LIB
        Print(f'    Save lib info')
        lib_file = f'{out_path}/{self.__LIB_FILE}'
        with open(lib_file, 'wb') as fh:
            pickle.dump(self.libParser, fh)
        #DEF
        Print(f'    Save floorplan info')
        fp_def_file = f'{out_path}/{self.__DEF_FILE}'
        if no_pin_loc is True:
            _module_def_dict = copy.deepcopy(self.module_def_dict)
            for ii in _module_def_dict.values():
                ii._DefParser__pins.clear()
            with open(fp_def_file, 'wb') as fh:
                pickle.dump(_module_def_dict, fh)
        else:
            with open(fp_def_file, 'wb') as fh:
                pickle.dump(self.module_def_dict, fh)
        # FT
        # Print(f'    Save FT')
        # ft_file = f'{out_path}/{self.__FT_FILE}'
        # with open(ft_file, 'wb') as fh:
        #     pickle.dump(self.ft_db, fh)
        Print(f'Finish saving database')

    def loadDataBase(self, db_path: str) -> bool:
        Print(f'Loading databse from {db_path}')

        Print(f'  Load {db_path}/{self.__CONFIG_FILE}')
        config = pickle.load(open(f'{db_path}/{self.__CONFIG_FILE}', 'rb'))
        self.LEF_LIST = config['LEF_LIST']
        self.LIB_LIST = config['LIB_LIST']
        self.VERILOG_LIST = config['VERILOG_LIST']
        self.TOP_NAME = config['TOP_NAME']
        self.TECH_LEF = config['TECH_FILE']

        Print(f'  Load {db_path}/{self.__TECH_FILE}')
        self.techLayerParser = pickle.load(open(f'{db_path}/{self.__TECH_FILE}', 'rb'))

        Print(f'  Load {db_path}/{self.__VERILOG_FILE}')
        self.modules = pickle.load(open(f'{db_path}/{self.__VERILOG_FILE}', 'rb'))

        Print(f'  Load {db_path}/{self.__LEF_FILE}')
        self.lefParser = pickle.load(open(f'{db_path}/{self.__LEF_FILE}', 'rb'))

        Print(f'  Load {db_path}/{self.__LIB_FILE}')
        self.libParser = pickle.load(open(f'{db_path}/{self.__LIB_FILE}', 'rb'))

        Print(f'  Load {db_path}/{self.__DEF_FILE}')
        self.module_def_dict = pickle.load(open(f'{db_path}/{self.__DEF_FILE}', 'rb'))

        ft = f'{db_path}/{self.__FT_FILE}'
        if os.path.isfile(ft):
            Print(f'  Load {ft}')
            self.ft_db = pickle.load(open(ft, 'rb'))

        # Rebuild layers and cells from the pickled parsers
        self.layers.clear()
        self.cells.clear()
        self._rebuildLayersFromParser()
        self._rebuildCellsFromParsers()

        self.initDataBase()
        self.definePartitionByDef([])

        if self.module_def_dict:
            return True
        else:
            return False

    def analyzeInterfaceInfo(self, block_info_yaml: str):
        block_info_dict = yaml.safe_load(open(block_info_yaml, 'r'))
        self.io_checker = IOChecker(self, block_io_csv_dict=block_info_dict)

    def reportInterfaceInfo(self, path_type: str, out_dir: str='interface_info_rpts', target_clock_domains: List[str]=[], target_module_pairs: List[Tuple[str, str]]=[]):
        if self.io_checker is None:
            Print(f'Report failed. IO check is not initialized.')
        else:
            if path_type == 'regular':
                self.io_checker.genRegularReport(out_dir, target_clock_domains, target_module_pairs)
            elif path_type == 'ft':
                self.io_checker.genFeedthroughReport(out_dir, target_clock_domains, target_module_pairs)

    def __getHInstByModule(self, module_name: str) -> List[DbHInst]:
        if module_name is None:
            target_hInsts = [self.chip.hInst]
        else:
            target_hInsts = [ii for ii in self.chip.hInst.treeHInsts.values() if ii.cell == module_name]
        if not target_hInsts:
            Print(f'Cannot find ant hInst match module name {module_name}', level='error')
        return target_hInsts

    def addInst(self, inst_name: str, cell_name: str, base_module=None, pt_x=None, pt_y=None, orient=None) -> List[DbInst]:
        out = []
        cell_height = self.cells[cell_name].height
        cell_width = self.cells[cell_name].width
        cell_shape = [(0, 0), (0, cell_height), (cell_width, cell_height), (cell_width, 0)]
        if orient in Orient.OA_DEF_map:
            orient = Orient.OA_DEF_map[orient]
        for hInst in self.__getHInstByModule(base_module):
            pHInst = hInst
            if hInst.name:
                abs_inst_name = hInst.name + '/' + inst_name
            else:
                abs_inst_name = inst_name

            if pt_x is not None and pt_y is not None and orient is not None:
                origin = CoordinateProcess.calculateOriginByOrient(ll_pt=(pt_x, pt_y), orient_name=orient, height=cell_height, width=cell_width)
                origin = CoordinateProcess.dbTransform(trans_type='to_global', pt=origin, orient_name=pHInst.ptn_orient, origin=pHInst.origin)
                _orient = Orient.mergeOrient(pHInst.ptn_orient, orient)
                inst_shape = [CoordinateProcess.dbTransform(trans_type='to_global', pt=ii, orient_name=_orient, origin=origin) for ii in cell_shape]
                _pt_x, _pt_y = min([ii[0] for ii in inst_shape]), min(ii[1] for ii in inst_shape)
                inst = DbInst(name=abs_inst_name, pHInst=pHInst, cell=self.cells[cell_name], pt_x=_pt_x, pt_y=_pt_y, orient=_orient, pstatus=PSTATUS.PLACED)
            else:
                inst = DbInst(name=abs_inst_name, pHInst=pHInst, cell=self.cells[cell_name])
            if inst.name in self.chip.insts:
                Print(f'Fail to add inst {inst.name} because it already exists.', level='error')
            else:
                self.chip._DbChip__insts[inst.name] = inst
                out.append(inst)
        return out

    def addNet(self, net_name: str, base_module=None) -> List[DbNet]:
        out = []
        for hInst in self.__getHInstByModule(base_module):
            net_hier = os.path.dirname(net_name)
            pHInst = hInst.treeHInsts[net_hier] if net_hier else hInst
            if hInst.name:
                abs_net_name = hInst.name + '/' +net_name
            else:
                abs_net_name = net_name
            net = DbNet(name=abs_net_name)
            hNet = DbHNet(abs_net_name, pHInst)
            if net.name in self.chip.nets:
                Print(f'Fail to add net {net.name} because it already exists.', level='error')
            else:
                hInst._DbHInst__hNets[abs_net_name] = hNet
                self.chip._DbChip__nets[abs_net_name] = net
                hNet._DbHNet__setNet(net)
                out.append(net)

        return out

    def attachToTerm(self, inst_name: str, term_name: str, net_name: str, base_module=None):
        for hInst in self.__getHInstByModule(base_module):
            if hInst.name:
                abs_net_name = hInst.name + '/' + net_name
                abs_inst_name = hInst.name + '/' + inst_name
            else:
                abs_net_name = net_name
                abs_inst_name = inst_name
            net = self.chip.nets[abs_net_name]
            inst_term = self.chip.insts[abs_inst_name].instTerms[abs_inst_name + '/' + term_name]
            net._DbNet__attachToInstTerm(inst_term)

    def attachModulePort(self, inst_name: str, term_name: str, port_name: str, base_module: str):
        for hInst in self.__getHInstByModule(base_module):
            if hInst.name:
                abs_port_name = hInst.name + '/' + port_name
                abs_inst_name = hInst.name + '/' + inst_name
            else:
                abs_port_name = port_name
                abs_inst_name = inst_name
            net = hInst.hInstTerms[abs_port_name].hTerm.downHNet.net
            inst_term = self.chip.insts[abs_inst_name].instTerms[abs_inst_name + '/' + term_name]
            net._DbNet__attachToInstTerm(inst_term)

    def addRoute(self, net_name: str, layer_name: str, from_pt: Tuple[float, float], to_pt: Tuple[float, float], width: float, begin_ext: float=0.0, end_ext: float=0.0, base_module=None) -> List[DbWire]:
        out = []
        for hInst in self.__genHInstByModule(base_module):
            if self.layers[layer_name].idx < 1:
                Print(f'Invalid layer name {layer_name}', level='error')
                break
            if hInst.name:
                abs_net_name = hInst.name + '/' + net_name
            else:
                abs_net_name = net_name

            _from_pt = CoordinateProcess.dbTransform(trans_type='to_global', pt=from_pt, orient_name=hInst.ptn_orient, origin=hInst.origin)
            _to_pt = CoordinateProcess.dbTransform(trans_type='to_global', pt=to_pt, orient_name=hInst.ptn_orient, origin=hInst.origin)
            wire = DbWire(net=hInst.hNets[abs_net_name].net, layer=self.layers[layer_name], from_pt=from_pt, to_pt=_to_pt, width=width, begin_ext=begin_ext, end_ext=end_ext)
            out.append(wire)
        return out
















