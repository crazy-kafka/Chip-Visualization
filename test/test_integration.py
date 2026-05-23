"""
Integration tests: full parse flow, DEF overlay, save/load, manual design.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataBase import DbDataBase
from dataBase.dbChip import DbChip
from dataBase.dbNet import DbNet
from dataBase.dbWire import DbWire
from dataBase.dbHInst import DbHInst


class TestFullParseFlow:
    def test_full_parse_flow(self, db):
        assert db.chip is not None
        assert db.chip.name == 'chip_top'
        assert len(db.layers) >= 3
        assert len(db.cells) >= 3
        assert len(db.chip.hInst.treeHInsts) > 0
        assert len(db.chip.nets) > 0
        assert db.is_initialized is True

    def test_cross_hierarchy_net_names(self, db):
        nets = db.chip.nets
        assert 'clk' in nets
        assert 'rst' in nets
        assert 'u_core_0/alu0_out' in nets
        assert 'u_core_0/u_alu_0/u_adder/n0' in nets

    def test_top_level_hInst_has_nets(self, db):
        root = db.chip.hInst
        assert len(root.hNets) > 0


class TestDefOverlay:
    def test_definePartitionByDef_adds_module_defs(self, db, chip_top_def_path, core_def_path):
        db.definePartitionByDef([chip_top_def_path, core_def_path])
        assert len(db.module_def_dict) > 0
        assert 'chip_top' in db.module_def_dict
        assert 'core' in db.module_def_dict

    def test_definePartitionByDef_sets_pin_locations(self, db, chip_top_def_path, core_def_path):
        db.definePartitionByDef([chip_top_def_path, core_def_path])
        for hInst in db.allHInsts():
            if hInst.is_ptn:
                assert hInst.shape is not None
                assert len(hInst.shape) > 0


class TestSaveLoadRoundtrip:
    def test_full_save_and_load(self, db, tmp_path, chip_top_def_path, core_def_path):
        db.definePartitionByDef([chip_top_def_path, core_def_path])
        out_dir = str(tmp_path / 'full_db')
        os.makedirs(out_dir, exist_ok=True)
        db.saveDataBase(out_dir)

        db2 = DbDataBase()
        result = db2.loadDataBase(out_dir)
        assert result is True
        assert db2.chip.name == db.chip.name
        assert db2.is_initialized is True

    def test_save_no_pin_loc(self, db, tmp_path):
        out_dir = str(tmp_path / 'no_pin_db')
        os.makedirs(out_dir, exist_ok=True)
        db.saveDataBase(out_dir, no_pin_loc=True)


class TestManualDesignFlow:
    def test_add_inst_net_wire_full_flow(self, db):
        insts = db.addInst('my_buf', 'BUFX2', pt_x=100, pt_y=200, orient='N')
        assert len(insts) == 1
        nets = db.addNet('my_net')
        assert len(nets) == 1

    def test_addInst_fails_duplicate(self, db):
        db.addInst('unique_inst', 'BUFX2', pt_x=10, pt_y=10, orient='N')
        result = db.addInst('unique_inst', 'BUFX2', pt_x=10, pt_y=10, orient='N')
        assert len(result) == 0
