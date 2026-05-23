from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from utils import Print
import  re


class CompileRe:
    __NAME__ = r'[_a-zA-Z0-9/\\]+'
    __INTEGER__ = r'[0-9]+'
    __BINARY__ = r'[0-9]+\'b[01]+'

    re_spef = re.compile(rf'\*SPEF\s+(?P<SPEF>\S+)')
    re_design = re.compile(rf'\*DESIGN\s+(?P<DESIGN>\S+)')
    re_DATE = re.compile(rf'\*DESIGN\s+(?P<DATE>\S+)')

    NAME_MAP_FLAG = '*NAME_MAP'
    re_map = re.compile(rf'\*(?P<id>{__INTEGER__})\s+(?P<name>{__NAME__})')

    PORTS_FLAG = '*PORTS'
    re_port = re.compile(rf'(?P<idx>\S+)\s+(?P<direction>\S+)')
    COMMENT = '//'

    re_NET = re.compile(rf'\*D_NET\s+(?P<id>\S+)\s+(?P<total_cap>\S+)')
    CONN_flag = '*CONN'
    re_conn = re.compile(rf'\*(?P<pt_type>[IP])\s+(?P<name>\S+)\s+(?P<direction>[IOB])\s+\*C\s+(?P<x>\S+)\s+(?P<y>\S+)(?:\*D\s+(?P<ref_name>\S+))?')
    CAP_flag = '*CAP'
    re_cap = re.compile(rf'\d+\s+(?P<node>\S+)(?:\s+(?P<couple_node>\S+))?\s+(?P<value>\S+)')
    RES_flag = '*RES'
    re_res = re.compile(rf'\d+\s+(?P<node_0>\S+)\s+(?P<node_1>\S+)\s+(?P<value>\S+)')
    END_FLAG = '*END'



