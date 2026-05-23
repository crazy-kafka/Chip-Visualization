# Photon — Chip Visualization Tool

A PyQt5 desktop application for VLSI physical design data visualization and analysis.

Photon parses industry-standard EDA formats, builds a hierarchical in-memory database of the chip design, and provides both an interactive GUI and a Python shell for exploring floorplans, netlists, timing paths, and design metrics.

## Supported Formats

| Format | Purpose |
|---|---|
| LEF (Library Exchange Format) | Technology layers + macro/cell definitions |
| DEF (Design Exchange Format) | Floorplan, placement, routing |
| Verilog netlist | Logical hierarchy and connectivity |
| SPEF (Standard Parasitic Exchange Format) | RC parasitics |
| Liberty (.lib) | Timing library (cell area, leakage, footprint) |

## Dependencies

- Python 3.9+
- PyQt5
- numpy, pandas, matplotlib
- networkx
- shapely
- pyyaml
- xlsxwriter
- gzip (standard library)

Developed on Windows 11 and deployed on Linux.

## Command-Line Interface

Start the application:

```bash
python bin/photon.py [-f <script>] [-l <logfile>] [--nolog]
```

| Argument | Description |
|---|---|
| `-f`, `--file` | Python script to execute at startup |
| `-l`, `--log` | Log file path (default: `proton.log`) |
| `--nolog` | Disable logging |

The `-f` script runs before the interactive shell starts, so it is the standard way to automate a design load.

### Interactive Shell

After startup, Photon presents an interactive Python shell (based on `code.InteractiveConsole`) with tab-completion and command history. Built-in commands:

| Command | Action |
|---|---|
| `win` | Show the GUI window (alias for `win()`) |
| `win off` | Hide the GUI window (alias for `winoff()`) |
| `history` | Print command history |
| `pwd` | Print current working directory |
| `runfile <path>` | Execute a Python script file |

On startup, `proton_command.py` is auto-loaded and provides:

```python
db = createDB()              # Create a new UiDB session
insts = extractNetlistInsts(nl_file, top_name)  # Extract leaf instances
```

### Typical Automation Script

```python
db = createDB()

# Configure input files
db.setTechLef('tech.lef')
db.setTopName('TOP')
db.setLefList(['cells.lef'])
db.setLibList(['stdcells.lib', 'mems.lib'])
db.setVerilogList(['chip.v'])

# Parse and build the database
db.initDataBase()

# Load floorplan from DEF files
db.definePartitionByDef(['floorplan.def'])

# Show the GUI
db.win()
```

## Graphical Interface

### Window Layout

```
+---------------------------------------------------+
| Menu Bar: File > Load DB / Save DB                 |
+---------------------------------------------------+
| Tool Bar                                           |
+-------------------+-------------------------------+
| Grid Map Panel    |                               |
| (checkbox list    |     Main View                  |
|  + color legend)  |     (pan/zoom chip canvas)     |
|                   |                               |
+-------------------+-------------------------------+
| Status Bar: coordinates / selected object name     |
+---------------------------------------------------+
```

### Navigation

| Action | Result |
|---|---|
| **Mouse wheel** | Zoom in/out |
| **Middle-drag** | Pan the view |
| **Right-drag** | Zoom to rectangle |
| **Left-click** | Select item (instance or wire) |
| **Left-drag** | Area select |
| **Arrow keys** | Pan by 25% of visible area |
| **R** | Reset view to full design |
| **F** | Fit view to bounding box |

### Visual Elements

- **Partitions** — grey semi-transparent polygons showing hierarchy block boundaries. Nested blocks render on top.
- **Instances** — dark blue hatched polygons for placed leaf cells.
- **Wires** — colored hatched rectangles; each manufacturing layer has a distinct color from an 18-color palette.
- **Grid Maps** — heatmap overlays (cell density, pin density, timing slack, etc.) rendered as colored pixmap overlays with a color-bar legend.
- **Selection** — highlighted with a white dashed outline; the selected object's name appears in the status bar.

### Coordinate System

The view uses a bottom-left origin (Y-axis flipped relative to screen coordinates), matching standard VLSI physical design convention. All coordinates are in microns.

## User API Reference

The `UiDB` class provides the primary API. Access it via `createDB()` in the shell.

### Database Setup

| Method | Description |
|---|---|
| `setTechLef(path)` | Set technology LEF file |
| `setLefList(paths)` | Set macro LEF file list |
| `setLibList(paths)` | Set Liberty timing library file list |
| `setVerilogList(paths)` | Set Verilog netlist file list |
| `setTopName(name)` | Set top-level module name |
| `initDataBase()` | Parse all inputs and build the in-memory database |
| `definePartitionByDef(paths)` | Load DEF floorplan and overlay physical data |

### Persistence

| Method | Description |
|---|---|
| `saveDb(dir_path)` | Serialize entire database to a directory (pickle) |
| `loadDb(dir_path)` | Restore database from a saved directory |

### Design Creation

| Method | Description |
|---|---|
| `addInst(name, cell, module, x, y, orient)` | Place a new instance |
| `addNet(name, module)` | Create a new net |
| `attachToTerm(inst, term, net, module)` | Connect an instance terminal to a net |
| `attachModulePort(inst, term, port, module)` | Connect to a module port |
| `addRoute(net, layer, from_pt, to_pt, width)` | Add a wire segment |

### View Control

| Method | Description |
|---|---|
| `win()` / `winoff()` | Show / hide the GUI window |
| `view.showInst(name)` | Show instance(s) in the view |
| `view.hideInst(name)` | Hide instance(s) |
| `view.showNet(name)` | Show net wire(s) |
| `view.hideNet(name)` | Hide net wire(s) |
| `view.selectInst(name)` | Highlight instance(s) |
| `view.selectNet(name)` | Highlight net wire(s) |
| `view.deselectAll()` | Clear all selections |
| `view.viewBox()` | Get current viewport bounding box |
| `view.zoomBox(box)` | Zoom to specified box |

### Grid Maps

Grid maps appear in the left panel as checkable entries. Click to toggle visibility.
The color bar shows a 128-color smooth gradient.

```python
map = view.createGridMap('cell_density', grid_array, grid_size=10)
map.setUpperValue(100.0)
map.setLowerValue(0.0)
map.showMap()       # auto-show (optional — user can toggle via panel checkbox)
map.hideMap()
map.savePicture('heatmap.png')
```

### IO Timing Analysis

```python
db.analyzeInterfaceInfo('block_io_info.yaml')
db.reportRegularInterfaceInfo(out_dir='regular_rpts')
db.reportFeedthroughInterfaceInfo(out_dir='ft_rpts')
```

Generates per-clock-domain and per-module-pair reports including distance, delay, and slack distribution plots.

### Netlist Analysis

```python
checker = db.checkNetLists({'block_a': 'a.v', 'block_b': 'b.v'})
checker.dumpXlsxReport('my_report')
checker.getNlInfo('block_a')       # Per-block metrics
checker.getNlBaseInfo('block_a')   # Base (non-hierarchical) metrics
checker.saveGraph('graph.pkl')     # Save hierarchy DAG to disk
```

Reports include cell counts, area, pin counts, VT type ratios, register counts, memory bits, leakage, and combinational cell statistics — both per-block and hierarchically accumulated.

### Grid Map Generation

`genGridMapArray` generates 2D numpy grid arrays from DEF placement data. Supports two modes:

**Batch mode** (default) — each block processed in parallel via `genStatGrid.py`:

```python
spec = {
    'chip_top': {'def_file': 'chip_top.def', 'mapping_file': ''},
    'core':     {'def_file': 'core.def',     'mapping_file': ''},
    'alu':      {'def_file': 'alu.def',      'mapping_file': ''},
    'adder':    {'def_file': 'adder.def',    'mapping_file': ''},
}
db.genGridMapArray('density.npy', mode='cell_density', grid_size=20,
                   spec_dict=spec, use_lsf=False)
```

**No-batch mode** — single mapping file with flatten hierarchy names, processed in-process:

```python
# Mapping file uses full hierarchy paths: u_core_0/u_alu_0/u_adder/u_buf_a 5.0
db.genGridMapArray('power.npy', mode='value_continuous', grid_size=20,
                   spec_dict={'chip_top': {'def_file': 'chip_top.def',
                                           'mapping_file': 'power_map.txt'}},
                   no_batch=True)
```

Parameters:

| Parameter | Default | Description |
|---|---|---|
| `mode` | (required) | `cell_density`, `pin_density`, `value_continuous`, `discrete`, `discrete_max`, `discrete_mean`, `density_continuous` |
| `grid_size` | (required) | Grid cell size in microns |
| `spec_dict` | (required) | Block name → `{def_file, mapping_file}` mappings |
| `use_lsf` | `True` | Use LSF batch scheduler; `False` for local multiprocess |
| `lsf_cmd` | `None` | Custom LSF command (default: `bsub -q me_pd ...`) |
| `no_batch` | `False` | Process all blocks recursively with flatten-name mapping |

### Geometry Utilities

```python
db.dumpBlockGlobalLocalBoxMapping('block_name', 'out.txt', mode='max', grid_size=10)
db.dumpGridOffsetFile('block_name', 'out.txt')
```

### Database Properties (read-only)

| Property | Type | Description |
|---|---|---|
| `db.chip` | `DbChip` | Top-level chip container |
| `db.cells` | `Dict[str, DbMacro]` | All macro/cell definitions |
| `db.layers` | `Dict[str, TechLayer]` | All technology layers |
| `db.selected` | `List` | Currently selected objects |

## Project Structure

```
photon/
├── bin/              Entry-point scripts (photon.py, genStatGrid.py)
├── dataBase/         Core in-memory data model (DbChip, DbHInst, DbNet, etc.)
├── DEF/              DEF file parser (floorplan, placement, routing)
├── gui/              PyQt5 GUI (MainWindow, MainView, Workspace, scene items)
├── ioTiming/         IO timing path analysis and reporting
├── LEF/              LEF file parser (technology + macro)
├── nlChecker/        Netlist composition analysis and Excel reporting
├── shell/            Interactive Python shell with command history
├── spef/             SPEF parasitics parser
├── tcl_scripts/      TCL helper scripts for Innovus and PrimeTime
├── test/             Test files
├── timingLib/        Liberty (.lib) timing library parser
├── ui/               UI command handlers (UiDB, UiView, UiGridMap)
├── utils/            Utilities (coordinate transforms, logging, parallelism)
└── verilog/          Verilog netlist parser
```

## Architecture

```
User Script / Shell
       │
       ▼
     UiDB  ──────────────────────────────────────┐
       │                                         │
       ├── DbDataBase (parse, build, query)      │
       │    ├── LEF/LIB parsers → DbMacro        │
       │    ├── Verilog parser → DbHInst tree    │
       │    ├── DEF parser → physical overlay    │
       │    └── SPEF parser → RC networks        │
       │                                         │
       ├── MainWindow (GUI)                      │
       │    └── Workspace                        │
       │         ├── GridMapPanel                │
       │         └── MainView (scene)            │
       │              ├── InstItem (polygons)     │
       │              ├── WireItem (rects)        │
       │              └── GridPixMapItem (pixmap) │
       │                                         │
       ├── IOChecker (timing analysis)           │
       └── NlChecker (netlist analysis)          │
```

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run full test suite (GUI tests require offscreen mode on Linux/headless)
set QT_QPA_PLATFORM=offscreen && python -m pytest test/ -v

# Run specific test groups
python -m pytest test/test_utils.py -v        # Utility functions
python -m pytest test/test_parsers.py -v      # EDA format parsers
python -m pytest test/test_dataBase.py -v     # Data model
python -m pytest test/test_integration.py -v  # Integration tests
python -m pytest test/test_gui.py -v          # GUI components
python -m pytest test/test_e2e_gui.py -v      # End-to-end GUI
```

### Test Structure

```
test/
├── conftest.py              Shared fixtures (parsers, DbDataBase)
├── pytest.ini               Pytest config
├── data/                    Synthetic EDA test data
│   ├── tech.lef             Technology LEF (M1, M2, M3 layers)
│   ├── cells.lef            Macro LEF (BUFX2, DFF, NAND2, INV, NOR2, MUX2)
│   ├── cells.lib            Liberty timing library (6 cells)
│   ├── chip_top.v / core.v / alu.v / adder.v   Verilog (4-level hierarchy)
│   ├── chip_top.def / core.def / alu.def / adder.def   DEF floorplans
│   ├── top.v / sub.v / top.def / sub.def       Legacy 2-level test data
│   └── test.spef            SPEF parasitics
├── scripts/                 Test scripts for photon.py -f
│   ├── test_gui_interactive.py    Full 4-level hierarchy + 5 grid maps
│   ├── test_gui_startup.py       DB init + GUI launch + exit
│   └── test_heatmap_colors.py    Verify 128-color heatmap gradient
├── test_utils.py            57 tests — Orient, CoordinateProcess, PathOperation, shapeProcess
├── test_parsers.py          58 tests — TlefParser, LefParser, DefParser, VerilogParser, SPEF, Liberty
├── test_dataBase.py         28 tests — DbDataBase, DbChip, DbHInst, DbNet, DbWire, DbGridMap
├── test_integration.py      9 tests — Full parse→DB→DEF overlay→save/load flow
├── test_gui.py              49 tests — MainWindow, MainView, InstItem, WireItem, Point
├── test_genGridMap.py       9 tests — genStatGrid batch + no_batch, all grid modes
└── test_e2e_gui.py          2 tests — photon.py -f subprocess startup
```

### End-to-End GUI Test

Run a test script through the full photon startup path:

```bash
set QT_QPA_PLATFORM=offscreen && python bin/photon.py -f test/scripts/test_gui_startup.py --nolog
```

The script initializes a database from test data, loads DEF floorplans, shows the GUI,
prints `GUI_STARTUP_OK`, and exits cleanly.

### Test Coverage Summary

220 tests total across 7 test files.

| Test File | Tests | Coverage |
|---|---|---|
| `test_utils.py` | 62 | Orient (16), CoordinateProcess (17), PathOperation (12), shapeProcess (5), readFile (2), PSTATUS (1) |
| `test_parsers.py` | 58 | TlefParser, LefParser, DefParser, VerilogParser, InstExtractor, SpefParser, LibertyParser |
| `test_dataBase.py` | 28 | DbDataBase init/add/save, DbChip, DbHInst, DbNet/DbWire, DbGridMap |
| `test_integration.py` | 9 | Full parse flow, DEF overlay, save/load, manual design |
| `test_gui.py` | 49 | Point, MainWindow, MainView, InstItem, WireItem, GridPixMapItem, GenericGraphicsView |
| `test_genGridMap.py` | 9 | genStatGrid batch (5), no_batch (4): cell_density, pin_density, value_continuous, discrete |
| `test_e2e_gui.py` | 2 | photon.py -f subprocess startup + heatmap color count |

### Notes

- **GUI tests** require a display or `QT_QPA_PLATFORM=offscreen` on headless systems
- **Interactive GUI test** launches the full 4-level hierarchy with 5 grid maps (batch/no-batch cell density + power density):
  ```bash
  set QT_QPA_PLATFORM=offscreen && python bin/photon.py -f test/scripts/test_gui_interactive.py --nolog
  ```
- **Test data** is synthetic and self-contained; the 4-level hierarchy (chip_top → core → alu → adder)
  has 36 hInst partitions, 6 cell types, and only legal orientations (N/S/FN/FS; no R=90/270)
- **Heatmap** uses a 128-color smooth gradient (white→red→orange→yellow→green→cyan→blue→black)
- Legacy test files `test/lef_test.py` and `test/verilog_test.py` from the original project are preserved

## License

This project is distributed under the terms specified in the LICENSE file.
