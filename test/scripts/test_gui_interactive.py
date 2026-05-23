import sys, os, numpy as np
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from ui import UiDB
def createDB():
    return UiDB()

# Isolate all generated files in test/workdir/
os.makedirs('test/workdir', exist_ok=True)
os.chdir('test/workdir')
D = '../data'

db = createDB()
db.setTechLef(D + '/tech.lef')
db.setTopName('chip_top')
db.setLefList([D + '/cells.lef'])
db.setLibList([D + '/cells.lib'])
db.setVerilogList([D + '/chip_top.v', D + '/core.v', D + '/alu.v', D + '/adder.v'])
db.initDataBase()
db.definePartitionByDef([D + '/chip_top.def', D + '/core.def', D + '/alu.def', D + '/adder.def'])

tree = db.chip.hInst.treeHInsts
max_depth = max((h.name.count('/') for h in tree.values()), default=0)
ptn_count = sum(1 for h in tree.values() if h.is_ptn)
orients_used = set(h.ptn_orient for h in tree.values() if h.is_ptn)
print('=' * 72)
print('MULTI-HIERARCHY GUI TEST - 4-level design')
print('Cells: %d - %s' % (len(db.cells), list(db.cells.keys())))
print('Layers: %d - %s' % (len(db.layers), list(db.layers.keys())))
print('Nets: %d' % len(db.chip.nets))
print('Hierarchy: %d levels, %d hInsts, %d partitions' % (max_depth + 1, len(tree), ptn_count))
print('Orientations: %s (%d of 8)' % (sorted(orients_used), len(orients_used)))
print()

print('Partition tree (* = with physical shape):')
for name in sorted(tree, key=lambda x: x.count('/')):
    h = tree[name]
    depth = name.count('/')
    indent = '  ' * depth
    ptn = '*' if h.is_ptn else ' '
    short = name.split('/')[-1] if name else '(chip_top)'
    print('%s[%s] %-24s cell=%-8s orient=%-4s origin=(%d,%d) area=%d' %
          (indent, ptn, short, h.cell, h.ptn_orient,
           int(h.origin_x), int(h.origin_y), int(h.area)))

print()
print('Working dir: %s' % os.path.abspath('.'))
print('=' * 72)

db.win()

spec = {
    'chip_top': {'def_file': os.path.abspath(D + '/chip_top.def'), 'mapping_file': ''},
    'core':     {'def_file': os.path.abspath(D + '/core.def'),     'mapping_file': ''},
    'alu':      {'def_file': os.path.abspath(D + '/alu.def'),      'mapping_file': ''},
    'adder':    {'def_file': os.path.abspath(D + '/adder.def'),    'mapping_file': ''},
}

# --- 1. cell_density (batch) ---
db.genGridMapArray('batch_cell.npy', mode='cell_density', grid_size=20,
                   spec_dict=spec, use_lsf=False)
npy_path = os.path.join('genGridArray', 'batch_cell.npy')
grid_file = npy_path if os.path.exists(npy_path) else 'batch_cell.npy'
if os.path.exists(grid_file):
    grid = np.load(grid_file)
    db.view.createGridMap('cell_density (batch)', grid, grid_size=20)
    print('GridMap "cell_density (batch)" shape=%s max=%.3f'
          % (grid.shape, np.nanmax(grid)))

# --- 2. cell_density (no_batch) ---
db.genGridMapArray('nb_cell.npy', mode='cell_density', grid_size=20,
                   spec_dict=spec, no_batch=True)
if os.path.exists('nb_cell.npy'):
    grid = np.load('nb_cell.npy')
    db.view.createGridMap('cell_density (no_batch)', grid, grid_size=20)
    print('GridMap "cell_density (no_batch)" shape=%s max=%.3f'
          % (grid.shape, np.nanmax(grid)))

# --- 3. power_density (batch) - local names in adder block ---
adder_power = os.path.abspath('adder_power.txt')
with open(adder_power, 'w') as f:
    f.write('u_buf_a 5.0\n')
    f.write('u_buf_b 3.0\n')
    f.write('u_buf_c 2.0\n')
    f.write('u_dff_a 8.0\n')
    f.write('u_inv_a 1.0\n')
    f.write('u_inv_b 1.5\n')
    f.write('u_nand_a 2.5\n')
    f.write('u_nand_b 2.0\n')
    f.write('u_mux_a 6.0\n')
    f.write('u_nor_a 1.8\n')
db.genGridMapArray('batch_power.npy', mode='value_continuous', grid_size=20,
                   spec_dict={'adder': {'def_file': os.path.abspath(D + '/adder.def'),
                                        'mapping_file': adder_power}},
                   use_lsf=False)
npy_path = os.path.join('genGridArray', 'batch_power.npy')
grid_file = npy_path if os.path.exists(npy_path) else 'batch_power.npy'
if os.path.exists(grid_file):
    grid = np.load(grid_file)
    if not np.all(np.isnan(grid)):
        db.view.createGridMap('power_density (batch)', grid, grid_size=20)
        print('GridMap "power_density (batch)" shape=%s max=%.3f'
              % (grid.shape, np.nanmax(grid)))
    else:
        print('WARNING: batch_power grid is all NaN, skipping GridMap')

# --- 4. power_density (no_batch) - flatten names ---
nb_power = os.path.abspath('nb_power_map.txt')
with open(nb_power, 'w') as f:
    f.write('u_core_0/u_alu_0/u_adder/u_buf_a 5.0\n')
    f.write('u_core_0/u_alu_0/u_adder/u_buf_b 3.0\n')
    f.write('u_core_0/u_alu_0/u_adder/u_dff_a 8.0\n')
    f.write('u_core_0/u_alu_0/u_adder/u_inv_a 1.0\n')
    f.write('u_core_0/u_alu_0/u_adder/u_mux_a 6.0\n')
    f.write('u_core_1/u_alu_1/u_adder/u_buf_a 4.0\n')
    f.write('u_core_1/u_alu_1/u_adder/u_nand_a 2.5\n')
    f.write('u_core_2/u_alu_2/u_adder/u_nor_a 1.8\n')
    f.write('u_core_3/u_alu_3/u_adder/u_buf_c 2.0\n')
    f.write('u_buf_top 10.0\n')
db.genGridMapArray('nb_power.npy', mode='value_continuous', grid_size=20,
                   spec_dict={
                       'chip_top': {'def_file': os.path.abspath(D + '/chip_top.def'), 'mapping_file': nb_power},
                       'core':     {'def_file': os.path.abspath(D + '/core.def'),     'mapping_file': ''},
                       'alu':      {'def_file': os.path.abspath(D + '/alu.def'),      'mapping_file': ''},
                       'adder':    {'def_file': os.path.abspath(D + '/adder.def'),    'mapping_file': ''},
                   },
                   no_batch=True)
if os.path.exists('nb_power.npy'):
    grid = np.load('nb_power.npy')
    db.view.createGridMap('power_density (no_batch)', grid, grid_size=20)
    print('GridMap "power_density (no_batch)" shape=%s max=%.3f'
          % (grid.shape, np.nanmax(grid)))

# --- 5. Synthetic gradient ramp ---
ramp = np.tile(np.linspace(0, 1, 50), (20, 1))
db.view.createGridMap('gradient_ramp', ramp, grid_size=20)

print('5 grid maps ready. Check left panel to toggle.')
print('GUI ready. Commands: win / win off')
