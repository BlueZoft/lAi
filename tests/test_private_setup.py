import shutil
import stat
import subprocess
import sys
from pathlib import Path


def test_setup_makes_uv_created_configuration_directory_private(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    source = Path(__file__).resolve().parents[1] / "scripts/prepare_local.py"
    shutil.copyfile(source, scripts / "prepare_local.py")
    local = tmp_path / ".local"
    local.mkdir(mode=0o755)
    result = subprocess.run(
        [sys.executable, str(scripts / "prepare_local.py")], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert stat.S_IMODE(local.stat().st_mode) == 0o700
    assert stat.S_IMODE((local / "postgres.password").stat().st_mode) == 0o600
    assert (local / "postgres-socket").is_dir()
