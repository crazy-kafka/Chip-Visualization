"""
Unit tests for utility modules: Orient, CoordinateProcess, PathOperation,
shapeProcess, readFile, PSTATUS.
"""
import os
import sys
import pytest
import math
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.coordinateProcess import Orient, CoordinateProcess, PathOperation
from utils.shapeProcess import polygonPartitioning, rectMapToPtnLocal
from utils.readFile import readFile, readFileLines
from utils.pstatus import PSTATUS


# ======================== Orient ========================

class TestOrient:
    def test_all_eight_orientations_in_map(self):
        for orient in ['N', 'S', 'W', 'E', 'FN', 'FS', 'FW', 'FE']:
            assert orient in Orient.orient_map
            assert 'R' in Orient.orient_map[orient]
            assert 'X' in Orient.orient_map[orient]
            assert 'Y' in Orient.orient_map[orient]

    def test_DEF_OA_roundtrip_all(self):
        for def_orient in ['N', 'S', 'W', 'E', 'FN', 'FS', 'FW', 'FE']:
            oa = Orient.DEF_OA_map[def_orient]
            def_back = Orient.OA_DEF_map[oa]
            assert def_back == def_orient

    def test_OA_DEF_roundtrip_all(self):
        for oa in ['R0', 'R180', 'R90', 'R270', 'MY', 'MX', 'MX90', 'MY90']:
            def_orient = Orient.OA_DEF_map[oa]
            oa_back = Orient.DEF_OA_map[def_orient]
            assert oa_back == oa

    def test_merge_N_N(self):
        assert Orient.mergeOrient('N', 'N') == 'N'

    def test_merge_S_S_is_N(self):
        assert Orient.mergeOrient('S', 'S') == 'N'

    def test_merge_N_FN_is_FN(self):
        assert Orient.mergeOrient('N', 'FN') == 'FN'

    def test_merge_FS_FS_is_N(self):
        assert Orient.mergeOrient('FS', 'FS') == 'N'

    def test_merge_N_W_is_W(self):
        assert Orient.mergeOrient('N', 'W') == 'W'

    def test_merge_W_W_is_S(self):
        assert Orient.mergeOrient('W', 'W') == 'S'

    def test_merge_N_E_is_E(self):
        assert Orient.mergeOrient('N', 'E') == 'E'

    def test_merge_invalid_raises(self):
        with pytest.raises(ValueError):
            Orient.mergeOrient('INVALID', 'N')

    def test_merge_N_S_is_S(self):
        assert Orient.mergeOrient('N', 'S') == 'S'

    def test_merge_FW_S_is_FE(self):
        assert Orient.mergeOrient('FW', 'S') == 'FE'

    def test_merge_FW_FE_is_N(self):
        assert Orient.mergeOrient('FW', 'FE') == 'N'

    def test_merge_FS_W_is_FW(self):
        assert Orient.mergeOrient('FS', 'W') == 'FW'

    def test_merge_E_FN_is_FW(self):
        assert Orient.mergeOrient('E', 'FN') == 'FW'


# ======================== CoordinateProcess ========================

class TestCoordinateProcess:
    def test_dbTransform_to_global_N(self):
        result = CoordinateProcess.dbTransform('to_global', (10, 20), 'N', (100, 200))
        assert result == (110.0, 220.0)

    def test_dbTransform_to_global_S(self):
        result = CoordinateProcess.dbTransform('to_global', (10, 20), 'S', (100, 200))
        assert result == (90.0, 180.0)

    def test_dbTransform_to_global_W(self):
        result = CoordinateProcess.dbTransform('to_global', (10, 20), 'W', (100, 200))
        assert result == (80.0, 210.0)

    def test_dbTransform_to_global_E(self):
        result = CoordinateProcess.dbTransform('to_global', (10, 20), 'E', (100, 200))
        assert result == (120.0, 190.0)

    def test_dbTransform_to_global_FN(self):
        result = CoordinateProcess.dbTransform('to_global', (10, 20), 'FN', (100, 200))
        assert result == (90.0, 220.0)

    def test_dbTransform_to_global_FS(self):
        result = CoordinateProcess.dbTransform('to_global', (10, 20), 'FS', (100, 200))
        assert result == (110.0, 180.0)

    def test_dbTransform_to_global_FW(self):
        result = CoordinateProcess.dbTransform('to_global', (10, 20), 'FW', (100, 200))
        assert result == (120.0, 210.0)

    def test_dbTransform_to_global_FE(self):
        result = CoordinateProcess.dbTransform('to_global', (10, 20), 'FE', (100, 200))
        assert result == (80.0, 190.0)

    def test_dbTransform_to_local_N(self):
        result = CoordinateProcess.dbTransform('to_local', (110, 220), 'N', (100, 200))
        assert result == (10.0, 20.0)

    def test_dbTransform_roundtrip_all_orientations(self):
        originals = {
            'N': (10, 20), 'S': (10, 20), 'W': (10, 20), 'E': (10, 20),
            'FN': (10, 20), 'FS': (10, 20), 'FW': (10, 20), 'FE': (10, 20),
        }
        for orient, pt in originals.items():
            global_pt = CoordinateProcess.dbTransform('to_global', pt, orient, (100, 100))
            local_pt = CoordinateProcess.dbTransform('to_local', global_pt, orient, (100, 100))
            assert local_pt == pt, f"Roundtrip failed for {orient}: {pt} -> {global_pt} -> {local_pt}"

    def test_dbTransform_batch_matches_single(self):
        import numpy as np
        xs = np.array([10, 20, 30])
        ys = np.array([5, 15, 25])
        bx, by = CoordinateProcess.dbTransformBatch('to_global', (xs, ys), 'N', (100, 100))
        for i in range(len(xs)):
            sx, sy = CoordinateProcess.dbTransform('to_global', (float(xs[i]), float(ys[i])), 'N', (100, 100))
            assert round(bx[i], 4) == round(sx, 4)
            assert round(by[i], 4) == round(sy, 4)

    def test_dbTransform_invalid_trans_type(self):
        with pytest.raises(ValueError):
            CoordinateProcess.dbTransform('invalid', (10, 20), 'N', (0, 0))

    def test_dbTransform_invalid_orient(self):
        with pytest.raises(ValueError):
            CoordinateProcess.dbTransform('to_global', (10, 20), 'INVALID', (0, 0))

    def test_calculateBoundingBox(self):
        box = CoordinateProcess.calulateBoundingBox([(0, 0), (10, 20), (-5, 30)])
        assert box == [(-5, 0), (10, 30)]

    def test_calculateUrptByOrient_N(self):
        result = CoordinateProcess.calculateUrptByOrient([0, 0], 'N', height=5, width=10)
        assert result == [10, 5]

    def test_calculateUrptByOrient_W(self):
        result = CoordinateProcess.calculateUrptByOrient([0, 0], 'W', height=5, width=10)
        assert result == [5, 10]

    def test_calculateUrptByOrient_E(self):
        result = CoordinateProcess.calculateUrptByOrient([0, 0], 'E', height=5, width=10)
        assert result == [5, 10]

    def test_calculateOriginByOrient_N(self):
        result = CoordinateProcess.calculateOriginByOrient((0, 0), 'N', 5, 10)
        assert result == (0, 0)

    def test_calculateOriginByOrient_S(self):
        result = CoordinateProcess.calculateOriginByOrient((0, 0), 'S', 5, 10)
        assert result == (10, 5)

    def test_calculateOriginByOrient_W(self):
        result = CoordinateProcess.calculateOriginByOrient((0, 0), 'W', 5, 10)
        assert result == (5, 0)

    def test_calculateOriginByOrient_E(self):
        result = CoordinateProcess.calculateOriginByOrient((0, 0), 'E', 5, 10)
        assert result == (0, 5)

    def test_calculateOriginByOrient_invalid(self):
        with pytest.raises(ValueError):
            CoordinateProcess.calculateOriginByOrient((0, 0), 'INVALID', 5, 10)

    def test_getManhattanLength(self):
        assert CoordinateProcess.getManhattanLength((0, 0), (3, 4)) == 7.0

    def test_resizeBox(self):
        box = [(0, 0), (10, 0), (10, 10), (0, 10)]
        result = CoordinateProcess.resizeBox(box, 2, 3)
        assert result == [(-2, -3), (12, -3), (12, 13), (-2, 13)]


# ======================== PathOperation ========================

class TestPathOperation:
    def test_getPathLength_straight(self):
        length = PathOperation.getPathLength([(0, 0), (3, 4)])
        assert length == pytest.approx(5.0)

    def test_getPathLength_L_shape(self):
        length = PathOperation.getPathLength([(0, 0), (3, 0), (3, 4)])
        assert length == pytest.approx(7.0)

    def test_mapLenToPath_halfway(self):
        pt = PathOperation.mapLenToPath([(0, 0), (10, 0)], 5.0)
        assert pt == (5.0, 0.0)

    def test_mapLenToPath_exceeds_raises(self):
        with pytest.raises(ValueError):
            PathOperation.mapLenToPath([(0, 0), (10, 0)], 100.0)

    def test_getEvenCoordInPath_3points(self):
        coords = PathOperation.getEvenCoordInPath([(0, 0), (10, 0)], 3)
        assert len(coords) == 3
        assert coords[0] == (2.5, 0.0)
        assert coords[1] == (5.0, 0.0)
        assert coords[2] == (7.5, 0.0)

    def test_getEvenCoordInPath_single_point(self):
        coords = PathOperation.getEvenCoordInPath([(0, 0), (10, 0)], 1)
        assert len(coords) == 1
        assert coords[0] == (5.0, 0.0)

    def test_getEvenCoordInPath_zero_returns_empty(self):
        coords = PathOperation.getEvenCoordInPath([(0, 0), (10, 0)], 0)
        assert coords == []

    def test_assignPathNode_default(self):
        coords = PathOperation.assignPathNode([(0, 0), (10, 0)], 3)
        assert len(coords) == 3

    def test_isBetween_true(self):
        assert PathOperation.isBetween((0, 0), (10, 0), (5, 0)) is True

    def test_isBetween_false_outside(self):
        assert PathOperation.isBetween((0, 0), (10, 0), (15, 0)) is False

    def test_isBetween_false_not_collinear(self):
        assert PathOperation.isBetween((0, 0), (10, 0), (5, 1)) is False

    def test_cutPathByPoint(self):
        result = PathOperation.cutPathByPoint([(0, 0), (10, 0), (10, 10)], (10, 0))
        assert result == [(0, 0), (10, 0)]

    def test_cutPathByLen(self):
        result = PathOperation.cutPathByLen([(0, 0), (10, 0), (10, 10)], 12.0)
        assert len(result) == 3
        assert result[0] == (0, 0)
        assert result[1] == (10, 0)
        assert result[2] == (10.0, 2.0)


# ======================== shapeProcess ========================

class TestShapeProcess:
    def test_polygonPartitioning_hrect_square(self):
        V = [(0, 0), (10, 0), (10, 10), (0, 10)]
        rects = polygonPartitioning(V, mode='hrect')
        assert len(rects) == 1
        assert rects[0] == (0, 0, 10, 10)

    def test_polygonPartitioning_vrect_square(self):
        V = [(0, 0), (10, 0), (10, 10), (0, 10)]
        rects = polygonPartitioning(V, mode='vrect')
        assert len(rects) == 1
        assert rects[0] == (0, 0, 10, 10)

    def test_polygonPartitioning_empty(self):
        rects = polygonPartitioning([], mode='hrect')
        assert rects == []

    def test_polygonPartitioning_hrect_L_shape(self):
        # L-shaped polygon
        V = [(0, 0), (4, 0), (4, 1), (2, 1), (2, 4), (0, 4)]
        rects = polygonPartitioning(V, mode='hrect')
        assert len(rects) >= 2

    def test_polygonPartitioning_vrect_L_shape(self):
        V = [(0, 0), (4, 0), (4, 1), (2, 1), (2, 4), (0, 4)]
        rects = polygonPartitioning(V, mode='vrect')
        assert len(rects) >= 2


# ======================== readFile ========================

class TestReadFile:
    def test_readFile_plain(self, tech_lef_path):
        content = readFile(tech_lef_path)
        assert 'LAYER M1' in content
        assert 'TYPE ROUTING' in content

    def test_readFileLines_count(self, tech_lef_path):
        lines = readFileLines(tech_lef_path)
        assert len(lines) > 0
        assert any('LAYER M1' in line for line in lines)


# ======================== PSTATUS ========================

class TestPSTATUS:
    def test_enum_values(self):
        assert PSTATUS.UNPLACED.value == 0
        assert PSTATUS.PLACED.value == 1
        assert PSTATUS.FIXED.value == 2
