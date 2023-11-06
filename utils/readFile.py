from __future__ import annotations
from typing import List, Tuple, Dict, Union, Iterable, TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    pass

import gzip


def readFile(file_name: str) -> str:
    if file_name.endswith('.gz'):
        try:
            return gzip.open(file_name).read().decode('utf-8')
        except gzip.BadGzipFile:
            return open(file_name).read()
    else:
        return open(file_name).read()


def readFileLines(file_name: str) -> List[str]:
    if file_name.endswith('.gz'):
        try:
            return [ii.decode('utf-8') for ii in  gzip.open(file_name).readlines()]
        except gzip.BadGzipFile:
            return open(file_name).readlines()
    else:
        return open(file_name).readlines()
