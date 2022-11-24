from __future__ import annotations

import re
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass


class CompiledRe:

    re_cell = re.compile(r'cell\s+\(\s*([^\)\s]+)\s*\)\s+{')
    re_area = re.compile(r'area\s*:\s*([0-9]+(\.[0-9]+)?)\s*')
    re_footprint = re.compile(r'cell_footprint\s*:\s*"([^""]+)"\s*;')
    re_memory = re.compile(r'\s*memory\s*\(\)\s*{')
    re_leakage = re.compile(r'leakage_power\s*\(\)\s*{')
    re_value = re.compile(r'value\s*:\s*([0-9]+(\.[0-9]+)?)]\s*;')
