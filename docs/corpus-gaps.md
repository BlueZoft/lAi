# Corpus coverage and gap register

Status is OPEN and UNVERIFIED on 18 November 2026. No real corpus is loaded and
no domain is enabled. The brief reports upstream Acts starting in 1981 and
judgments/gazettes with later coverage. T2 must inventory the actual files and
sources before this becomes a measured coverage report.

| Gap | Why it matters | Planned closure evidence | Accountable role |
| --- | --- | --- | --- |
| Foundational prescription and limitation instruments, often pre-1981 | Missing law could cause false reassurance about time limits | Authoritative text, amendments and commencement evidence, section anchors and attorney review; retain hard limitation warning | Corpus steward and reviewing attorney |
| Penal and criminal-procedure instruments | High-risk criminal matters can exceed source coverage | Source and version evidence; criminal-defence requests remain escalation-only | Corpus steward and reviewing attorney |
| Civil procedure | Procedural content may be historically incomplete | Verified foundational text and later changes, with reviewed administrative scope | Corpus steward and reviewing attorney |
| Land-related foundational instruments | High-risk disputes and older instruments | Domain-specific authoritative inventory and review before enabling any coverage | Corpus steward and reviewing attorney |
| Labour and employment foundations | Later amendments may omit the governing older instrument | Original text plus amendment/commencement chain and review | Corpus steward and reviewing attorney |
| Sinhala and Tamil versions | Translations, legacy fonts and tokenisation can break alignment | Version/language identity and competent bilingual review, verified conversion or quarantine | Language and corpus reviewers |
| Scanned or garbled documents | OCR may be absent or unusable | Measured extraction quality, quarantined failures and human-checked samples outside Git | Corpus engineering |
| Consolidated status | Sources may contain amendments without current consolidated text | Version graph with explicit unknowns and evidence-backed edges | Corpus engineering and reviewing attorney |
| Administrative source freshness | Offices, fees and timelines change | Dated official source evidence and refresh policy for every offered task | Source steward |

## Manual seeding path planned for T2

1. Register the gap and intended administrative domain. Locate an authoritative
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

T2 implements this path and a synthetic demonstration. T1 supplies no guessed
statute number, section, case citation or claim of current applicability.
