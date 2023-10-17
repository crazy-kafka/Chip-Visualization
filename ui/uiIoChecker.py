from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from ioTiming import IOChecker
    from ui.uiDB import UiDB
    from gui import Workspace

import math
import os
import pandas as pd
from utils import Print
from utils import CoordinateProcess


class UiIoChecker:

    def __init__(self, workspace: Workspace, io_checker: IOChecker, check_type: bool):
        self.__workspace = workspace
        self.__io_checker = io_checker

















