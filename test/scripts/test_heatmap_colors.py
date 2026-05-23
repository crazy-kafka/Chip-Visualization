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
db.win()

from gui.mainView import MainView
count = len(MainView.HEATMAP_COLORS)
assert count == 128, 'Expected 128 colors, got %d' % count
print('HEATMAP_COLORS_OK')
sys.exit(0)
