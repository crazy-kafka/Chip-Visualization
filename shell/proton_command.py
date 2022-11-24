from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ui import UiDB
from verilog import InstExtractor


def createDB() -> UiDB:
    return UiDB()


def runfile(input_file):
    __console.runfile(input_file)


def extractNetlistInsts(nl_file: str, top_name: str) -> Dict[str, str]:
    extractor = InstExtractor(nl_file, top_name)
    return extractor.insts
