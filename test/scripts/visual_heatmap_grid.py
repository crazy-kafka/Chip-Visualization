"""Generate a 2D heatmap comparison: old 12-color vs new 128-color gradient.

Creates a synthetic data grid with a radial gradient and renders it with both palettes.
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import numpy as np
from PIL import Image
from PyQt5 import QtGui

SIZE = 300  # pixels per side

# ---- Synthetic data: radial gradient + noise ----
xs = np.linspace(-2, 2, SIZE)
ys = np.linspace(-2, 2, SIZE)
xx, yy = np.meshgrid(xs, ys)
data = np.sin(xx) * np.cos(yy) + 0.3 * np.random.randn(SIZE, SIZE)
# Normalize to [0, 1]
dmin, dmax = data.min(), data.max()
data = (data - dmin) / (dmax - dmin)

# ---- Old 12-color palette ----
old_c = [
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
old_n = len(old_c) - 1

# ---- New 128-color palette ----
from gui.mainView import _generateHeatmapColors
new_b = _generateHeatmapColors(128)
new_c = [b.color() for b in new_b]
new_n = len(new_c) - 1

def render(data, colors, n):
    """Map data [0,1] to color indices and produce RGBA image."""
    indices = (n - np.ceil(n * np.clip(data, 0, 1))).astype(int)
    img = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    for i in range(SIZE):
        for j in range(SIZE):
            c = colors[indices[i, j]]
            img[i, j] = [c.red(), c.green(), c.blue(), c.alpha()]
    return img

old_img = render(data, old_c, old_n)
new_img = render(data, new_c, new_n)

# ---- Side-by-side image (old left, new right) ----
gap = 10 ; label_h = 20
out = Image.new('RGBA', (SIZE * 2 + gap, SIZE + label_h), (30, 30, 30, 255))
out.paste(Image.fromarray(old_img, 'RGBA'), (0, label_h))
out.paste(Image.fromarray(new_img, 'RGBA'), (SIZE + gap, label_h))

out_path = os.path.join(os.path.dirname(__file__), '..', '..', 'heatmap_comparison.png')
out.save(out_path)
print(f'Saved: {out_path}')
print(f'Old palette: {len(old_c)} colors ({old_n} bins) — visible banding')
print(f'New palette: {len(new_c)} colors ({new_n} bins) — smooth')
