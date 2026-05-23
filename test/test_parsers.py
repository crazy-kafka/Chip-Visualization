"""
Unit tests for parsers: TlefParser, LefParser, DefParser, VerilogParser,
InstExtractor, SpefParser, LibertyParser.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LEF import TlefParser, LefParser
from DEF import DefParser
from verilog.verilogParser import VerilogParser
from verilog.instExtract import InstExtractor
from spef.spefParser import SpefParser
from timingLib.libertyParser import LibertyParser


# ======================== TlefParser ========================

class TestTlefParser:
    def test_parse_3_layers(self, tlef_parser):
        layers = tlef_parser.layers
        assert len(layers) == 3
        assert 'M1' in layers
        assert 'M2' in layers
        assert 'M3' in layers

    def test_M1_properties(self, tlef_parser):
        m1 = tlef_parser.layers['M1']
        assert m1.type == 'ROUTING'
        assert m1.direction == 'HORIZONTAL'
        assert m1.pitch_x == 0.10
        assert m1.pitch_y == 0.10
        assert m1.width == 0.05
        assert m1.spacing == 0.05

    def test_M2_vertical(self, tlef_parser):
        m2 = tlef_parser.layers['M2']
        assert m2.direction == 'VERTICAL'
        assert m2.pitch_x == 0.12
        assert m2.width == 0.06

    def test_M3_properties(self, tlef_parser):
        m3 = tlef_parser.layers['M3']
        assert m3.type == 'ROUTING'
        assert m3.direction == 'HORIZONTAL'
        assert m3.width == 0.08

    def test_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            TlefParser('nonexistent_file.lef')


# ======================== LefParser ========================

class TestLefParser:
    def test_parse_3_macros(self, lef_parser):
        macros = lef_parser.getMacros()
        assert len(macros) == 6
        assert 'BUFX2' in macros
        assert 'DFF' in macros
        assert 'NAND2' in macros
        assert 'INV' in macros
        assert 'NOR2' in macros
        assert 'MUX2' in macros

    def test_BUFX2_class_and_size(self, lef_parser):
        bufx2 = lef_parser.getMacro('BUFX2')
        assert bufx2.macroClass() == 'CORE'
        assert bufx2.size() == (0.5, 1.0)

    def test_BUFX2_pins(self, lef_parser):
        bufx2 = lef_parser.getMacro('BUFX2')
        pins = bufx2.pins()
        pin_names = [p.pin_name for p in pins]
        assert len(pins) == 4
        assert 'A' in pin_names
        assert 'Y' in pin_names
        assert 'VDD' in pin_names
        assert 'VSS' in pin_names

    def test_BUFX2_pin_directions(self, lef_parser):
        bufx2 = lef_parser.getMacro('BUFX2')
        pins = {p.pin_name: p for p in bufx2.pins()}
        assert pins['A'].direction == 'INPUT'
        assert pins['Y'].direction == 'OUTPUT'
        assert pins['VDD'].direction == 'INOUT'
        assert pins['VSS'].direction == 'INOUT'

    def test_BUFX2_pin_use(self, lef_parser):
        bufx2 = lef_parser.getMacro('BUFX2')
        pins = {p.pin_name: p for p in bufx2.pins()}
        assert pins['A'].use == 'SIGNAL'
        assert pins['VDD'].use == 'POWER'
        assert pins['VSS'].use == 'GROUND'

    def test_BUFX2_pin_counts_by_type(self, lef_parser):
        bufx2 = lef_parser.getMacro('BUFX2')
        assert bufx2.getInputPinNum() == 1
        assert bufx2.getOutputPinNum() == 1
        assert bufx2.getInoutPinNum() == 2

    def test_BUFX2_pin_A_rect(self, lef_parser):
        bufx2 = lef_parser.getMacro('BUFX2')
        pin_a = bufx2.pin('A')
        assert pin_a.layer == 'M1'
        assert len(pin_a.shape) == 2
        assert pin_a.shape[0] == (0.0, 0.3)
        assert pin_a.shape[1] == (0.1, 0.7)

    def test_DFF_pin_count(self, lef_parser):
        dff = lef_parser.getMacro('DFF')
        assert len(dff.pins()) == 5

    def test_NAND2_pin_count(self, lef_parser):
        nand2 = lef_parser.getMacro('NAND2')
        assert len(nand2.pins()) == 5

    def test_DFF_size(self, lef_parser):
        dff = lef_parser.getMacro('DFF')
        assert dff.size() == (0.8, 1.2)

    def test_NAND2_class(self, lef_parser):
        nand2 = lef_parser.getMacro('NAND2')
        assert nand2.macroClass() == 'CORE'


# ======================== DefParser ========================

class TestDefParserTop:
    def test_design_name(self, def_parser_top):
        assert def_parser_top.designName == 'top'

    def test_db_unit(self, def_parser_top):
        assert def_parser_top.dbUnit() == 2000

    def test_die_area(self, def_parser_top):
        area = def_parser_top.getDieArea()
        assert len(area) == 4

    def test_width_height(self, def_parser_top):
        assert def_parser_top.getWidth() > 0
        assert def_parser_top.getHeight() > 0

    def test_shape_points(self, def_parser_top):
        shape = def_parser_top.shape()
        assert len(shape) == 4

    def test_2_components(self, def_parser_top):
        comps = def_parser_top.getAllComponents()
        assert len(comps) == 2
        comp_names = [c.comp_name for c in comps]
        assert 'u_sub' in comp_names
        assert 'u_buf' in comp_names

    def test_component_u_sub(self, def_parser_top):
        u_sub = def_parser_top.getComponent('u_sub')
        assert u_sub.model_name == 'sub'
        assert u_sub.orient == 'N'
        assert u_sub.pos_x > 0
        assert u_sub.pos_y > 0

    def test_component_all_orientations(self, def_parser_top):
        comps = def_parser_top.getAllComponents()
        for comp in comps:
            assert comp.orient in ['N', 'S', 'W', 'E', 'FN', 'FS', 'FW', 'FE']

    def test_2_pins(self, def_parser_top):
        pins = def_parser_top.getAllPins()
        assert len(pins) == 2
        pin_names = [p.pin_name for p in pins]
        assert 'clk' in pin_names
        assert 'out' in pin_names

    def test_pin_clk(self, def_parser_top):
        clk = def_parser_top.getPin('clk')
        assert clk.direction == 'INPUT'

    def test_pin_out(self, def_parser_top):
        out = def_parser_top.getPin('out')
        assert out.direction == 'OUTPUT'

    def test_3_nets(self, def_parser_top):
        nets = def_parser_top.getAllNets()
        assert len(nets) == 3

    def test_net_has_wiring(self, def_parser_top):
        nets = def_parser_top.getAllNets()
        nets_with_wires = [n for n in nets if n.wiring]
        assert len(nets_with_wires) > 0

    def test_net_wire_layer(self, def_parser_top):
        for net in def_parser_top.getAllNets():
            for wire in net.wiring:
                assert wire.layer_name == 'M1'

    def test_net_has_connections(self, def_parser_top):
        nets = def_parser_top.getAllNets()
        nets_with_conn = [n for n in nets if n.connect_pins]
        assert len(nets_with_conn) > 0


class TestDefParserSub:
    def test_design_name(self, def_parser_sub):
        assert def_parser_sub.designName == 'sub'

    def test_3_components(self, def_parser_sub):
        comps = def_parser_sub.getAllComponents()
        assert len(comps) == 3
        comp_names = [c.comp_name for c in comps]
        assert 'BUFX2_inst' in comp_names
        assert 'DFF_inst' in comp_names
        assert 'NAND2_inst' in comp_names

    def test_2_pins(self, def_parser_sub):
        pins = def_parser_sub.getAllPins()
        assert len(pins) == 2
        pin_names = [p.pin_name for p in pins]
        assert 'clk' in pin_names
        assert 'sig_out' in pin_names

    def test_3_nets(self, def_parser_sub):
        nets = def_parser_sub.getAllNets()
        assert len(nets) == 3

    def test_multisegment_net(self, def_parser_sub):
        net_n1 = def_parser_sub.getNet('n1')
        assert len(net_n1.wiring) == 2

    def test_db_unit(self, def_parser_sub):
        assert def_parser_sub.dbUnit() == 2000


class TestDefParserOptions:
    def test_skip_comp(self, top_def_path):
        dp = DefParser(def_file=top_def_path, skip_comp=True)
        assert len(dp.getAllComponents()) == 0

    def test_parse_pin_false(self, top_def_path):
        dp = DefParser(def_file=top_def_path, parse_pin=False)
        assert len(dp.getAllPins()) == 0

    def test_no_nets_when_parse_net_false(self, top_def_path):
        dp = DefParser(def_file=top_def_path, parse_net=False)
        assert len(dp.getAllNets()) == 0


# ======================== VerilogParser ========================

class TestVerilogParser:
    def test_2_modules(self, verilog_parser):
        assert len(verilog_parser) >= 2
        assert 'top' in verilog_parser
        assert 'sub' in verilog_parser

    def test_top_ports(self, verilog_parser):
        top = verilog_parser['top']
        ports = top.allPorts
        assert 'clk' in ports
        assert 'out' in ports

    def test_top_port_direction(self, verilog_parser):
        top = verilog_parser['top']
        assert top.port('clk').direction == 'input'
        assert top.port('out').direction == 'output'

    def test_sub_ports(self, verilog_parser):
        sub = verilog_parser['sub']
        ports = sub.allPorts
        assert 'clk' in ports
        assert 'sig_out' in ports

    def test_top_nets(self, verilog_parser):
        top = verilog_parser['top']
        nets = top.allNets
        assert 'n0' in nets

    def test_sub_nets(self, verilog_parser):
        sub = verilog_parser['sub']
        nets = sub.allNets
        assert 'n1' in nets
        assert 'n2' in nets

    def test_top_instances(self, verilog_parser):
        top = verilog_parser['top']
        insts = top.allInsts
        assert 'u_sub' in insts
        assert 'u_buf' in insts

    def test_top_instance_cell_names(self, verilog_parser):
        top = verilog_parser['top']
        assert top.inst('u_sub').cell_name == 'sub'
        assert top.inst('u_buf').cell_name == 'BUFX2'

    def test_sub_instances(self, verilog_parser):
        sub = verilog_parser['sub']
        insts = sub.allInsts
        assert 'BUFX2_inst' in insts
        assert 'DFF_inst' in insts
        assert 'NAND2_inst' in insts

    def test_sub_instance_cell_names(self, verilog_parser):
        sub = verilog_parser['sub']
        assert sub.inst('BUFX2_inst').cell_name == 'BUFX2'
        assert sub.inst('DFF_inst').cell_name == 'DFF'
        assert sub.inst('NAND2_inst').cell_name == 'NAND2'


# ======================== InstExtractor ========================

class TestInstExtractor:
    def test_extract_leaf_instances(self, top_v_path):
        ext = InstExtractor(top_v_path, 'top')
        assert len(ext.insts) > 0
        for path, cell in ext.insts.items():
            assert isinstance(path, str)
            assert isinstance(cell, str)

    def test_extract_top_level_buf(self, top_v_path):
        ext = InstExtractor(top_v_path, 'top')
        buf_insts = {k: v for k, v in ext.insts.items() if v == 'BUFX2'}
        assert len(buf_insts) > 0


# ======================== SpefParser ========================

class TestSpefParser:
    def test_parse_completes(self, spef_parser):
        assert isinstance(spef_parser.nets, dict)

    def test_name_map_populated(self, spef_parser):
        assert isinstance(spef_parser.name_map, dict)
        assert len(spef_parser.name_map) >= 3

    def test_net_has_capacitance(self, spef_parser):
        for net in spef_parser.nets.values():
            assert net.total_cap > 0

    def test_net_is_digraph(self, spef_parser):
        for net in spef_parser.nets.values():
            assert isinstance(net.net_name, str)
            assert net.total_cap > 0


# ======================== LibertyParser ========================

class TestLibertyParser:
    def test_parse_3_cells(self, lib_parser):
        macros = lib_parser.getMacros()
        assert len(macros) == 6

    def test_BUFX2_area(self, lib_parser):
        macros = lib_parser.getMacros()
        assert len(macros) > 0
        for name, cell in macros.items():
            if 'BUFX2' in name or name == 'BUFX2':
                assert cell.area == 0.5
                return
        pytest.fail('BUFX2 not found')

    def test_DFF_area(self, lib_parser):
        macros = lib_parser.getMacros()
        for name, cell in macros.items():
            if 'DFF' in name or name == 'DFF':
                assert cell.area == 0.96
                return
        pytest.fail('DFF not found')

    def test_NAND2_area(self, lib_parser):
        macros = lib_parser.getMacros()
        for name, cell in macros.items():
            if 'NAND2' in name or name == 'NAND2':
                assert cell.area == 0.32
                return
        pytest.fail('NAND2 not found')

    def test_cell_has_area(self, lib_parser):
        macros = lib_parser.getMacros()
        for cell in macros.values():
            assert cell.area > 0

    def test_leakage_values(self, lib_parser):
        macros = lib_parser.getMacros()
        for cell in macros.values():
            assert cell.leakage >= 0
