"""Check operator-supplied trusted checksums before recording local artefact pins."""

import argparse
from pathlib import Path

from lai.model_tasks.local import LlamaCppBackend, ModelManifest
from lai.model_tasks.measure import write_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--expected-model-sha256", required=True)
    parser.add_argument("--expected-executable-sha256", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--runner-revision", required=True)
    parser.add_argument("--parameters-billions", type=float, required=True)
    parser.add_argument("--licence-evidence-ref", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = ModelManifest(
            model_id=args.model_id,
            revision=args.revision,
            runner_revision=args.runner_revision,
            model_sha256=args.expected_model_sha256,
            executable_sha256=args.expected_executable_sha256,
            parameters_billions=args.parameters_billions,
            licence_evidence_ref=args.licence_evidence_ref,
        )
        LlamaCppBackend(args.executable, args.model, manifest)
        write_report(args.output, manifest.model_dump(mode="json"))
    except (OSError, ValueError):
        raise SystemExit(
            "Pinning failed; check trusted checksums, local files and output path"
        ) from None
    print(
        "Local artefact pins recorded; licensing, model metadata and language quality need review"
    )


if __name__ == "__main__":
    main()
