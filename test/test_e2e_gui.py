import os
import sys
import subprocess
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')
PHOTON_BIN = os.path.join(os.path.dirname(__file__), '..', 'bin', 'photon.py')


def _run_photon(script_name):
    env = os.environ.copy()
    env['QT_QPA_PLATFORM'] = 'offscreen'
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    return subprocess.run(
        [sys.executable, PHOTON_BIN, '-f', script_path, '--nolog'],
        capture_output=True, text=True, timeout=120, env=env
    )


class TestPhotonE2E:
    def test_gui_startup_via_photon(self):
        result = _run_photon('test_gui_startup.py')
        assert 'GUI_STARTUP_OK' in result.stdout, (
            f'Marker not found.\nstdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}'
        )
        assert result.returncode == 0, f'Exit code: {result.returncode}'

    def test_heatmap_colors_count(self):
        result = _run_photon('test_heatmap_colors.py')
        assert 'HEATMAP_COLORS_OK' in result.stdout, (
            f'Marker not found.\nstdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}'
        )
        assert result.returncode == 0, f'Exit code: {result.returncode}'
