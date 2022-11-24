from __future__ import annotations

import re
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

import code
import os
import sys
import rlcompleter
import readline
import logging
from utils import Print, GlobalVariable

readline.parse_and_bind('tab: complete')


class Shell(code.InteractiveConsole):

    INIT = 'import sys, os;print("Python", sys.version);sys.ps1="\x01\x1b[1;49;33m\x02>>>\x01\x1b[0m\x02 ";sys.ps="\x01\x1b[1;49;31m\x02...\x01\x1b[0m\x02 ";'
    BUILDIN_CMDs = [f'{os.path.dirname(__file__)}/proton_command.py']
    BANNER = '\nWelcome to XXX Shell :)'
    EXITMSG = 'Now exiting XXX...'

    def __init__(self, scope=None, init_file: str=''):
        super().__init__(locals=scope)
        self.__histories = []
        self.runsource(self.INIT)
        for CMD in self.BUILDIN_CMDs:
            self.runsource(f'exec(open("{CMD}").read()')
        Print(GlobalVariable.BANNER)

    def runfile(self, input_file):
        if isinstance(input_file, str):
            with open(input_file, 'r') as fh:
                flag = True
                while flag:
                    line = fh.readline()
                    if (not line.startswith(' ') or not line) and line != '\n':
                        self.push('')
                    elif line.lstrip(' ') == '\n':
                        continue
                    if not line:
                        break
                    self.push(line.rstrip('\n'))
        elif isinstance(input_file, list) or isinstance(input_file, set) or isinstance(input_file, tuple):
            for ii in input_file:
                self.runfile(ii)

    def runstr(self, input_str: str):
        for line in input_str.split('\n'):
            self.push(line)

    def loopStart(self):
        self.interact(banner=self.BANNER, exitmsg=self.EXITMSG)

    def write(self, data: str) -> None:
        if 'Traceback' in data:
            Print('\n' + data, level='error')
        elif 'Error' in data:
            Print(data)
        elif self.EXITMSG in data:
            Print('\n' + data)
        elif self.BANNER in data:
            print(data)

    def push(self, line: str):
        if line:
            self.__histories.append(line)

        if line == 'win':
            line += '()'
        elif line == 'win off':
            line = 'winoff()'
        elif line.strip('\n') == 'history':
            line = 'pass'
            for idx, his in enumerate(self.__histories):
                print(f'  {idx}. {his}')
        elif line.strip(' ') == 'pwd':
            line = f'os.getcwd()'
        elif line.strip(' ').startswith(f'runfile '):
            runfile = re.search(r'\s*runfile\s*([^\s]+)', line).group(1)
            self.runfile(runfile)
            return super().push('pass')
        elif line.rstrip(' ').startswith(f'runfile('):
            self.runsource(line)
            return super().push('pass')
        self.__recordInLog(line)

        return super().push(line)

    @staticmethod
    def __recordInLog(line: str):
        if line and line != 'pass':
            GlobalVariable.CMD_LOGGER.info(line)
            GlobalVariable.BASE_LOGGER.info(f'<cmd> {line}')





