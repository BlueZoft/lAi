import subprocess
import sys
from pathlib import Path


def test_source_package_is_allowed_while_corpus_artifacts_are_blocked(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    script = Path(__file__).resolve().parents[1] / "scripts/check_repository.py"
    source = tmp_path / "src/lai/corpus"
    source.mkdir(parents=True)
    (source / "models.py").write_text('"""Synthetic source module."""\n')
    command = [sys.executable, str(script), "--root", str(tmp_path)]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0
    data = tmp_path / "corpus"
    data.mkdir()
    (data / "synthetic.json").write_text('{"synthetic": true}')
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Forbidden artefact: corpus/synthetic.json" in result.stderr
