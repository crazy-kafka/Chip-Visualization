from __future__ import annotations
from typing import List, Tuple, Dict, Union, Iterable, TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    from dataBase import DbDataBase
    from dataBase.dbHInst import DbHInst

import math
import copy
from .coordinateProcess import CoordinateProcess
from .logUtil import Print

def polygonPartitioning(_V: List[Tuple[float, float]], mode='hrect', rects: List[Tuple[float, float, float, float]]=None) -> List[Tuple[float, float, float, float]]:
    """
    K.D.Gourley and D.M.Green, "A polygon-to-rectangle conversion algorithm,"
    IEEE Computer Graphics, vol.3, no.1, pp. 31 - 36, Jan / Feb.

    step 1 Let the given polygon be represented by as set V of vertices
    Step 2 Let Pk be the leftmost of the lowest vertices in V; Pl the next leftmost of the lowest vertices in V
    Step 3 Let Pm be the leftmost of the lowest vertices in V with y value greater than yk and x coordinate in the range between xk and xl (including xk, and xl)
    Step 4 The next rectangle is: xmin = xk,; ymin = yl; xmax = xl; ymax = ym
    Step 5 Remove Pk and Pl from V. Remove ( xk, ym ) and ( xl, ym ) if present in V else add them to V
    Step 6 If V is empty then stop else goto step 2
    """

    if rects is None:
        rects = []
    if not _V:
        return rects
    V = copy.deepcopy(_V)
    if mode == 'hrect':
        y_sorted = sorted(set([ii[1] for ii in V]))
        yk = y_sorted[0]
        V_lowermost = sorted([ii for ii in V if ii[1] == yk], key=lambda x: x[0])

        Pk = V_lowermost[0] ; xk = Pk[0] ; yk = Pk[1]
        Pl = V_lowermost[1] ; xl = Pl[0] ; yl = Pl[1]

        for y_value in y_sorted[1:]:
            pts = sorted([ii for ii in V if ii[1] == y_value and xl <= ii[0] <= xl], key=lambda  x: x[0])
            if len(pts) >= 1:
                Pm = pts[0]
                ym = y_value
                break
        rects.append((xl, yk, xl, ym))
        V.remove(Pk)
        V.remove(Pl)

        if (xk, ym) in V:
            V.remove((xk, ym))
        else:
            V.append((xk, ym))

        if (xl, ym) in V:
            V.remove((xl, ym))
        else:
            V.append((xl, ym))
        return polygonPartitioning(V, mode, rects)
    elif mode == 'vrect':
        x_sorted = sorted(set(ii[0] for ii in V))
        xk = x_sorted[0]
        V_lefmost = sorted([ii for ii in V if ii[0] == xk], key=lambda x: x[1])

        Pk = V_lefmost[0] ; xl = Pk[0] ; yk = Pk[1]
        Pl = V_lefmost[1] ; xl = Pl[0] ; yl = Pl[1]

        for x_value in x_sorted[1:]:
            pts = sorted([ii for ii in V if ii[0] == x_value and yk <= ii[1] <= yl], key=lambda  x: x[1])
            if len(pts) >= 1:
                Pm = pts[0]
                xm = x_value
                break
        rects.append((xk, yk, xm, yl))
        V.remove(Pk)
        V.remove(Pl)

        if (xm ,yk) in V:
            V.remove((xm, yk))
        else:
            V.append((xm, yk))

        if (xm, yl) in V:
            V.remove((xm, yl))
        else:
            V.append((xm, yl))
        return polygonPartitioning(V, mode, rects)

    else:
        Print(f'Error: {mode} is not valid polygon partitioning mode. Only vrect and hrect are acceptable')






