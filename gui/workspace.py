from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dataBase import DbDataBase
    from .mainWindow import MainWindow
    from ui.uiView import UiView


from PyQt5 import QtWidgets, QtGui, QtCore
from .mainView import MainView
from .gridMapPanel import GridMapPanel


class Workspace(QtWidgets.QWidget):

    def __init__(self, workspace_tag: str, dataBase: DbDataBase, parent_window: MainWindow, parent=None):
        super(Workspace, self).__init__(parent=parent)
        self.__tag = workspace_tag
        self.database = dataBase
        self.parent_window = parent_window

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.leftLayout = QtWidgets.QVBoxLayout()
        self.viewLayout = QtWidgets.QVBoxLayout()

        self.view = MainView(self.database, workspace_tag)
        self.grid_map_panel = GridMapPanel(self.view.HEATMAP_COLORS)

        self.__ui_view = None

        self.__initUi()

    def __initUi(self):
        self.setLayout(self.mainLayout)
        self.mainLayout.addLayout(self.leftLayout, stretch=1)
        self.mainLayout.addLayout(self.viewLayout, stretch=5)

        self.leftLayout.addWidget(self.grid_map_panel)
        self.viewLayout.addWidget(self.view)

    def setUiView(self, ui_view: UiView):
        self.__ui_view = ui_view

    @property
    def tag(self) -> str:
        return self.__tag

    @property
    def ui_view(self):
        return self.__ui_view



