# LEF/DEF 5.8 Syntax Reference

Based on Cadence LEF/DEF 5.8 Language Reference, January 2023.
Summarized for this project's parser usage.

---

## LEF (Library Exchange Format)

### General Rules
- Identifiers (net names, cell names) limited to 2,048 characters
- Distance in microns, precision controlled by `UNITS` statement
- Statements end with semicolon (`;`) — space required between last character and `;`
- Keywords are case-insensitive
- LEF files split into **technology LEF** (layers, vias, design rules) and **cell library LEF** (macros, standard cells)

### Statement Order
```
[VERSION]
[BUSBITCHARS]
[DIVIDERCHAR]
[UNITS]
[MANUFACTURINGGRID]
[USEMINSPACING]
[CLEARANCEMEASURE]
[PROPERTYDEFINITIONS]
[FIXEDMASK]
[LAYER (Routing/Nonrouting)] ...
[MAXVIASTACK]
[VIARULE GENERATE] ...
[VIA] ...
[VIARULE] ...
[NONDEFAULTRULE] ...
[SITE] ...
[MACRO [PIN ...] [OBS ...]] ...
[BEGINEXT] ...
[END LIBRARY]
```

### Technology LEF Statements

#### UNITS
```
UNITS
  DATABASE MICRONS db_unit ;
END UNITS
```
Controls distance precision. All coordinates are divided by `db_unit` to get micron values.

#### MANUFACTURINGGRID
```
MANUFACTURINGGRID value ;
```
Specifies the manufacturing grid resolution in microns.

#### BUSBITCHARS
```
BUSBITCHARS "[]" ;
```
Character pair for bus bit delimiters. Default: `"[]"`.

#### DIVIDERCHAR
```
DIVIDERCHAR "/" ;
```
Character for hierarchy delimiter. Default: `"/"`.

#### CLEARANCEMEASURE
```
CLEARANCEMEASURE {MAXXY | EUCLIDEAN} ;
```
Default: `EUCLIDEAN`. Controls spacing measurement method.

### Layer (Routing) — `LAYER layerName ... END layerName`

```
LAYER layerName
  TYPE ROUTING ;
  [MASK maskNum ;]
  DIRECTION {HORIZONTAL | VERTICAL | DIAG45 | DIAG135} ;
  PITCH {distance | xDistance yDistance} ;
  [DIAGPITCH {distance | diag45Distance diag135Distance} ;]
  WIDTH defaultWidth ;
  [OFFSET {distance | xDistance yDistance} ;]
  [DIAGWIDTH diagWidth ;]
  [DIAGSPACING diagSpacing ;]
  [DIAGMINEDGELENGTH diagLength ;]
  [AREA minArea ;]
  [MINSIZE minWidth minLength [minWidth2 minLength2] ... ;]
  [SPACING minSpacing
    [RANGE minWidth maxWidth
      [USELENGTHTHRESHOLD | INFLUENCE value | RANGE minWidth maxWidth]
    | LENGTHTHRESHOLD maxLength
    | ENDOFLINE eolWidth WITHIN eolWithin [PARALLELEDGE ...]
    | SAMENET [PGONLY]
    | NOTCHLENGTH minNotchLength ...]
  ;] ...
  [SPACINGTABLE ... ;]
  [WIREEXTENSION value ;]
  [MINIMUMCUT numCuts WIDTH width ... ;] ...
  [MAXWIDTH width ;]
  [MINWIDTH width ;]
  [MINSTEP minStepLength ... ;]
  [MINENCLOSEDAREA area [WIDTH width] ;] ...
  [PROTRUSIONWIDTH width1 LENGTH length WIDTH width2 ;]
  [RESISTANCE RPERSQ value ;]
  [CAPACITANCE CPERSQDIST value ;]
  [HEIGHT distance ;]
  [THICKNESS distance ;]
  [SHRINKAGE distance ;]
  [CAPMULTIPLIER value ;]
  [EDGECAPACITANCE value ;]
  [MINIMUMDENSITY minDensity ;]
  [MAXIMUMDENSITY maxDensity ;]
  [DENSITYCHECKWINDOW windowLength windowWidth ;]
  [DENSITYCHECKSTEP stepValue ;]
  [FILLACTIVESPACING spacing ;]
  [ANTENNAMODEL {OXIDE1 | OXIDE2 | ... | OXIDE32} ;] ...
  [ANTENNAAREARATIO value ;] ...
  [ANTENNADIFFAREARATIO {value | PWL((d1 r1)(d2 r2)...)} ;] ...
  [ANTENNACUMAREARATIO value ;] ...
  [ANTENNACUMDIFFAREARATIO {value | PWL(...)} ;] ...
  [ANTENNAAREAFACTOR value [DIFFUSEONLY] ;] ...
  [ANTENNASIDEAREARATIO value ;] ...
  [ANTENNADIFFSIDEAREARATIO {value | PWL(...)} ;] ...
  [ANTENNACUMSIDEAREARATIO value ;] ...
  [ANTENNACUMDIFFSIDEAREARATIO {value | PWL(...)} ;] ...
  [ANTENNASIDEAREAFACTOR value [DIFFUSEONLY] ;] ...
  [ANTENNACUMROUTINGPLUSCUT ;]
  [ANTENNAGATEPLUSDIFF plusDiffFactor ;]
  [ANTENNAAREAMINUSDIFF minusDiffFactor ;]
  [ANTENNAAREADIFFREDUCEPWL ((diffArea1 diffMetalFactor1)...) ;]
  [PROPERTY propName propVal ;] ...
  [ACCURRENTDENSITY {PEAK | AVERAGE | RMS} {value | FREQUENCY ... TABLEENTRIES ...} ;]
  [DCCURRENTDENSITY AVERAGE {value | WIDTH ... TABLEENTRIES ...} ;]
  [PROPERTY LEF58_* ... ;] ...
END layerName
```

Only `TYPE ROUTING` layers are assigned sequential `idx` values by the parser.

### Layer (Cut)
```
LAYER layerName
  TYPE CUT ;
  [SPACING minSpacing ;] ...
  [WIDTH width ;]
  [ENCLOSURE {ABOVE | BELOW} overhang1 overhang2 [WIDTH ...] ;] ...
  ...
END layerName
```

### Layer (Masterslice or Overlap)
```
LAYER layerName
  TYPE {MASTERSLICE | OVERLAP} ;
  ...
END layerName
```

### VIA
```
VIA viaName
  [DEFAULT]
  [RESISTANCE value ;]
  {LAYER layerName ; RECT pt pt ;} ...
END viaName
```
Multi-layer via definition. Each `LAYER` section has a `RECT` for the via shape on that layer.

### VIARULE
```
VIARULE ruleName
  LAYER layerName ; DIRECTION {HORIZONTAL | VERTICAL} ;
  WIDTH minWidth TO maxWidth ;
  {LAYER layerName ; DIRECTION ... ; WIDTH ... TO ... ;} ...
  {VIA viaName ;} ...
END ruleName
```

### VIARULE GENERATE
```
VIARULE viaName GENERATE
  LAYER layerName ; ENCLOSURE overhang1 overhang2 ;
  {LAYER layerName ; ENCLOSURE overhang1 overhang2 ;} ...
  {LAYER cutLayerName ; RECT pt pt ; SPACING x BY y ;}
END viaName
```

### SITE
```
SITE siteName
  SIZE width BY height ;
  [CLASS {PAD | CORE} ;]
  [SYMMETRY {X | Y | R90} ... ;]
END siteName
```

### NONDEFAULTRULE
```
NONDEFAULTRULE ruleName
  [HARDSPACING ;]
  {LAYER layerName
    WIDTH width ;
    [DIAGWIDTH diagWidth ;]
    [SPACING minSpacing ;]
    [WIREEXTENSION value ;]
  END layerName} ...
  [VIA viaStatement ;] ...
  [USEVIA viaName ;] ...
  [USEVIARULE viaRuleName ;] ...
  [MINCUTS cutLayerName numCuts ;] ...
END ruleName
```

### MACRO
```
MACRO macroName
  [CLASS {COVER [BUMP] | RING | BLOCK [BLACKBOX|SOFT] | PAD [INPUT|OUTPUT|INOUT|POWER|SPACER|AREAIO]
         | CORE [FEEDTHRU|TIEHIGH|TIELOW|SPACER|ANTENNACELL|WELLTAP]
         | ENDCAP {PRE|POST|TOPLEFT|TOPRIGHT|BOTTOMLEFT|BOTTOMRIGHT}} ;]
  [FIXEDMASK ;]
  [FOREIGN foreignCellName [pt [orient]] ;] ...
  [ORIGIN pt ;]
  [EEQ macroName ;]
  [SIZE width BY height ;]
  [SYMMETRY {X | Y | R90} ... ;]
  [SITE siteName [sitePattern] ;] ...
  [PIN statement] ...
  [OBS statement] ...
  [DENSITY statement] ...
  [PROPERTY propName propVal ;] ...
END macroName
```

**CLASS types:**
- `COVER [BUMP]` — fixed floorplan data (power routing)
- `RING` — internal power mesh macro
- `BLOCK [BLACKBOX|SOFT]` — hierarchical block
- `PAD [INPUT|OUTPUT|INOUT|POWER|SPACER|AREAIO]` — I/O pad
- `CORE [FEEDTHRU|TIEHIGH|TIELOW|SPACER|ANTENNACELL|WELLTAP]` — standard cell
- `ENDCAP {PRE|POST|TOPLEFT|TOPRIGHT|BOTTOMLEFT|BOTTOMRIGHT}` — row end-cap cell

### PIN (Macro Pin)
```
PIN pinName
  [TAPERRULE ruleName ;]
  [DIRECTION {INPUT | OUTPUT [TRISTATE] | INOUT | FEEDTHRU} ;]
  [USE {SIGNAL | ANALOG | POWER | GROUND | CLOCK} ;]
  [NETEXPR "netExprPropName defaultNetName" ;]
  [SUPPLYSENSITIVITY powerPinName ;]
  [GROUNDSENSITIVITY groundPinName ;]
  [SHAPE {ABUTMENT | RING | FEEDTHRU} ;]
  [MUSTJOIN pinName ;]
  {PORT
    [CLASS {NONE | CORE | BUMP} ;]
    {layerGeometries} ...
  END} ...
  [ANTENNAPARTIALMETALAREA value [LAYER layerName] ;] ...
  [ANTENNAPARTIALMETALSIDEAREA value [LAYER layerName] ;] ...
  [ANTENNAPARTIALCUTAREA value [LAYER layerName] ;] ...
  [ANTENNADIFFAREA value [LAYER layerName] ;] ...
  [ANTENNAMODEL {OXIDE1|OXIDE2|OXIDE3|OXIDE4} ;] ...
  [ANTENNAGATEAREA value [LAYER layerName] ;] ...
  [ANTENNAMAXAREACAR value LAYER layerName ;] ...
  [ANTENNAMAXSIDEAREACAR value LAYER layerName ;] ...
  [ANTENNAMAXCUTCAR value LAYER layerName ;] ...
  [PROPERTY propName propVal ;] ...
END pinName
```

### Layer Geometries (inside PIN or OBS)
```
LAYER layerName ;
  [RECT pt pt ;] ...
  [POLYGON pt pt pt ... ;] ...
  [VIA pt viaName ;] ...
```
Layer geometries appear inside PIN PORT blocks or OBS blocks.

### OBS (Obstruction)
```
OBS
  {layerGeometries} ...
END
```

### DENSITY
```
DENSITY
  {LAYER layerName ;
    {RECT x1 y1 x2 y2 densityValue ;} ...
  } ...
END
```
`densityValue` is a float from 0 to 100 (percentage).

---

## DEF (Design Exchange Format)

### General Rules
- Coordinates in DEF database units (divide by UNITS DISTANCE MICRONS value for microns)
- Statements end with `;`
- Net/component names follow the hierarchy divider character (default `/`)
- Keyword order within a statement is flexible; statement order is significant

### Statement Order
```
[VERSION]
[DIVIDERCHAR]
[BUSBITCHARS]
[DESIGN]
[UNITS]
[PROPERTYDEFINITIONS]
[DIEAREA]
[ROWS]
[TRACKS]
[GCellGRID]
[VIAS]
[STYLES]
[NONDEFAULTRULES]
[REGIONS]
[COMPONENTS]
[PINS]
[PINPROPERTIES]
[BLOCKAGES]
[SLOTS]
[FILLS]
[SPECIALNETS]
[NETS]
[SCANCHAINS]
[GROUPS]
[BEGINEXT]
END DESIGN
```

### DESIGN
```
DESIGN designName ;
```
Must be the first statement after header statements.

### UNITS
```
UNITS DISTANCE MICRONS db_unit ;
```
All coordinates in the DEF file are divided by `db_unit` to get microns.

### DIEAREA
```
DIEAREA pt pt pt pt ;
```
Defines the chip boundary as a rectangle (4 points) or polygon.

### COMPONENTS
```
COMPONENTS numComps ;
  [- compName modelName
    [+ EEQMASTER macroName]
    [+ SOURCE {NETLIST | DIST | USER | TIMING}]
    [+ {FIXED pt orient | COVER pt orient | PLACED pt orient | UNPLACED}]
    [+ MASKSHIFT shiftLayerMasks]
    [+ HALO [SOFT] left bottom right top]
    [+ ROUTEHALO haloDist minLayer maxLayer]
    [+ WEIGHT weight]
    [+ REGION regionName]
    [+ PROPERTY {propName propVal} ...]
  ;] ...
END COMPONENTS
```

**Placement status:**
- `FIXED` — cannot be moved by automatic tools
- `COVER` — part of a cover macro, cannot be moved
- `PLACED` — has a location, can be moved by automatic tools
- `UNPLACED` — no location assigned

**Orientation values:** `N`, `S`, `W`, `E`, `FN`, `FS`, `FW`, `FE`

### PINS
```
PINS numPins ;
  [- pinName + NET netName
    [+ DIRECTION {INPUT | OUTPUT | INOUT | FEEDTHRU}]
    [+ USE {SIGNAL | ANALOG | POWER | GROUND | CLOCK}]
    [+ LAYER layerName pt pt]
    [+ {FIXED | PLACED | COVER} pt orient]
  ;] ...
END PINS
```

### NETS
```
NETS numNets ;
  [- netName
    ( {compName pinName | PIN pinName} ) ...
    [+ regularWiring] ...
  ;] ...
END NETS
```

### Regular Wiring
```
+ ROUTED layerName [TAPER | TAPERRULE ruleName] ( x0 y0 [e0] ) ( x1 y1 [e1] ) ...
  [NEW layerName ( x0 y0 [e0] ) ( x1 y1 [e1] ) ...] ...
```
- `*` (asterisk) can replace coordinates in routing points to indicate continuity from the previous point
- `TAPER`/`TAPERRULE` specifies tapered routing
- `NEW` starts a new routing path on a new layer

### SPECIALNETS
```
SPECIALNETS numNets ;
  [- netName
    [( compName pinName )] ...
    [+ specialWiring] ...
  ;] ...
END SPECIALNETS
```

### Special Wiring
```
+ layerName width ( x0 y0 [e0] ) ( x1 y1 [e1] ) [viaName] ...
  [NEW layerName width ( x0 y0 ) ...] ...
```
- `*` placeholders work the same as in regular wiring
- `e0`/`e1` are optional extension values

### BLOCKAGES
```
BLOCKAGES numBlockages ;
  [- LAYER layerName
    [+ {PLACEMENT | ROUTING | SOFT}]
    [+ PUSHDOWN]
    [+ COMPONENT compName]
    [+ SPACING minSpacing]
    [+ DESIGNRULEWIDTH width]
    [RECT pt pt ;] ...
    [POLYGON pt pt pt ... ;] ...
  ;] ...
END BLOCKAGES
```

### TRACKS
```
TRACKS {X | Y} start DO numTracks STEP step
  [MASK maskNum [SAMEMASK]]
  LAYER layerName ... ;
```

### FILLS
```
FILLS numFills ;
  [- LAYER layerName
    [+ MASK maskNum]
    RECT pt pt ; ...
  ;] ...
END FILLS
```

### VIAS (DEF-level)
```
VIAS numVias ;
  [- viaName
    [+ layerName RECT pt pt ;] ...
  ;] ...
END VIAS
```

### NONDEFAULTRULES (DEF-level)
```
NONDEFAULTRULES numNDRs ;
  [- ruleName
    [+ HARDSPACING]
    [+ LAYER layerName WIDTH width [SPACING spacing] ;] ...
    [+ VIA viaName ;] ...
    [+ USEVIA viaName ;] ...
    [+ MINCUTS layerName numCuts ;] ...
  ;] ...
END NONDEFAULTRULES
```

### ROWS
```
ROWS numRows ;
  [- rowName siteName pt orient
    [+ DO numX BY numY]
    [+ STEP stepX stepY]
    [+ PROPERTY propName propVal ;] ...
  ;] ...
END ROWS
```

### STYLES
```
STYLES numStyles ;
  [- styleNum pt orient ;] ...
END STYLES
```

### SCANCHAINS
```
SCANCHAINS numChains ;
  [- chainName
    [+ {INPUT | OUTPUT} portPinName] ...
    [+ FLOATING {compName pinName} ...]
    [+ ORDERED {compName pinName [pinName]} ...] ...
  ;] ...
END SCANCHAINS
```

### GCellGRID
```
GCELLGRID {X | Y} start DO num STEP step ;
```

### REGIONS
```
REGIONS numRegions ;
  [- regionName pt pt ... ;] ...
END REGIONS
```

### PROPERTYDEFINITIONS
```
PROPERTYDEFINITIONS
  [DESIGN propName {INTEGER | REAL | STRING} ... ;] ...
END PROPERTYDEFINITIONS
```

---

## Examples

### Minimal Tech LEF
```
LAYER M1
  TYPE ROUTING ;
  DIRECTION HORIZONTAL ;
  PITCH 0.10 0.10 ;
  WIDTH 0.05 ;
  SPACING 0.05 ;
END M1
```

### Minimal Macro LEF
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

### Minimal DEF
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
NETS 3 ;
  - net_clk
    ( PIN clk ) ( u_sub/clk )
    + ROUTED M1 ( 5000 50000 ) ( 20000 45000 )
  ;
END NETS
END DESIGN
```

---

## Orientation Reference

| DEF Name | OA Name | Rotation | Mirror X | Mirror Y |
|---|---|---|---|---|
| N | R0 | 0 | No | No |
| S | R180 | 180 | No | No |
| W | R90 | 90 | No | No |
| E | R270 | 270 | No | No |
| FN | MY | 0 | No | Yes |
| FS | MX | 0 | Yes | No |
| FW | MX90 | 90 | Yes | No |
| FE | MY90 | 90 | No | Yes |
