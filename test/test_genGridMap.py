"""
Tests for genStatGrid.py --parallel local (multiprocess mode).
Tests genStatGrid.py directly via subprocess to avoid UiDB/MainWindow overhead.
"""
import os
import sys
import subprocess
import pickle
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DATA = os.path.join(os.path.dirname(__file__), 'data')
GENSTAT = os.path.join(os.path.dirname(__file__), '..', 'bin', 'genStatGrid.py')


def _run_genstat(tmp_path, mode, spec_lines, lsf_cmd=None):
    """Run genStatGrid.py with --parallel local and return the result grid."""
    cwd = os.getcwd()
    os.chdir(str(tmp_path))

    # Pickle the LEF parser (use abspath so it works from tmp_path)
    from LEF import LefParser
    cells_lef = os.path.join(DATA, 'cells.lef')
    lp = LefParser([cells_lef])
    cell_db = os.path.join(str(tmp_path), 'cell_info.db')
    with open(cell_db, 'wb') as f:
        pickle.dump(lp, f)

    # Write spec file
    spec_file = 'test.spec'
    with open(spec_file, 'w') as f:
        for line in spec_lines:
            f.write(line + '\n')

    # Create ptn_info files referenced in spec (absolute paths in tmp_path)
    for line in spec_lines:
        parts = line.split()
        ptn_info_file = os.path.join(str(tmp_path), parts[2])
        if not os.path.exists(ptn_info_file):
            with open(ptn_info_file, 'w') as f:
                f.write('# ptn_orient origin_x origin_y\n')
                f.write('N 0 0\n')

    out_dir = 'StatGrid_test'
    cmd = [sys.executable, GENSTAT,
           '-m', mode, '-s', spec_file, '-l', cell_db,
           '-g', '10', '-o', out_dir,
           '--parallel', 'local']
    if lsf_cmd:
        cmd.extend(['--lsf_cmd', lsf_cmd])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    os.chdir(cwd)

    # Find output .txt files
    out_files = []
    if os.path.exists(str(tmp_path)):
        for root, dirs, files in os.walk(str(tmp_path)):
            for fn in files:
                if fn.endswith('.txt') and 'StatGrid' in root:
                    out_files.append(os.path.join(root, fn))

    return result, out_files


class TestGenStatGridLocal:
    def test_cell_density_runs(self, tmp_path):
        """genStatGrid --parallel local in cell_density mode produces output."""
        adder_def = os.path.join(DATA, 'adder.def')
        spec = [f'adder {adder_def} adder.ptn_info']
        result, out_files = _run_genstat(tmp_path, 'cell_density', spec)
        assert result.returncode == 0, f'stderr: {result.stderr[-500:]}'
        assert len(out_files) > 0, 'No output files generated'
        assert os.path.getsize(out_files[0]) > 0

    def test_pin_density_runs(self, tmp_path):
        """genStatGrid --parallel local in pin_density mode."""
        adder_def = os.path.join(DATA, 'adder.def')
        spec = [f'adder {adder_def} adder.ptn_info']
        result, out_files = _run_genstat(tmp_path, 'pin_density', spec)
        assert result.returncode == 0, f'stderr: {result.stderr[-500:]}'
        assert len(out_files) > 0

    def test_discrete_runs(self, tmp_path):
        """genStatGrid --parallel local in discrete mode."""
        adder_def = os.path.join(DATA, 'adder.def')
        spec = [f'adder {adder_def} adder.ptn_info']
        result, out_files = _run_genstat(tmp_path, 'discrete', spec)
        assert result.returncode == 0, f'stderr: {result.stderr[-500:]}'

    def test_lsf_cmd_accepted(self, tmp_path):
        """--lsf_cmd is accepted but not used in local mode (no crash)."""
        adder_def = os.path.join(DATA, 'adder.def')
        spec = [f'adder {adder_def} adder.ptn_info']
        result, _ = _run_genstat(
            tmp_path, 'cell_density', spec,
            lsf_cmd='bsub -q test_q -n1')
        assert result.returncode == 0

    def test_done_file_created(self, tmp_path):
        """Each partition creates a .done marker on success."""
        adder_def = os.path.join(DATA, 'adder.def')
        spec = [f'adder {adder_def} adder.ptn_info']
        result, _ = _run_genstat(tmp_path, 'cell_density', spec)
        done_files = []
        for root, dirs, files in os.walk(str(tmp_path)):
            for fn in files:
                if fn.endswith('.done'):
                    done_files.append(os.path.join(root, fn))
        assert len(done_files) > 0, 'No .done files created'


def _run_genstat_no_batch(tmp_path, mode, spec_line, def_list, mapping_file=''):
    """Run genStatGrid.py --no-batch and return the output .npy path."""
    cwd = os.getcwd()
    os.chdir(str(tmp_path))

    from LEF import LefParser
    lp = LefParser([os.path.join(DATA, 'cells.lef')])
    cell_db = os.path.join(str(tmp_path), 'cell_info.db')
    with open(cell_db, 'wb') as f:
        pickle.dump(lp, f)

    spec_file = 'no_batch.spec'
    with open(spec_file, 'w') as f:
        f.write(spec_line + '\n')

    out_dir = 'StatGrid_nb'
    cmd = [sys.executable, GENSTAT,
           '-m', mode, '-s', spec_file, '-l', cell_db,
           '-g', '20', '-o', out_dir,
           '--no-batch', '--no-batch-defs'] + def_list
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    os.chdir(cwd)
    if result.returncode != 0:
        raise RuntimeError(f'genStatGrid failed: {result.stderr[-500:]}')

    npy_path = os.path.join(str(tmp_path), out_dir, f'{spec_line.split()[0]}.npy')
    return npy_path if os.path.exists(npy_path) else None


class TestGenGridNoBatch:
    def test_cell_density(self, tmp_path):
        defs = [os.path.join(DATA, d) for d in
                ['chip_top.def', 'core.def', 'alu.def', 'adder.def']]
        npy = _run_genstat_no_batch(
            tmp_path, 'cell_density',
            f'chip_top {defs[0]}', defs)
        assert npy and os.path.exists(npy)
        g = np.load(npy)
        assert g.shape[0] > 0
        assert np.count_nonzero(~np.isnan(g)) > 0

    def test_value_continuous(self, tmp_path):
        mapping = os.path.join(str(tmp_path), 'power.txt')
        with open(mapping, 'w') as f:
            f.write('u_core_0/u_alu_0/u_adder/u_buf_a 5.0\n')
            f.write('u_core_0/u_alu_0/u_adder/u_dff_a 8.0\n')
            f.write('u_core_1/u_alu_1/u_adder/u_mux_a 6.0\n')
            f.write('u_buf_top 10.0\n')
            f.write('u_core_0/u_alu_0/u_adder/u_nor_a 3.0\n')

        defs = [os.path.join(DATA, d) for d in
                ['chip_top.def', 'core.def', 'alu.def', 'adder.def']]
        npy = _run_genstat_no_batch(
            tmp_path, 'value_continuous',
            f'chip_top {defs[0]} {mapping}', defs)
        assert npy and os.path.exists(npy)
        g = np.load(npy)
        assert np.nanmax(g) > 0, 'Grid should have non-zero power values'

    def test_pin_density(self, tmp_path):
        defs = [os.path.join(DATA, d) for d in
                ['chip_top.def', 'core.def', 'alu.def', 'adder.def']]
        npy = _run_genstat_no_batch(
            tmp_path, 'pin_density',
            f'chip_top {defs[0]}', defs)
        assert npy and os.path.exists(npy)
        g = np.load(npy)
        assert np.nanmax(g) >= 0

    def test_discrete(self, tmp_path):
        mapping = os.path.join(str(tmp_path), 'disc.txt')
        with open(mapping, 'w') as f:
            f.write('u_core_0/u_alu_0/u_adder/u_buf_a 100.0\n')
            f.write('u_buf_top 50.0\n')

        defs = [os.path.join(DATA, d) for d in
                ['chip_top.def', 'core.def', 'alu.def', 'adder.def']]
        npy = _run_genstat_no_batch(
            tmp_path, 'discrete',
            f'chip_top {defs[0]} {mapping}', defs)
        assert npy and os.path.exists(npy)
        g = np.load(npy)
        assert np.nanmax(g) > 0
