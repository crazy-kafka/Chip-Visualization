from __future__ import annotations
from typing import List, Tuple, Dict, Union, Iterable, TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    pass

from .module import Module
from .compileRe import CompiledRe
from utils import readFile, Print
import time

class VerilogParser:

    def __init__(self, verilog_file: str):
        self.__modules: Dict[str, Module] = {}
        self.verilog_file = verilog_file
        self.parseStart()

    def parseStart(self):
        t0 = time.time()
        Print(f'Start parsing verilog file {self.verilog_file}')
        content = readFile(self.verilog_file).replace('\n', '').replace('\t', '')
        module_str_list = CompiledRe.re_module.findall(content)
        module_str_list.sort(key=lambda x:len(x), reverse=True)

        for module in map(self.parseModule, module_str_list):
            self.__modules[module.name] = module

        Print(f'End parsing of {self.verilog_file} in {round(time.time() - t0, 3)}s')

    @staticmethod
    def parseModule(module_string: str) -> Module:
        return Module(module_string)

    def module(self, module_name: str) -> Module:
        return self.__modules[module_name]

    def allModules(self) -> Dict[str, Module]:
        return self.__modules

    def __repr__(self):
        return f'Verilog parser for file: {self.verilog_file}\nTotal {len(self.__modules)} module(s) parsed.'
