"""Measure an upstream extraction without emitting document text or metadata values."""

import argparse
import json
import sys
from pathlib import Path

from lai.corpus.cli import read_limited
from lai.corpus.models import Extraction, Instrument, digest
from lai.corpus.parser import parse_act
from lai.corpus.quality import assess_text


def block_fonts(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"fonts", "font"}:
                if isinstance(item, str):
                    found.add(item)
                if isinstance(item, list):
                    found.update(font for font in item if isinstance(font, str))
            found.update(block_fonts(item))
    elif isinstance(value, list):
        for item in value:
            found.update(block_fonts(item))
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=Path, required=True)
    parser.add_argument("--blocks", type=Path)
    parser.add_argument("--language", choices=["en", "si", "ta"], required=True)
    args = parser.parse_args()
    try:
        text_bytes = read_limited(args.text)
        text = text_bytes.decode("utf-8")
        fonts = block_fonts(json.loads(read_limited(args.blocks))) if args.blocks else set()
        extraction = Extraction(
            method="native_pdf", tool="upstream-sample", version="1", fonts=tuple(sorted(fonts))
        )
        quality = assess_text(text, args.language, extraction)
        parsed = parse_act(text, args.language, Instrument(id="research-only", kind="act"))
    except (OSError, ValueError):
        print(json.dumps({"error": "sample_measurement_failed"}), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "text_sha256": digest(text_bytes),
                "text_bytes": len(text_bytes),
                "font_count": len(fonts),
                "quality": quality.model_dump(mode="json"),
                "parsed_sections": len(parsed.sections),
                "parse_issues": parsed.issues,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
