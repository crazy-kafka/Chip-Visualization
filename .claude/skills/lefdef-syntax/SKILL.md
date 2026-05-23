---
name: lefdef-syntax
description: LEF/DEF 5.8 syntax reference for creating, editing, or parsing LEF and DEF files. Use when working with .lef or .def files, the LEF/DEF parsers, or creating test fixture data.
user-invocable: true
tools: Read, Glob, Grep
---

# LEF/DEF 5.8 Syntax

Reference for creating valid LEF/DEF files that work with this project's parsers (`LEF/`, `DEF/`).
For the complete specification, see `eda_doc/lefdefref.md`.

## General Rules (Both Formats)

- Distance in microns; DEF coordinates divided by `UNITS DISTANCE MICRONS` value
- Statements end with `;` — space required before `;`
- Keywords case-insensitive; shown UPPERCASE by convention
- Hierarchy divider default: `/` ; bus bit delimiters default: `[]`
- Identifiers (names): max 2,048 characters

---

## LEF — Library Exchange Format

### Technology LEF (layer definitions, vias, rules)

```
LAYER layerName
  TYPE ROUTING ;
  DIRECTION {HORIZONTAL | VERTICAL} ;
  PITCH xDistance yDistance ;
  WIDTH defaultWidth ;
  [SPACING minSpacing ;]
  [AREA minArea ;]
END layerName
```

- Only `TYPE ROUTING` layers get sequential `idx` values assigned by the parser
- `TYPE CUT`, `TYPE MASTERSLICE`, `TYPE OVERLAP` get `idx=0`

```
VIA viaName [DEFAULT]
  LAYER layerName ; RECT x1 y1 x2 y2 ;
  LAYER layerName ; RECT x1 y1 x2 y2 ;
END viaName

SITE siteName
  SIZE width BY height ;
  [CLASS {PAD | CORE} ;]
END siteName
```

### Macro LEF (cell definitions)

```
MACRO macroName
  CLASS {CORE | PAD | BLOCK | COVER | RING | ENDCAP} ;
  SIZE width BY height ;
  [SYMMETRY {X | Y | R90} ... ;]
  [SITE siteName ;]
  [FOREIGN foreignCellName pt [orient] ;]

  PIN pinName
    DIRECTION {INPUT | OUTPUT [TRISTATE] | INOUT | FEEDTHRU} ;
    USE {SIGNAL | ANALOG | POWER | GROUND | CLOCK} ;
    [SHAPE {ABUTMENT | RING | FEEDTHRU} ;]
    PORT
      [CLASS {NONE | CORE | BUMP} ;]
      LAYER layerName ;
        RECT x1 y1 x2 y2 ;
    END
  END pinName

  [OBS
    LAYER layerName ;
      RECT x1 y1 x2 y2 ;
  END]
END macroName
```

**Important parser behavior:**
- `USE POWER` or `USE GROUND` pins get direction forced to `INOUT` and count as inout pins
- Pins with `USE SIGNAL` and `DIRECTION INPUT` → input count; `DIRECTION OUTPUT` → output count

### Minimal Cell Example
```
MACRO BUFX2
  CLASS CORE ;
  SIZE 0.5 BY 1.0 ;
  PIN A
    DIRECTION INPUT ;
    USE SIGNAL ;
    LAYER M1 ;
      RECT 0.0 0.3 0.1 0.7 ;
  END A
  PIN Y
    DIRECTION OUTPUT ;
    USE SIGNAL ;
    LAYER M1 ;
      RECT 0.4 0.3 0.5 0.7 ;
  END Y
  PIN VDD
    DIRECTION INOUT ;
    USE POWER ;
    LAYER M1 ;
      RECT 0.1 0.0 0.4 0.2 ;
  END VDD
  PIN VSS
    DIRECTION INOUT ;
    USE GROUND ;
    LAYER M1 ;
      RECT 0.1 0.8 0.4 1.0 ;
  END VSS
END BUFX2
```

---

## DEF — Design Exchange Format

### Design Header
```
DESIGN designName ;
UNITS DISTANCE MICRONS db_unit ;
DIEAREA ( x0 y0 ) ( x0 y1 ) ( x1 y1 ) ( x1 y0 ) ;
```

### COMPONENTS
```
COMPONENTS numComps ;
  - compName modelName
    + SOURCE {NETLIST | DIST | USER | TIMING}
    + {FIXED | COVER | PLACED | UNPLACED} ( x y ) orient
  ; ...
END COMPONENTS
```
- `modelName` must match a LEF MACRO name
- orient: `N | S | W | E | FN | FS | FW | FE`

### PINS
```
PINS numPins ;
  - pinName + NET netName
    + DIRECTION {INPUT | OUTPUT | INOUT}
    + USE {SIGNAL | POWER | GROUND | CLOCK}
    + LAYER layerName ( x0 y0 ) ( x1 y1 )
    + PLACED ( x y ) orient
  ; ...
END PINS
```
**Known parser bug:** Pins only parse when `;` is NOT on the same line as the pin definition (multi-line format). For single-line pins with trailing `;`, use a `;` on its own line after the pin body.

### NETS (regular wiring)
```
NETS numNets ;
  - netName
    ( {compName pinName | PIN pinName} ) ...
    + ROUTED layerName ( x0 y0 [e0] ) ( x1 y1 [e1] ) ...
      [NEW layerName ( x0 y0 ) ...] ...
  ; ...
END NETS
```
- `*` replaces coordinates to indicate continuity from the previous point
- `+ ROUTED` starts a new routing path; `NEW` starts on a new layer within the same path

### SPECIALNETS
```
SPECIALNETS numNets ;
  - netName
    ( compName pinName ) ...
    + layerName width ( x0 y0 [e0] ) ( x1 y1 [e1] ) [viaName] ...
  ; ...
END SPECIALNETS
```
- Width is required in special wiring (not present in regular wiring)

### TRACKS
```
TRACKS {X | Y} offset DO numTracks STEP step LAYER layerName ... ;
```

### BLOCKAGES
```
BLOCKAGES numBlockages ;
  - LAYER layerName
    [+ PLACEMENT | + ROUTING]
    RECT ( x0 y0 ) ( x1 y1 ) ; ...
  ; ...
END BLOCKAGES
```

### Minimal DEF Example
```
DESIGN top ;
UNITS DISTANCE MICRONS 2000 ;
DIEAREA ( 0 0 ) ( 0 100000 ) ( 100000 100000 ) ( 100000 0 ) ;
COMPONENTS 2 ;
  - u_sub sub + PLACED ( 20000 20000 ) N ;
  - u_buf BUFX2 + PLACED ( 70000 70000 ) N ;
END COMPONENTS
PINS 2 ;
  - clk + NET clk + DIRECTION INPUT + USE SIGNAL + LAYER M1 ( 0 50000 ) ( 5000 50000 ) + PLACED ( 0 50000 ) N ;
  - out + NET out + DIRECTION OUTPUT + USE SIGNAL + LAYER M1 ( 100000 50000 ) ( 95000 50000 ) + PLACED ( 100000 50000 ) N ;
END PINS
NETS 2 ;
  - net_clk
    ( PIN clk ) ( u_sub/clk )
    + ROUTED M1 ( 5000 50000 ) ( 20000 45000 )
  ;
END NETS
END DESIGN
```

### Project-Specific DEF Parser Flags

The project's `DefParser` supports optional flags:
```python
DefParser(def_file, skip_comp=False, parse_pin=False, parse_net=False,
          parse_blockage=False, parse_specialnet=False, batch_mode=False)
```
- `skip_comp=True` — skip component parsing (used for top-level DEF with hierarchy)
- `parse_pin=True` — enable pin parsing (off by default)
- `parse_net=True` — enable net/wiring parsing (off by default)

---

## Orientation Reference

| DEF | OA   | Rotation | Mirror X | Mirror Y | Notes |
|-----|------|----------|----------|----------|-------|
| N   | R0   | 0°       | No       | No       | Default, no transform |
| S   | R180 | 180°     | No       | No       | Rotate 180° |
| W   | R90  | 90°      | No       | No       | Rotate 90° counter-clockwise |
| E   | R270 | 270°     | No       | No       | Rotate 270° counter-clockwise |
| FN  | MY   | 0°       | No       | Yes      | Mirror Y |
| FS  | MX   | 0°       | Yes      | No       | Mirror X |
| FW  | MX90 | 90°      | Yes      | No       | Mirror X + Rotate 90° |
| FE  | MY90 | 90°      | No       | Yes      | Mirror Y + Rotate 90° |

Defined in `utils/coordinateProcess.py` → `Orient.orient_map` with `DEF_OA_map` / `OA_DEF_map` for conversion.

---

## Project Parser Quick Reference

| Directory | Parser Class | Input | Output |
|-----------|-------------|-------|--------|
| `LEF/` | `TlefParser` | Tech LEF file | `Dict[str, LefLayer]` |
| `LEF/` | `LefParser` | Macro LEF files list | `Dict[str, LefMacro]` |
| `DEF/` | `DefParser` | DEF file + flags | components, pins, nets, die area |
| `verilog/` | `VerilogParser` | .v file | `Dict[str, Module]` |
| `spef/` | `SpefParser` | .spef file | `Dict[str, SpefNet]` (NetworkX DiGraph) |
| `timingLib/` | `LibertyParser` | .lib files list | `Dict[str, LibertyCell]` |

For full syntax reference, read `eda_doc/lefdefref.md`.
