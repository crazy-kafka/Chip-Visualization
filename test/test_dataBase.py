"""
Unit tests for the dataBase module: DbDataBase, DbChip, DbHInst,
DbNet, DbWire, DbInst, DbGridMap.
"""
import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataBase import DbDataBase
from dataBase.dbChip import DbChip
from dataBase.dbHInst import DbHInst
from dataBase.dbNet import DbNet
from dataBase.dbWire import DbWire
from dataBase.dbInst import DbInst
from dataBase.dbGridMap import DbGridMap
from utils.pstatus import PSTATUS


# ======================== DbDataBase Initialization ========================

class TestDbDataBaseInit:
    def test_initDataBase_creates_chip(self, db):
        assert db.chip is not None
        assert db.chip.name == 'chip_top'

    def test_initDataBase_creates_layers(self, db):
        assert len(db.layers) == 3
        assert 'M1' in db.layers
        assert 'M2' in db.layers
        assert 'M3' in db.layers
        assert db.layers['M1'].idx > 0

    def test_initDataBase_creates_cells(self, db):
        assert len(db.cells) == 6
        assert 'BUFX2' in db.cells
        assert 'DFF' in db.cells
        assert 'NAND2' in db.cells
        assert db.cells['BUFX2'].width == 0.5
        assert db.cells['BUFX2'].height == 1.0

    def test_cell_macro_merges_lef_and_lib(self, db):
        bufx2 = db.cells['BUFX2']
        assert len(bufx2.terms) > 0
        assert bufx2.footprint == 'buf'
        assert bufx2.leakage == 0.001
        assert bufx2.area == 0.5

    def test_initDataBase_hierarchy_not_empty(self, db):
        assert db.chip.hInst is not None
        tree = db.chip.hInst.treeHInsts
        assert len(tree) > 0
        assert 'u_core_0' in tree

    def test_initDataBase_nets_created(self, db):
        nets = db.chip.nets
        assert len(nets) > 0
        for net in nets.values():
            assert isinstance(net, DbNet)

    def test_allHInsts_includes_root(self, db):
        all_hinsts = db.allHInsts()
        assert any(h.name == '' for h in all_hinsts)  # root has empty name


class TestDbDataBaseManualAdd:
    def test_addInst_creates_DbInst(self, db):
        result = db.addInst('test_inst', 'BUFX2', pt_x=10, pt_y=20, orient='N')
        assert len(result) > 0
        assert result[0].name in db.chip.insts

    def test_addInst_with_placement(self, db):
        result = db.addInst('placed_inst', 'BUFX2', pt_x=10, pt_y=20, orient='N')
        assert len(result) > 0
        inst = result[0]
        assert inst.pstatus == PSTATUS.PLACED
        assert len(inst.shape) > 0

    def test_addNet_creates_DbNet(self, db):
        result = db.addNet('test_net', base_module=None)
        assert len(result) > 0
        net = result[0]
        assert isinstance(net, DbNet)
        assert net.name in db.chip.nets

    def test_attachToTerm_connects(self, db):
        db.addInst('term_test_inst', 'BUFX2', pt_x=0, pt_y=0, orient='N')
        inst_term_name = 'term_test_inst/A'
        assert inst_term_name in db.chip.insts['term_test_inst'].instTerms


# ======================== DbChip ========================

class TestDbChip:
    def test_chip_insts_initially_empty_dict(self):
        chip = DbChip('test_top')
        assert chip.insts == {}

    def test_chip_nets_initially_empty_dict(self):
        chip = DbChip('test_top')
        assert chip.nets == {}

    def test_chip_hInst_is_root(self):
        chip = DbChip('test_top')
        assert chip.hInst is not None
        assert chip.hInst.name == ''


# ======================== DbHInst ========================

class TestDbHInst:
    def test_add_child(self):
        parent = DbHInst(name='parent', cell='CELL_A', pHInst=None)
        child = DbHInst(name='parent/child', cell='CELL_B', pHInst=parent)
        parent.addHInst(child)
        assert 'parent/child' in parent.hInsts

    def test_add_hNet(self):
        parent = DbHInst(name='parent', cell='CELL_A', pHInst=None)
        parent.addHNet('net_a')
        assert 'parent/net_a' in parent.hNets

    def test_treeHInsts_flattens(self):
        root = DbHInst(name='', cell='TOP', pHInst=None)
        child = DbHInst(name='child', cell='CELL_A', pHInst=root)
        root.addHInst(child)
        grandchild = DbHInst(name='child/grandchild', cell='CELL_B', pHInst=child)
        child.addHInst(grandchild)
        tree = root.treeHInsts
        assert 'child' in tree
        assert 'child/grandchild' in tree

    def test_is_ptn_only_when_defined(self):
        hinst = DbHInst(name='test', cell='CELL_A', pHInst=None)
        assert hinst.is_ptn is False
        hinst.definePartition(
            shape=[(0, 0), (10, 0), (10, 10), (0, 10)],
            pt_x=0, pt_y=0, origin_x=0, origin_y=0,
            orient='N', area=100.0
        )
        assert hinst.is_ptn is True

    def test_define_partition_sets_properties(self):
        hinst = DbHInst(name='test', cell='CELL_A', pHInst=None)
        hinst.definePartition(
            shape=[(0, 0), (10, 0), (10, 10), (0, 10)],
            pt_x=5, pt_y=5, origin_x=0, origin_y=0,
            orient='N', area=100.0
        )
        assert hinst.ptn_orient == 'N'
        assert hinst.area == 100.0


# ======================== DbNet / DbWire ========================

class TestDbNetAndDbWire:
    def test_wire_auto_registers_with_net(self):
        net = DbNet('test_net')
        DbWire(net=net, layer=None, from_pt=(0, 0), to_pt=(10, 0), width=0.5, begin_ext=0.0, end_ext=0.0)
        assert len(net.wires) == 1

    def test_wire_horizontal_valid(self, db):
        net = db.chip.nets[list(db.chip.nets.keys())[0]]
        wire = DbWire(net=net, layer=db.layers['M1'], from_pt=(0, 0), to_pt=(10, 0), width=0.1, begin_ext=0.0, end_ext=0.0)
        assert wire.direction == 'HORIZONTAL'

    def test_wire_vertical_valid(self, db):
        net = db.chip.nets[list(db.chip.nets.keys())[0]]
        wire = DbWire(net=net, layer=db.layers['M1'], from_pt=(5, 0), to_pt=(5, 10), width=0.1, begin_ext=0.0, end_ext=0.0)
        assert wire.direction == 'VERTICAL'

    def test_wire_diagonal_still_creates(self, db):
        net = db.chip.nets[list(db.chip.nets.keys())[0]]
        wire = DbWire(net=net, layer=db.layers['M1'], from_pt=(0, 0), to_pt=(10, 10), width=0.1, begin_ext=0.0, end_ext=0.0)
        assert wire is not None

    def test_net_length_accumulates(self, db):
        net = DbNet('length_test_net')
        DbWire(net=net, layer=None, from_pt=(0, 0), to_pt=(10, 0), width=0.5, begin_ext=0.0, end_ext=0.0)
        DbWire(net=net, layer=None, from_pt=(10, 0), to_pt=(10, 10), width=0.5, begin_ext=0.0, end_ext=0.0)
        assert net.length == pytest.approx(20.0)

    def test_wire_shape_has_4_points(self, db):
        net = db.chip.nets[list(db.chip.nets.keys())[0]]
        wire = DbWire(net=net, layer=db.layers['M1'], from_pt=(0, 0), to_pt=(10, 0), width=0.1, begin_ext=0.0, end_ext=0.0)
        assert len(wire.shape) == 4


# ======================== DbGridMap ========================

class TestDbGridMap:
    def test_grid_map_updateColorGrid(self):
        grid = np.array([[0.0, 5.0], [10.0, 15.0]], dtype=float)
        from PyQt5 import QtGui
        colors = [QtGui.QBrush(QtGui.QColor(255, 0, 0, 150)),
                  QtGui.QBrush(QtGui.QColor(0, 255, 0, 150))]
        db_grid = DbGridMap('test_map', grid, colors)
        db_grid.updateColorGrid()
        assert db_grid.color_grid_image.shape == (2, 2, 4)

    def test_grid_map_nan_to_transparent(self):
        grid = np.array([[0.0, np.nan], [10.0, 15.0]], dtype=float)
        from PyQt5 import QtGui
        colors = [QtGui.QBrush(QtGui.QColor(255, 0, 0, 150)),
                  QtGui.QBrush(QtGui.QColor(0, 255, 0, 150))]
        db_grid = DbGridMap('test_map', grid, colors)
        db_grid.updateColorGrid()
        assert np.all(db_grid.color_grid_image[0, 1] == np.array([0, 0, 0, 0]))


# ======================== Serialization ========================

class TestSerialization:
    def test_save_load_roundtrip(self, db, tmp_path):
        out_dir = str(tmp_path / 'test_save')
        os.makedirs(out_dir, exist_ok=True)
        db.saveDataBase(out_dir)

        db2 = DbDataBase()
        db2.loadDataBase(out_dir)
        assert db2.chip.name == db.chip.name
        assert db2.TOP_NAME == db.TOP_NAME
