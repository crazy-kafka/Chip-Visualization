"""
Shared pytest fixtures for Photon test suite.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture(scope='session')
def data_dir():
    return DATA_DIR


@pytest.fixture(scope='session')
def tech_lef_path(data_dir):
    return os.path.join(data_dir, 'tech.lef')


@pytest.fixture(scope='session')
def cells_lef_path(data_dir):
    return os.path.join(data_dir, 'cells.lef')


@pytest.fixture(scope='session')
def cells_lib_path(data_dir):
    return os.path.join(data_dir, 'cells.lib')


@pytest.fixture(scope='session')
def top_v_path(data_dir):
    return os.path.join(data_dir, 'top.v')


@pytest.fixture(scope='session')
def sub_v_path(data_dir):
    return os.path.join(data_dir, 'sub.v')


@pytest.fixture(scope='session')
def top_def_path(data_dir):
    return os.path.join(data_dir, 'top.def')


@pytest.fixture(scope='session')
def sub_def_path(data_dir):
    return os.path.join(data_dir, 'sub.def')


@pytest.fixture(scope='session')
def spef_path(data_dir):
    return os.path.join(data_dir, 'test.spef')

# ---- New 4-level hierarchy data ----
@pytest.fixture(scope='session')
def chip_top_v_path(data_dir):
    return os.path.join(data_dir, 'chip_top.v')

@pytest.fixture(scope='session')
def core_v_path(data_dir):
    return os.path.join(data_dir, 'core.v')

@pytest.fixture(scope='session')
def alu_v_path(data_dir):
    return os.path.join(data_dir, 'alu.v')

@pytest.fixture(scope='session')
def adder_v_path(data_dir):
    return os.path.join(data_dir, 'adder.v')

@pytest.fixture(scope='session')
def chip_top_def_path(data_dir):
    return os.path.join(data_dir, 'chip_top.def')

@pytest.fixture(scope='session')
def core_def_path(data_dir):
    return os.path.join(data_dir, 'core.def')

@pytest.fixture(scope='session')
def alu_def_path(data_dir):
    return os.path.join(data_dir, 'alu.def')

@pytest.fixture(scope='session')
def adder_def_path(data_dir):
    return os.path.join(data_dir, 'adder.def')


@pytest.fixture(scope='session')
def tlef_parser(tech_lef_path):
    from LEF import TlefParser
    return TlefParser(tech_lef_path)


@pytest.fixture(scope='session')
def lef_parser(cells_lef_path):
    from LEF import LefParser
    return LefParser([cells_lef_path])


@pytest.fixture(scope='session')
def lib_parser(cells_lib_path):
    from timingLib import LibertyParser
    return LibertyParser([cells_lib_path])


@pytest.fixture(scope='session')
def verilog_parser(top_v_path, sub_v_path):
    """Original 2-level verilog (used by parser-specific tests)."""
    from verilog import VerilogParser
    modules = {}
    for path in [top_v_path, sub_v_path]:
        vp = VerilogParser(path)
        modules.update(vp.allModules())
    return modules

@pytest.fixture(scope='session')
def verilog_parser_4level(chip_top_v_path, core_v_path, alu_v_path, adder_v_path):
    from verilog import VerilogParser
    modules = {}
    for path in [chip_top_v_path, core_v_path, alu_v_path, adder_v_path]:
        vp = VerilogParser(path)
        modules.update(vp.allModules())
    return modules


@pytest.fixture(scope='session')
def def_parser_top(top_def_path):
    from DEF import DefParser
    return DefParser(def_file=top_def_path, parse_pin=True, parse_net=True)


@pytest.fixture(scope='session')
def def_parser_sub(sub_def_path):
    from DEF import DefParser
    return DefParser(def_file=sub_def_path, parse_pin=True, parse_net=True)


@pytest.fixture(scope='session')
def spef_parser(spef_path):
    from spef import SpefParser
    return SpefParser(spef_path)


@pytest.fixture(scope='function')
def db(tech_lef_path, cells_lef_path, cells_lib_path,
       chip_top_v_path, core_v_path, alu_v_path, adder_v_path):
    """Create an initialized DbDataBase with 4-level test data."""
    from dataBase import DbDataBase
    database = DbDataBase()
    database.TECH_LEF = tech_lef_path
    database.LEF_LIST = [cells_lef_path]
    database.LIB_LIST = [cells_lib_path]
    database.VERILOG_LIST = [chip_top_v_path, core_v_path, alu_v_path, adder_v_path]
    database.TOP_NAME = 'chip_top'
    database.initDataBase()
    return database

@pytest.fixture(scope='function')
def db_with_def(db, chip_top_def_path, core_def_path, alu_def_path, adder_def_path):
    """Create an initialized DbDataBase with DEF overlay for partition info."""
    db.definePartitionByDef([chip_top_def_path, core_def_path,
                              alu_def_path, adder_def_path])
    return db
