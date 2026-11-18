"""Build a local, clearly synthetic draft-review document; never approves product copy."""

import argparse
import html
import json
import os
from importlib.resources import files
from pathlib import Path

from lai.answers.service import load_glosses
from lai.corpus.ingest import ingest_document
from lai.corpus.models import SourceManifest, digest
from lai.retrieval.catalog import record_chunks
from lai.triage.templates import load_templates

MARKER = "LAI_SYNTHETIC_REVIEW_PACKET_V1"


def build_packet(repository: Path, output: Path) -> None:
    destination = output.resolve()
    root = repository.resolve()
    if destination.suffix != ".html" or (
        destination.is_relative_to(root) and not destination.is_relative_to(root / ".local")
    ):
        raise ValueError("review_output_must_be_private_or_external_html")
    if destination.exists() and MARKER not in destination.read_text()[:500]:
        raise ValueError("refusing_to_overwrite_unrelated_file")
    fixture = root / "tests/fixtures"
    manifest = SourceManifest.model_validate_json(
        (fixture / "synthetic-act.manifest.json").read_bytes()
    )
    raw = (fixture / "synthetic-act.txt").read_bytes()
    record = ingest_document(manifest, raw, raw)
    chunks = {chunk.id: chunk for chunk in record_chunks(record)}
    glosses, templates = load_glosses(), load_templates()
    labels = json.loads(files("lai.answers").joinpath("ui/labels.json").read_bytes())

    def escaped(value: object) -> str:
        return html.escape(str(value))

    body = [
        f"<!doctype html><!-- {MARKER} --><html lang='en'><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>LAi synthetic reviewer packet — UNREVIEWED</title>",
        "<style>body{max-width:950px;margin:2rem auto;padding:1rem;"
        "font:17px/1.7 system-ui,sans-serif;color:#18342e;background:#f5f3ec}"
        "article{padding:1rem;border:1px solid #ccd4c9;margin:1rem 0;background:#fffef9}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}"
        "td,th{padding:.5rem;border:1px solid #ccd4c9;vertical-align:top;overflow-wrap:anywhere}"
        "code{overflow-wrap:anywhere}</style>",
        "<h1>SYNTHETIC OPERATOR REVIEW · UNREVIEWED DRAFTS</h1>",
        "<p>This is an offline reviewer document, not a product response. Sources and gloss "
        "seeds are invented. No approval or launch flag is changed by building or reading it. "
        "Reviewing these seeds does not approve any real legal provision.</p>",
        "<h2>What reviewers need to supply</h2><ol><li>Review the taxonomy and all six "
        "escalation paths, including safe alternatives for detention and imminent destitution.</li>"
        "<li>Review each fixed English/Sinhala safety pair and the interface labels below.</li>"
        "<li>For real glosses, supply the exact provision/version and reviewed text, language, "
        "review dates and an evidence reference. Regional phone confirmation and current "
        "eligibility/access still need primary evidence.</li></ol>",
        f"<p>Safety revision: {escaped(templates.revision)} · "
        f"Gloss revision: {escaped(glosses.revision)}</p>",
        "<h2>Version-bound synthetic gloss drafts</h2>",
    ]
    for gloss in glosses.glosses:
        chunk = chunks.get(gloss.chunk_id)
        if (
            chunk is None
            or gloss.source_record_id != record.record_id
            or gloss.section_sha256 != chunk.text_sha256
        ):
            raise ValueError("review_seed_source_mismatch")
        body.append(
            f"<article><h3>{escaped(gloss.id)} · {escaped(gloss.language)} · "
            f"{escaped(gloss.review_status)}</h3><p>Source is {escaped(chunk.language)}; "
            f"it is not machine-translated.</p><pre>{escaped(chunk.text)}</pre>"
            f"<p>{escaped(gloss.text)}</p><p>Chunk: <code>{escaped(chunk.id)}</code></p>"
            f"<p>Gloss text SHA-256: <code>{digest(gloss.text.encode())}</code></p>"
            f"<p>Source revision: {escaped(gloss.source_revision)}</p></article>"
        )
    body.append("<h2>Fixed safety copy — UNREVIEWED</h2>")
    for template in templates.templates:
        body.append(
            f"<article><h3>{escaped(template.id)} · {escaped(template.language)} · "
            f"{escaped(template.review_status)}</h3><p>{escaped(template.text)}</p></article>"
        )
    body.append(
        "<h2>Interface copy — UNREVIEWED</h2><table><tr>"
        "<th>ID</th><th>Sinhala</th><th>English</th></tr>"
    )
    for key, pair in labels.items():
        if key == "citation":
            continue
        body.append(
            f"<tr><td>{escaped(key)}</td><td lang='si'>{escaped(pair[0])}</td>"
            f"<td>{escaped(pair[1])}</td></tr>"
        )
    for key, pair in labels["citation"].items():
        body.append(
            f"<tr><td>{escaped(key)}</td><td lang='si'>{escaped(pair[0])}</td>"
            f"<td>{escaped(pair[1])}</td></tr>"
        )
    body.append(
        "</table><p>Record actual review against the exact revision/content hash, reviewer role, "
        "dates and an evidence reference retained outside Git. Do not include reviewer personal "
        "details or real client situations in this repository.</p></html>"
    )
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write("\n".join(body))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path(".local/t5-review.html"))
    args = parser.parse_args()
    try:
        build_packet(args.repository, args.output)
    except Exception:
        print("review_packet_failed")
        return 2
    print("Synthetic UNREVIEWED packet written; approvals and application configuration unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
