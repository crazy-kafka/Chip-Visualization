import os, sys
sys.path.append(os.path.abspath(os.path.realpath(os.path.dirname(__file__) + '/../')))
from verilog import VerilogParser, InstExtractor

ext = InstExtractor(os.path.dirname(__file__) + '\\test.v', 'test_module')
print(ext.insts)

