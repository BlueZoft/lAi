from pathlib import Path

import pytest

from lai.answers.review import MARKER, build_packet
from lai.answers.service import load_glosses
from lai.triage.templates import load_templates

ROOT = Path(__file__).resolve().parents[1]


def test_review_packet_is_offline_and_cannot_approve_copy(tmp_path: Path) -> None:
    output = tmp_path / "review.html"
    build_packet(ROOT, output)
    body = output.read_text()
    assert MARKER in body and "UNREVIEWED" in body and "SYNTHETIC" in body
    assert "<script" not in body and "<form" not in body
    assert all(item.review_status == "UNREVIEWED" for item in load_glosses().glosses)
    assert all(item.review_status == "UNREVIEWED" for item in load_templates().templates)
    assert output.stat().st_mode & 0o077 == 0
    build_packet(ROOT, output)
    assert output.read_text() == body


def test_packet_will_not_replace_unrelated_user_file(tmp_path: Path) -> None:
    output = tmp_path / "existing.html"
    output.write_text("SYNTHETIC unrelated user document")
    with pytest.raises(ValueError, match="refusing_to_overwrite"):
        build_packet(ROOT, output)
    assert output.read_text() == "SYNTHETIC unrelated user document"


def test_packet_will_not_write_tracked_project_paths() -> None:
    with pytest.raises(ValueError, match="review_output"):
        build_packet(ROOT, ROOT / "README.html")
