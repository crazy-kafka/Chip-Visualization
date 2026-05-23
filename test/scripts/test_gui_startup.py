import sys
import os

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from ui import UiDB
def createDB():
    return UiDB()

D = 'test/data'

db = createDB()
db.setTechLef(D + '/tech.lef')
db.setTopName('chip_top')
db.setLefList([D + '/cells.lef'])
db.setLibList([D + '/cells.lib'])
db.setVerilogList([D + '/chip_top.v', D + '/core.v', D + '/alu.v', D + '/adder.v'])
db.initDataBase()

assert db.chip is not None, 'Chip not created'
assert len(db.layers) == 3, 'Expected 3 layers, got %d' % len(db.layers)
assert len(db.cells) == 6, 'Expected 6 cells, got %d' % len(db.cells)
assert len(db.chip.nets) > 0, 'No nets created'

db.definePartitionByDef([D + '/chip_top.def', D + '/core.def', D + '/alu.def', D + '/adder.def'])
db.win()

tree = db.chip.hInst.treeHInsts
ptn_count = sum(1 for h in tree.values() if h.is_ptn)
assert ptn_count >= 5, 'Expected >= 5 partitions, got %d' % ptn_count

print('GUI_STARTUP_OK')
sys.exit(0)
