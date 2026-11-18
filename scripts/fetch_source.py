"""Explicit HTTPS acquisition with an expected SHA-256 and atomic local storage."""

import argparse
import json
import ssl
import sys
from http.client import HTTPMessage
from pathlib import Path
from typing import IO
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

from pydantic import TypeAdapter

from lai.corpus.ingest import MAX_DOCUMENT_BYTES
from lai.corpus.models import Sha256, Source, digest
from lai.corpus.store import write_immutable


class HTTPSRedirect(HTTPRedirectHandler):
    def redirect_request(
        self,
        request: Request,
        response: IO[bytes],
        code: int,
        message: str,
        headers: HTTPMessage,
        new_url: str,
    ) -> Request | None:
        Source.public_source_url(new_url)
        if urlsplit(new_url).scheme != "https":
            raise ValueError("https_redirect_required")
        return super().redirect_request(request, response, code, message, headers, new_url)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        expected = TypeAdapter(Sha256).validate_python(args.sha256)
        Source.public_source_url(args.url)
        if urlsplit(args.url).scheme != "https":
            raise ValueError("https_required")
        opener = build_opener(HTTPSHandler(context=ssl.create_default_context()), HTTPSRedirect())
        with opener.open(
            Request(args.url, headers={"User-Agent": "LAi-corpus-intake"}), timeout=30
        ) as response:
            data = response.read(MAX_DOCUMENT_BYTES + 1)
        if len(data) > MAX_DOCUMENT_BYTES or digest(data) != expected:
            raise ValueError("source_hash_or_size_invalid")
        write_immutable(args.output, data)
    except (OSError, ValueError):
        print(json.dumps({"error": "source_fetch_failed"}), file=sys.stderr)
        return 2
    print(json.dumps({"sha256": expected, "bytes": len(data)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
