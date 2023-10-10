from __future__ import annotations
from typing import List, Tuple, Dict, Union, Iterable, TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    from .instItem import InstItem
    from dataBase import DbDataBase
    from .wireItem import WireItem

from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os
import pandas as pd
from .workspace import Workspace
from utils import CoordinateProcess, Print, GlobalVariable
from dataBase.dbWire import DbWire
from dataBase.dbInst import DbInst
from dataBase.dbHInst import DbHInst


class MainWindow(QtWidgets.QWidget):

    STARTUP_WIDTH = 1000
    STARTUP_HEIGHT = 800

    sigOpenDb = QtCore.pyqtSignal(str)
    sigReadRpt = QtCore.pyqtSignal(str)

    def __init__(self, db: DbDataBase):
        super(MainWindow, self).__init__()

        self.dataBase = db
        self.dataBase.gui_window = self

        self.main_layout = QtWidgets.QVBoxLayout()
        self.menu_bar = QtWidgets.QMenuBar()
        self.tool_bar = QtWidgets.QToolBar()
        self.status_bar = QtWidgets.QStatusBar()
        self.mouse_pos_status = QtWidgets.QLabel()

        self.menu_file = QtWidgets.QMenu('File')
        self.load_db_action = QtWidgets.QAction('Load DB')
        self.save_db_action = QtWidgets.QAction('Save DB')

        self.workspace_layout = QtWidgets.QHBoxLayout()

        self.workspace_layout = QtWidgets.QHBoxLayout()

        # self.workspaces: Dict[str, Workspace] = {}
        self.tab = QtWidgets.QTabWidget()
        self.workspace: [None, Workspace]= None

        self.insts: Dict[str, InstItem] = {}
        self.net_wire_dict: Dict[str, List[WireItem]] = {}

        self.marker_brower = None

        self.__initUi()
        self.__connectSignal()

    def __initUi(self):
        self.setWindowTitle(GlobalVariable.SOFTWARE)
        self.resize(self.STARTUP_WIDTH, self.STARTUP_HEIGHT)

        self.workspace_layout.addWidget(self.tab, stretch=1)

        self.main_layout.addWidget(self.menu_bar, stretch=0)
        self.main_layout.addWidget(self.tool_bar, stretch=0)
        self.main_layout.addLayout(self.workspace_layout)
        self.main_layout.addWidget(self.status_bar, stretch=0)

        #menu bar
        self.menu_bar.addMenu(self.menu_file)
        self.menu_file.addAction(self.load_db_action)
        self.menu_file.addAction(self.save_db_action)

        #status bar
        self.status_bar.addPermanentWidget(self.mouse_pos_status)
        self.mouse_pos_status.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.setLayout(self.main_layout)

        win = self.frameGeometry()
        pos = QtWidgets.QDesktopWidget().availableGeometry().center()
        win.moveCenter(pos)
        self.move(win.topLeft())

    def __connectSignal(self):
        self.__connectMenuSig()

    def __connectMenuSig(self):
        self.load_db_action.triggered.connect(self.__menuOpenDb)
        self.save_db_action.triggered.connect(self.__menuSaveDb)

    def __menuOpenDb(self):
        file_name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Load DataBase', os.getcwd())
        if os.path.exists(file_name):
            self.sigOpenDb.emit(file_name)

    def __menuSaveDb(self):
        file_name, flag = QtWidgets.QFileDialog.getSaveFileName(self, 'Load DataBase', os.getcwd(), "")
        if file_name:
            os.system(f'mkdir -p {file_name}')
            self.dataBase.saveDataBase(file_name)

    def addView(self):
        view_name = 'physical view'
        self.workspace = Workspace(view_name, self.dataBase, parent_window=self)
        self.tab.addTab(self.workspace, view_name)
        self.initializeWorkSpace()
        self.connectWorkspaceSig()

    # def __addView(self, view_name: str) -> Workspace:
    #     Print(f'Add layout view << {view_name} >>')
    #     workspace = Workspace(view_name, self.dataBase, parent_window=self)
    #     # self.workspaces[view_name] = workspace
    #     self.workspace = workspace
    #     self.tab.addTab(workspace, view_name)
    #     self.initializeWorkSpace(workspace)
    #     self.connectWorkspaceSig(workspace)
    #     return workspace

    def connectWorkspaceSig(self):
        self.workspace.view.sigSelectOneItem.connect(self.__updateSelectedStatus)
        self.workspace.view.sigSceneMouseMoved.connect(lambda pt: self.mouse_pos_status.setText(f'{round(pt.x(), 4)}, {round(pt.y(), 4)}'))

    def initializeWorkSpace(self):
        self.workspace.view.addPtn(self.dataBase.chip.hInst)
        for hInst_name, hInst in self.dataBase.chip.hInst.treeHInsts.items():
            if hInst.is_ptn:
                self.workspace.view.addPtn(hInst)
        self.workspace.view.updateBoundingRect()
        self.workspace.view.fit()

    def __updateSelectedStatus(self, select_obj: Union[DbInst, DbWire, DbHInst, None]):
        if type(select_obj) == DbInst or type(select_obj) == DbHInst:
            self.status_bar.showMessage(select_obj.name, 10000000000000)
            self.dataBase.appendSelected(select_obj)
        elif type(select_obj) == DbWire:
            self.status_bar.showMessage(select_obj.net.name, 10000000000000)
        elif select_obj is None:
            self.status_bar.clearMessage()
            self.dataBase.clearSelected()

















