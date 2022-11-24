from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass
from .compiledRe import CompiledRe
from .libertyCell import LibertyCell
from utils import Print, readFile, ConcurrentProcess


class LibertyParser:

    def __init__(self, lib_files: List[str]):
        self.macro_dict: Dict[str, LibertyCell] = {}
        self.lib_files = lib_files
        with ConcurrentProcess.MP_POOL(ConcurrentProcess.PROCESS_CNT) as pool:
            for macros in pool.map(self.extractMacroInfo, self.lib_files):
                self.macro_dict.update(macros)

    def getMacros(self) -> Dict[str, LibertyCell]:
        return self.macro_dict

    def extractMacroInfo(self, lib_file: str) -> Dict[str, LibertyCell]:
        Print(f'Parsing lib file {lib_file}')
        macros = {}
        lib_lines = readFile(lib_file).split('\n')
        lib_len = len(lib_lines)
        cursor = 0
        while cursor < lib_len:
            macro_match = CompiledRe.re_cell.search(lib_lines[cursor])
            if macro_match:
                macro_name = macro_match.group(1)
                this_macro = LibertyCell(macro_name)
                l_brace = 1
                r_brace = 0
                cursor += 1
                while l_brace != r_brace:
                    if '{' in lib_lines[cursor]:
                        l_brace += 1
                    if '}' in lib_lines[cursor]:
                        r_brace += 1
                    match_area = CompiledRe.re_area.search(lib_lines[cursor])
                    if match_area:
                        this_macro.setArea(float(match_area.group(1)))
                        cursor += 1
                        continue
                    match_footprint = CompiledRe.re_footprint.search(lib_lines[cursor])
                    if match_footprint:
                        this_macro.setFootprint(match_footprint.group(1))
                        cursor += 1
                        continue
                    match_mem = CompiledRe.re_memory.search(lib_lines[cursor])
                    if match_mem:
                        this_macro.setFootprint('memory')
                        cursor += 1
                        continue
                    match_leakage = CompiledRe.re_leakage.search(lib_lines[cursor])
                    if match_leakage:
                        leakage_content = [lib_lines[cursor]]
                        while '}' not in lib_lines[cursor]:
                            cursor += 1
                            leakage_content.append(lib_lines[cursor])
                        r_brace += 1
                        leakage_content = ''.join(leakage_content)
                        value_match = CompiledRe.re_value.search(leakage_content)
                        if value_match:
                            this_macro.setLeakage(float(value_match.group(1)))
                        cursor += 1
                        continue
                    cursor += 1
                macros.update({macro_name: this_macro})
            else:
                cursor += 1
        Print(f'End Parsing lib file {lib_file}, get {len(macros)} cells information')
        return macros



