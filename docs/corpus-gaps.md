# Corpus coverage and gap register

Status is OPEN on 18 November 2026. No domain is enabled. T2 inspected the
government-document Acts index starting in 1981 and a separate Parliament
pipeline reporting metadata back to the 1940s. The latter's older metadata has
incomplete PDF and extraction coverage. Foundational instruments and their
version chains remain UNVERIFIED. One real English research acquisition was
staged in quarantine. See `corpus-inventory.md` for the measured scope.

| ID and gap | Why it matters | Required closure evidence | Accountable role |
| --- | --- | --- | --- |
| `gap-limitation` — foundational prescription and limitation | Missing law could cause false reassurance about time limits | Authoritative text, amendments and commencement evidence, section anchors and attorney review, retaining the hard limitation warning | Corpus steward and reviewing attorney |
| `gap-criminal` — penal and criminal procedure | High-risk criminal matters can exceed source coverage | Source and version evidence, with criminal-defence requests remaining escalation-only | Corpus steward and reviewing attorney |
| `gap-civil` — civil procedure | Procedural content may be historically incomplete | Verified foundational text and later changes, with reviewed administrative scope | Corpus steward and reviewing attorney |
| `gap-land` — land-related foundations | High-risk disputes and older instruments | Domain-specific authoritative inventory and review before enabling coverage | Corpus steward and reviewing attorney |
| `gap-employment` — labour and employment | Later amendments may omit the governing older instrument | Original text plus amendment/commencement chain and review | Corpus steward and reviewing attorney |
| `gap-languages` — Sinhala and Tamil versions | Legacy fonts and tokenisation can break alignment | Version/language identity and competent bilingual review, verified conversion or quarantine | Language and corpus reviewers |
| `gap-ocr` — scanned or garbled documents | OCR may be absent or unusable | Measured extraction quality, quarantined failures and human-checked samples outside Git | Corpus engineering |
| `gap-consolidation` — consolidated status | Sources may contain amendments without current consolidated text | Version graph with explicit unknowns and evidence-backed edges | Corpus engineering and reviewing attorney |
| `gap-administrative-freshness` — administrative sources | Offices, fees and timelines change | Dated official source evidence and refresh policy for every offered task | Source steward |

## Manual seeding path

1. Use a stable gap ID above and record the intended administrative domain. Locate an authoritative
   source and record acquisition permission and licensing evidence.
2. Fetch explicitly into ignored `data/raw/`, retaining original bytes outside
   Git. Never put real source excerpts or personal data in fixtures or logs.
3. Produce a manifest with canonical URL, publisher, acquisition time, content
   hash, source revision, instrument identity, language and verification state.
4. Extract, assess quality and detect legacy fonts. Quarantine uncertain text.
5. Parse section boundaries and anchor text to its source. Link amendments and
   commencement only when the supporting source has been inspected.
6. Seek attorney and language review. Record review evidence and unresolved gaps.
   Domain eligibility stays closed until every required source/version gap is
   closed. A new document alone does not close the gap.

Set `acquisition` to `manual_seed` and supply `gap_ids` in the source manifest.
The CLI rejects an unmapped manual seed. Tests exercise an invented pre-1981
instrument and retain its mapping. No real gap has been closed. The complete
operator path is in `corpus-intake.md`. Attorney-reviewed closure evidence must
cover every source/version/language requirement for each offered domain.
