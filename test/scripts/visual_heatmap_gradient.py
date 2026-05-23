"""Generate a visual comparison of old 12-color vs new 128-color gradient."""
import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from PyQt5 import QtGui

# ---- Old 12-color hardcoded (from original code) ----
old_colors = [
    QtGui.QColor(255, 255, 255, 150),
    QtGui.QColor(255, 0, 0, 155),
    QtGui.QColor(255, 128, 0, 150),
    QtGui.QColor(255, 255, 0, 150),
    QtGui.QColor(128, 255, 0, 150),
    QtGui.QColor(0, 204, 102, 150),
    QtGui.QColor(0, 255, 255, 150),
    QtGui.QColor(0, 128, 255, 150),
    QtGui.QColor(0, 0, 255, 150),
    QtGui.QColor(0, 0, 102, 150),
    QtGui.QColor(0, 0, 52, 150),
    QtGui.QColor(0, 0, 0, 150),
]

# ---- New 128-color gradient ----
from gui.mainView import _generateHeatmapColors
new_brushes = _generateHeatmapColors(128)
new_colors = [b.color() for b in new_brushes]

# ---- Build comparison image ----
HEIGHT = 60
old_width = 600
new_width = 600
gap = 4

img = Image.new('RGBA', (max(old_width, new_width), HEIGHT * 2 + gap), (30, 30, 30, 255))

# Old gradient (top)
for x in range(old_width):
    idx = int(x / old_width * len(old_colors))
    c = old_colors[min(idx, len(old_colors) - 1)]
    for y in range(HEIGHT):
        img.putpixel((x, y), (c.red(), c.green(), c.blue(), c.alpha()))

# New gradient (bottom)
for x in range(new_width):
    idx = int(x / new_width * len(new_colors))
    c = new_colors[min(idx, len(new_colors) - 1)]
    for y in range(HEIGHT):
        img.putpixel((x, HEIGHT + gap + y), (c.red(), c.green(), c.blue(), c.alpha()))

out_path = os.path.join(os.path.dirname(__file__), '..', '..', 'heatmap_gradient_comparison.png')
img.save(out_path)
print(f'Saved: {out_path}')
print(f'Old: {len(old_colors)} colors, New: {len(new_colors)} colors')
