"""Offline audit of source bytes and listing fields; never a live-service guarantee."""

import argparse
import hashlib
import json
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree

from lai.corpus.models import Contract, Sha256
from lai.triage.referrals import load_referrals


class Artefact(Contract):
    url: str
    file: str
    sha256: Sha256
    observed_on: date


class Manifest(Contract):
    sources: tuple[Artefact, ...]


class Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def audit(directory: Path) -> tuple[int, int]:
    manifest = Manifest.model_validate_json((directory / "manifest.json").read_bytes())
    bodies: dict[str, tuple[Artefact, bytes]] = {}
    for source in manifest.sources:
        path = (directory / source.file).resolve()
        if not path.is_relative_to(directory.resolve()):
            raise ValueError("artefact_path_invalid")
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != source.sha256:
            raise ValueError("artefact_digest_mismatch")
        bodies[source.sha256] = source, body
    verified = regional = 0
    for item in load_referrals().records:
        if item.status != "VERIFIED":
            continue
        if item.source_sha256 is None:
            raise ValueError("source_missing")
        source, body = bodies[item.source_sha256]
        if source.url != item.source_url or source.observed_on != item.verified_on:
            raise ValueError("source_observation_mismatch")
        parser = Text()
        parser.feed(body.decode("utf-8-sig"))
        text = " ".join(" ".join(parser.parts).split())
        for phone in ((item.phone,) if item.phone else ()) + item.additional_phones:
            digits = re.sub(r"\D", "", phone)
            pattern = r"(?<!\d)" + r"[\s()+-]*".join(digits) + r"(?!\d)"
            if not re.search(pattern, text):
                raise ValueError("phone_not_in_source")
        if item.kind == "regional":
            if item.directory_sha256 is None or item.directory_url is None:
                raise ValueError("directory_missing")
            evidence, kml = bodies[item.directory_sha256]
            if evidence.url != item.directory_url or evidence.observed_on != item.verified_on:
                raise ValueError("directory_observation_mismatch")
            map_id = parse_qs(urlsplit(item.directory_url).query).get("mid", [""])[0]
            if not map_id or map_id not in body.decode():
                raise ValueError("publisher_directory_link_missing")
            ns = {"k": "http://www.opengis.net/kml/2.2"}
            places = ElementTree.fromstring(kml).findall(".//k:Placemark", ns)
            name = item.organisation.removeprefix("Legal Aid Commission of Sri Lanka — ")
            matches = [place for place in places if place.findtext("k:name", namespaces=ns) == name]
            if len(matches) != 1 or item.phone is not None or item.additional_phones:
                raise ValueError("regional_identity_or_phone_invalid")
            fields = {
                entry.get("name"): entry.findtext("k:value", default="", namespaces=ns)
                for entry in matches[0].findall(".//k:Data", ns)
            }
            if fields.get("Address") != item.address:
                raise ValueError("regional_address_mismatch")
            regional += 1
        elif item.address and item.address not in text:
            raise ValueError("address_not_in_source")
        verified += 1
    return verified, regional


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    try:
        verified, regional = audit(args.directory)
    except Exception:
        print(json.dumps({"error": "referral_evidence_check_failed"}))
        return 2
    print(
        json.dumps(
            {
                "verified_listings_checked": verified,
                "regional_locations_checked": regional,
                "scope": "stored_bytes_and_listing_fields",
                "live_availability": "UNVERIFIED",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
