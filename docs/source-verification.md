# Source verification register

The table preserves the project brief's research inputs and their T1 verification
requirements. T2 metadata observations below update the dataset discovery and
counts. Legal status and retrieval performance remain UNVERIFIED. The follow-up
below records checked publisher contact listings with explicit limits. Nothing
here authorises display as verified law or guarantees a contact's availability.
Future checks must record source, inspected content, date and reviewer role.
Verified legal claims use `[PERISHABLE: verified YYYY-MM]` after that check.

| ID | Brief-supplied assertion | Required verification and delivery |
| --- | --- | --- |
| S01 | Sri Lanka Document Datasets, 215,670 documents / 60.3 GB / 13 datasets, Sinhala/Tamil/English, MIT, daily updates, GitHub and HuggingFace under nuuuwan | T2 actual repository/file and licence inventory, source dates and hashes |
| S02 | Acts 3,928, 1981–2025; Supreme Court judgments 1,575, 2016–2025; Appeal Court judgments 10,146, 2012–2025; extraordinary gazettes 101,532, 2010–2025; bills 4,077; Hansard 1,665 | T2 count what exists, inspect schemas, distinguish legal authority and source canonicality |
| S03 | Upstream GitHub Actions/Selenium/PyMuPDF pipeline, normalised title/date/source/language/hash JSON, preserved artefacts and idempotence | T2 inspect actual pipeline and representative files, with personal data excluded from logs |
| S04 | OCR unfinished, legacy-font and Sinhala/Tamil parsing weaknesses, no consolidation | T2 sample quality assessment and explicit graph/coverage gaps |
| S05 | Kelaniya government-context benchmark, August 2026, 500 human-verified queries and 1,699 contexts; BGE-M3 Sinhala R@1 59.4, R@5 90.2, R@15 96.2; Tamil R@15 95.6; monolingual R@15 8.2; multilingual-E5 73.0, LaBSE 72.4, NLLB query-translation 87.0 Sinhala | Locate paper and metric definitions. T3/T8 re-benchmark legal text. These figures establish no prototype accuracy |
| S06 | PDPA Act No. 9 of 2022 amended by Act No. 22 of 2025 | T7 inspect Acts and Authority publications; identifiers are copied research leads, not verified legal citations |
| S07 | Gazette 2498/16 of 22 July 2026 commences sections 2 and 3, Part I and Part III on 1 January 2027; Part V in force from 17 July 2023; Part II rights and Part VII penalties awaiting an order | T7 authoritative gazette/Authority verification and qualified interpretation. Every date and effect remains UNVERIFIED |
| S08 | Lawful basis/minimisation, section 11/Schedule V notice with automated-logic information, section 12 DPMP, section 20 DPO for specified processing, section 24 prior impact assessment, section 23 breaches, section 26 cross-border instruments | T7 primary-text mapping, DPIA/DPMP/notice/breach skeletons and questions for counsel. Do not assert compliance from this list |
| S09 | Legal Aid Commission provides free advice and lawyers, with regional counters | T4 verify current service description, numbers and regional routes against Ministry/Commission sources, store versioned records |
| S10 | Bar Association of Sri Lanka can provide a route to attorney review | Verify official referral/review approach and terms. No representation or partnership is implied |
| S11 | UNDP Reimagining Legal Aid in Sri Lanka prioritises a hotline and digital intake within 12 months | T8 verify current programme/publication and write a conditional integration/partnership approach |

Starting locations below are research leads. T1's network probe and any denials
are recorded in the turn log. Reachability alone never verifies page content.

- Upstream account discovery begins at GitHub and HuggingFace. [GitHub](https://github.com/nuuuwan) · [HuggingFace](https://huggingface.co/nuuuwan)
- Referral verification begins with the responsible public bodies. [Ministry of Justice](https://moj.gov.lk) · [Legal Aid Commission](https://legalaid.gov.lk)
- PDPA verification begins with the responsible authority. [Data Protection Authority](https://www.dpa.gov.lk)

No hotline number, case name or purported authoritative legal extract is included
in the prototype. Uncertainty remains visible until evidence is obtained.

## T2 metadata observations on 18 November 2026

S01–S04 have partial direct evidence in `corpus-inventory.md`. The actual index
is `nuuuwan/lk_datasets`, with 26 reported datasets and 303,457 document rows.
The complete inspected Acts TSV contains 3,979 language-version rows. The
government Acts data begins in 1981, while a distinct Parliament pipeline reports
older metadata and incomplete extraction. Both layouts were sampled. The
inspected code-repository licences declare MIT. Original PDF rights remain
UNVERIFIED.

English, Sinhala and Tamil source extracts were measured. The Sinhala/Tamil
samples contain replacement characters, and an older English sample has
ambiguous section ordering. These observations support explicit quality and
structural quarantine. The source report records hashes and commits. Full-corpus
coverage, upstream update guarantees, engine reproducibility, maintainer-specific
collections and HuggingFace contents remain UNVERIFIED.

S05–S11 remain pending their scheduled primary-source or measurement work. No
PDPA commencement, statute applicability or referral number was verified in T2.

## T4 referral attempts on 18 November 2026

S09 and S10 remain UNVERIFIED. Direct HTTPS requests to `https://moj.gov.lk/`,
`https://legalaid.gov.lk/` and `https://basl.lk/` each failed with curl exit 56,
CONNECT tunnel response 403 and HTTP result 000. The running policy was observed
restricted/enforced and omitted these domains. No primary page was inspected.

The user approved these three domains and their `www` forms. The setup tool
confirmed a saved restricted-network draft preserving package-manager presets.
Its save does not apply live settings or publish a version. Verification must
resume after the settings are applied. Legal Aid Commission service scope,
eligibility, regional counters, current contacts, emergency routes and the Bar
Association review/referral service remain UNVERIFIED. No partnership is asserted.

`src/lai/triage/data/referrals.json` records pending research targets, attempted
dates and blockers. These are excluded by `active_referrals`. There are no active
phone numbers, addresses, hours or regional-service claims. See `docs/safety.md`
for the evidence/expiry contract and the remaining primary-source procedure.

## T4 referral follow-up — 19 November 2026

The user's published environment is a different instance, observed with current,
enforced unrestricted networking. The prior destination-policy blocker is
resolved for the Ministry, Commission, BASL and inspected emergency publishers.
No environment configuration change or publication was performed by the agent.

S09 now has directly inspected listing evidence: the Commission contact page,
its publisher-linked 85-entry map (84 regional locations plus head office), and
the Ministry's Commission page. Regional phones are withheld because map values
use scientific notation and the head-office map value matches a fax. The
Ministry's older contacts/count/income threshold do not establish current
eligibility. Source bytes, exact links and hashes are recorded in
`referral-verification.md`; live access/eligibility remain UNVERIFIED.

S10 has a checked BASL general-office listing. A dedicated attorney review/
referral programme or partnership commitment was not established. Police, NCPA,
NIMH and Suwa Seriya pages supply five distinct scoped emergency/support records.
Specialist urgent routes for detention and destitution remain UNVERIFIED pending
safeguarding review. No telephone call, email or institution outreach was made.

The user supplied three distinct corpus repository URLs and instructed use of
both those links and T2, with official publishers governing conflicts. See the
dated inventory reconciliation. Reviewer availability was confirmed by the user;
actual reviews, template approvals and all launch flags remain pending.

## T7 PDPA inspection — 19 November 2026

The current enforced unrestricted environment reached the official Authority.
S06 document identities and specific S07 order wording now have inspected primary
PDF evidence: Act No. 9 of 2022, Amendment Act No. 22 of 2025, gazettes 2341/59,
2366/08, 2427/34 and 2498/16, and Circular 01/2026. Exact URLs, byte hashes,
findings/limits and the S08 amended-section mapping are in
`pdpa-verification.md`. `[PERISHABLE: verified 2026-11]` applies there only to
the specified inspected text observations, not overall legal compliance.

Gazette 2498/16 appoints 1 January 2027 for sections 2/3, Part I and Part III;
the older March 2025 paragraph was expressly repealed. The complete current
status of Parts II/VII, subsequent orders and binding final rules remains
UNVERIFIED. The later-dated circular's general wording about expected dates is
an explicit source inconsistency. Counsel must resolve completeness/application.
T7's DPIA, DPMP, Schedule V notice and breach runbook are unapproved skeletons;
all launch flags remain closed. No invented notification deadline or lawful
basis was selected. No institution was contacted.
