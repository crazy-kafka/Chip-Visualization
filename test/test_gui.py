"""
GUI tests: MainWindow, MainView, InstItem, WireItem, GridPixMapItem,
Point, GenericGraphicsView. Uses manual QApplication management.
"""
import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5 import QtWidgets, QtCore, QtGui


@pytest.fixture(scope='session')
def qapp():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    yield app


@pytest.fixture
def db_for_gui():
    from dataBase import DbDataBase
    db = DbDataBase()
    db.TOP_NAME = 'test_top'
    return db


@pytest.fixture
def window(qapp, db_for_gui):
    from gui.mainWindow import MainWindow
    win = MainWindow(db_for_gui)
    yield win
    win.close()


# ======================== Point ========================

class TestPoint:
    def test_constructor_scalar(self):
        from gui.Point import Point
        p = Point(5)
        assert p.x() == 5.0
        assert p.y() == 5.0

    def test_constructor_tuple(self):
        from gui.Point import Point
        p = Point((1, 2))
        assert p.x() == 1.0
        assert p.y() == 2.0

    def test_constructor_two_args(self):
        from gui.Point import Point
        p = Point(3.5, 4.5)
        assert p.x() == 3.5
        assert p.y() == 4.5

    def test_length_3_4_5(self):
        from gui.Point import Point
        p = Point(3, 4)
        assert p.length() == 5.0

    def test_dot_product(self):
        from gui.Point import Point
        assert Point(1, 0).dot(Point(0, 1)) == 0.0
        assert Point(2, 3).dot(Point(4, 5)) == 23.0

    def test_cross_product(self):
        from gui.Point import Point
        assert Point(1, 0).cross(Point(0, 1)) == 1.0
        assert Point(0, 1).cross(Point(1, 0)) == -1.0

    def test_angle_90_degrees(self):
        from gui.Point import Point
        ang = Point(1, 0).angle(Point(0, 1))
        assert abs(ang) == pytest.approx(90.0)

    def test_addition(self):
        from gui.Point import Point
        p = Point(1, 2) + Point(3, 4)
        assert p.x() == 4.0
        assert p.y() == 6.0

    def test_subtraction(self):
        from gui.Point import Point
        p = Point(5, 7) - Point(2, 3)
        assert p.x() == 3.0
        assert p.y() == 4.0

    def test_multiplication(self):
        from gui.Point import Point
        p = Point(2, 3) * 2
        assert p.x() == 4.0
        assert p.y() == 6.0

    def test_division(self):
        from gui.Point import Point
        p = Point(6, 9) / 3
        assert p.x() == 2.0
        assert p.y() == 3.0

    def test_indexing(self):
        from gui.Point import Point
        p = Point(1, 2)
        assert p[0] == 1.0
        assert p[1] == 2.0

    def test_copy(self):
        from gui.Point import Point
        p1 = Point(1, 2)
        p2 = p1.copy()
        assert p2.x() == 1.0
        assert p2.y() == 2.0


# ======================== MainWindow ========================

class TestMainWindow:
    def test_window_created(self, window):
        assert window is not None
        assert window.isVisible() is False

    def test_window_title(self, window):
        from utils.globalVariable import GlobalVariable
        assert window.windowTitle() == GlobalVariable.SOFTWARE

    def test_window_default_size(self, window):
        assert window.width() > 0
        assert window.height() > 0

    def test_menu_bar_exists(self, window):
        assert window.menu_bar is not None

    def test_menu_file_exists(self, window):
        assert window.menu_file is not None
        assert window.menu_file.title() == 'File'

    def test_load_db_action_exists(self, window):
        assert window.load_db_action is not None
        assert window.load_db_action.text() == 'Load DB'

    def test_save_db_action_exists(self, window):
        assert window.save_db_action is not None
        assert window.save_db_action.text() == 'Save DB'

    def test_status_bar_exists(self, window):
        assert window.status_bar is not None

    def test_mouse_pos_status_label(self, window):
        assert window.mouse_pos_status is not None

    def test_insts_dict_initially_empty(self, window):
        assert window.insts == {}

    def test_net_wire_dict_initially_empty(self, window):
        assert window.net_wire_dict == {}

    def test_addView_creates_workspace(self, qapp):
        from gui.mainWindow import MainWindow
        from dataBase import DbDataBase
        db = DbDataBase()
        db.TECH_LEF = os.path.join(os.path.dirname(__file__), 'data', 'tech.lef')
        db.LEF_LIST = [os.path.join(os.path.dirname(__file__), 'data', 'cells.lef')]
        db.LIB_LIST = [os.path.join(os.path.dirname(__file__), 'data', 'cells.lib')]
        db.VERILOG_LIST = [
            os.path.join(os.path.dirname(__file__), 'data', 'chip_top.v'),
            os.path.join(os.path.dirname(__file__), 'data', 'core.v'),
            os.path.join(os.path.dirname(__file__), 'data', 'alu.v'),
            os.path.join(os.path.dirname(__file__), 'data', 'adder.v'),
        ]
        db.TOP_NAME = 'chip_top'
        db.initDataBase()
        win = MainWindow(db)
        win.addView()
        assert win.workspace is not None
        assert win.tab.count() > 0
        win.close()

    def test_sigOpenDb_signal(self, window):
        assert window.sigOpenDb is not None


# ======================== MainView ========================

class TestMainView:
    def test_view_created(self, qapp, db_for_gui):
        from gui.mainView import MainView
        view = MainView(db_for_gui, 'test_view')
        assert view is not None
        assert view.view_tag == 'test_view'

    def test_view_black_background(self, qapp, db_for_gui):
        from gui.mainView import MainView
        view = MainView(db_for_gui, 'test_view')
        brush = view.backgroundBrush()
        assert brush.color().red() == 0
        assert brush.color().green() == 0
        assert brush.color().blue() == 0

    def test_view_has_scene(self, qapp, db_for_gui):
        from gui.mainView import MainView
        view = MainView(db_for_gui, 'test_view')
        assert view.sceneObj is not None

    def test_view_heatmap_colors(self, qapp, db_for_gui):
        from gui.mainView import MainView
        view = MainView(db_for_gui, 'test_view')
        assert len(view.HEATMAP_COLORS) == 128

    def test_view_initial_highlighted_empty(self, qapp, db_for_gui):
        from gui.mainView import MainView
        view = MainView(db_for_gui, 'test_view')
        assert view.highlighted_items == []


# ======================== GenericGraphicsView ========================

class TestGenericGraphicsView:
    def test_view_created(self, qapp):
        from gui.genericView import GenericGraphicsView
        view = GenericGraphicsView()
        assert view is not None

    def test_view_initial_range(self, qapp):
        from gui.genericView import GenericGraphicsView
        view = GenericGraphicsView()
        assert view.range.width() > 0
        assert view.range.height() > 0

    def test_view_pixelSize(self, qapp):
        from gui.genericView import GenericGraphicsView
        view = GenericGraphicsView()
        ps = view.pixelSize()
        assert ps.x() > 0
        assert ps.y() > 0

    def test_view_has_scene(self, qapp):
        from gui.genericView import GenericGraphicsView
        view = GenericGraphicsView()
        assert view.sceneObj is not None

    def test_view_setRange(self, qapp):
        from gui.genericView import GenericGraphicsView
        view = GenericGraphicsView()
        old_w = view.range.width()
        view.setRange(padding=0)
        assert view.range.width() > 0


# ======================== InstItem ========================

class TestInstItem:
    def test_partition_item_created(self, qapp):
        from gui.instItem import InstItem
        from dataBase.dbHInst import DbHInst
        hinst = DbHInst(name='test', cell='CELL_A', pHInst=None)
        hinst.definePartition(
            shape=[(0, 0), (10, 0), (10, 10), (0, 10)],
            pt_x=0, pt_y=0, origin_x=0, origin_y=0,
            orient='N', area=100.0
        )
        item = InstItem(hinst)
        assert item is not None
        assert item.db_obj == hinst

    def test_partition_toPtn_style(self, qapp):
        from gui.instItem import InstItem
        from dataBase.dbHInst import DbHInst
        hinst = DbHInst(name='test', cell='CELL_A', pHInst=None)
        hinst.definePartition(
            shape=[(0, 0), (10, 0), (10, 10), (0, 10)],
            pt_x=0, pt_y=0, origin_x=0, origin_y=0,
            orient='N', area=100.0
        )
        item = InstItem(hinst)
        item.toPtn()
        assert item.pen == InstItem.ptn_pen
        assert item.brush == InstItem.ptn_brush

    def test_highlight(self, qapp):
        from gui.instItem import InstItem
        from dataBase.dbHInst import DbHInst
        hinst = DbHInst(name='test', cell='CELL_A', pHInst=None)
        hinst.definePartition(
            shape=[(0, 0), (10, 0), (10, 10), (0, 10)],
            pt_x=0, pt_y=0, origin_x=0, origin_y=0,
            orient='N', area=100.0
        )
        item = InstItem(hinst)
        original_z = item.zValue()
        item.highlight()
        assert item.zValue() == 1  # highlight sets z to 1
        item.deHighlight()
        assert item.zValue() == original_z

    def test_shape_polygon_points(self, qapp):
        from gui.instItem import InstItem
        from dataBase.dbHInst import DbHInst
        hinst = DbHInst(name='test', cell='CELL_A', pHInst=None)
        shape = [(0, 0), (10, 0), (10, 10), (0, 10)]
        hinst.definePartition(
            shape=shape,
            pt_x=0, pt_y=0, origin_x=0, origin_y=0,
            orient='N', area=100.0
        )
        item = InstItem(hinst)
        polygon = item.polygon()
        assert polygon.count() == 4

    def test_toObs_style(self, qapp):
        from gui.instItem import InstItem
        from dataBase.dbHInst import DbHInst
        hinst = DbHInst(name='test', cell='CELL_A', pHInst=None)
        hinst.definePartition(
            shape=[(0, 0), (10, 0), (10, 10), (0, 10)],
            pt_x=0, pt_y=0, origin_x=0, origin_y=0,
            orient='N', area=100.0
        )
        item = InstItem(hinst)
        item.toObs()
        assert item.pen == InstItem.obs_pen
        assert item.brush == InstItem.obs_brush


# ======================== WireItem ========================

class TestWireItem:
    def test_wire_item_created(self, qapp, db_for_gui):
        from gui.wireItem import WireItem
        from dataBase.dbWire import DbWire
        from dataBase.dbNet import DbNet
        from dataBase.techLayer import TechLayer
        layer = TechLayer(name='M1', layer_type='ROUTING', idx=1, direction='HORIZONTAL',
                          pitch_x=0.1, pitch_y=0.1, width=0.05, spacing=0.05,
                          area=0.0, region=None, based_layer=None)
        net = DbNet('test_net')
        wire = DbWire(net=net, layer=layer, from_pt=(0, 0), to_pt=(10, 0),
                      width=0.1, begin_ext=0.0, end_ext=0.0)
        item = WireItem(wire)
        assert item is not None
        assert item.db_obj == wire

    def test_wire_item_highlight(self, qapp, db_for_gui):
        from gui.wireItem import WireItem
        from dataBase.dbWire import DbWire
        from dataBase.dbNet import DbNet
        from dataBase.techLayer import TechLayer
        layer = TechLayer(name='M1', layer_type='ROUTING', idx=0, direction='HORIZONTAL',
                          pitch_x=0.1, pitch_y=0.1, width=0.05, spacing=0.05,
                          area=0.0, region=None, based_layer=None)
        net = DbNet('test_net')
        wire = DbWire(net=net, layer=layer, from_pt=(0, 0), to_pt=(10, 0),
                      width=0.1, begin_ext=0.0, end_ext=0.0)
        item = WireItem(wire)
        item.highlight()
        item.deHighlight()


# ======================== GridPixMapItem ========================

class TestGridPixMapItem:
    def test_created_from_rgba_array(self, qapp):
        from gui.gridPixMapItem import GridPixMapItem
        arr = np.zeros((10, 10, 4), dtype=np.uint8)
        arr[:, :, 3] = 255  # full alpha
        item = GridPixMapItem(arr, grid_size=1.0)
        assert item is not None
        assert item.grid_size == 1.0

    def test_transform_scales_by_grid_size(self, qapp):
        from gui.gridPixMapItem import GridPixMapItem
        arr = np.zeros((5, 5, 4), dtype=np.uint8)
        arr[:, :, 3] = 255
        item = GridPixMapItem(arr, grid_size=5.0)
        transform = item.transform()
        assert transform.m11() == 5.0
        assert transform.m22() == 5.0


# ======================== Palette ========================

class TestPalette:
    def test_layer_colors_count(self):
        from gui.palette import Palette
        assert len(Palette.layer_colors) == 18


# ======================== GuiVariable ========================

class TestGuiVariable:
    def test_z_values(self):
        from gui.guiVariable import GuiVariable
        assert GuiVariable.PIX_MAP_ZVALUE == 100
        assert GuiVariable.PTN_BASE_ZVALUE > 0
        assert GuiVariable.INST_BASE_ZVALUE > GuiVariable.PTN_BASE_ZVALUE
        assert GuiVariable.WIRE_BASE_ZVALUE > GuiVariable.INST_BASE_ZVALUE


# ======================== GUI Integration ========================

class TestGuiIntegration:
    def test_db_gui_window_binding(self, db_for_gui, window):
        assert db_for_gui.gui_window == window

    def test_addView_populates_workspace(self, qapp, db_for_gui):
        from gui.mainWindow import MainWindow
        db_for_gui.TECH_LEF = os.path.join(
            os.path.dirname(__file__), 'data', 'tech.lef')
        db_for_gui.LEF_LIST = [os.path.join(
            os.path.dirname(__file__), 'data', 'cells.lef')]
        db_for_gui.LIB_LIST = [os.path.join(
            os.path.dirname(__file__), 'data', 'cells.lib')]
        db_for_gui.VERILOG_LIST = [
            os.path.join(os.path.dirname(__file__), 'data', 'chip_top.v'),
            os.path.join(os.path.dirname(__file__), 'data', 'core.v'),
            os.path.join(os.path.dirname(__file__), 'data', 'alu.v'),
            os.path.join(os.path.dirname(__file__), 'data', 'adder.v'),
        ]
        db_for_gui.TOP_NAME = 'chip_top'
        db_for_gui.initDataBase()

        def_files = [
            os.path.join(os.path.dirname(__file__), 'data', 'chip_top.def'),
            os.path.join(os.path.dirname(__file__), 'data', 'core.def'),
        ]
        win = MainWindow(db_for_gui)
        db_for_gui.definePartitionByDef(def_files)
        win.addView()
        assert win.workspace is not None
        assert win.workspace.view is not None
        win.close()
