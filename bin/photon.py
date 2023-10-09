from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass


import os
import sys
import argparse
from PyQt5 import QtWidgets
import pydoc
pydoc.pager = pydoc.plainpager
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
from shell import Shell
from utils import logInitialize


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description=f'XXX - Chip Visualization Tool by Hongji.Liu')
    arg_parser.add_argument('-f', '--file', type=str, default='', help='The initial file executed at the beginning of program')
    arg_parser.add_argument('-l', '--log', type=str, default='', help='log file for proton')
    arg_parser.add_argument('--nolog', action='store_true', help='no log')

    args = arg_parser.parse_args()

    App = QtWidgets.QApplication(sys.argv)

    if not args.nolog:
        logInitialize(args.log)

    init_file = args.file

    __console = Shell(scope=locals())
    if init_file:
        __console.runfile(init_file)
    __console.loopStart()









