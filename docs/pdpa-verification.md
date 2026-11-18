# PDPA source inspection — 19 November 2026

This is an engineering evidence record, not advice on applicability or compliance.
Primary document text was inspected from the responsible Authority's official
site. The source bytes and pdftotext output stay in ignored
`data/research/pdpa/2026-11-19/`. No real user/judgment data was fetched.
Recheck before deployment and have qualified Sri Lankan counsel interpret the
amended provisions, commencement orders, applicable rules and this processing.

## Sources actually read

The official [home page](https://www.dpa.gov.lk/) and
[publications page](https://www.dpa.gov.lk/guidelines.php) link the Acts, gazettes
and Circular below. HTTPS verification remained enabled. Successful GETs and
local PDF extraction established content access; no approval/notification was sent.

| Document / official URL | SHA-256 of inspected bytes |
| --- | --- |
| [Act No. 9 of 2022, English](https://www.dpa.gov.lk/acts/Data%20Protection%20Act%20SL%20-%20English%20%282%29.pdf) | `6fcdf94fe219d9f7cd18c4790a2c6332568c65eb72846790480e65834012ef46` |
| [Amendment Act No. 22 of 2025, English](https://www.dpa.gov.lk/acts/22-2025_E_251104_201549%20%281%29.pdf) | `675ec8209637f46e81bab7f8fad12e4b8acae3e1a202120d975534e2f7db2c76` |
| [Gazette 2341/59, 21 July 2023](https://www.dpa.gov.lk/Gazet/2023-07-21/2341-59_E.pdf) | `9c6b735cc61f9cd8dc931229b5c7431b975c4ce8f96ba347ce796f110201af75` |
| [Gazette 2366/08, 8 January 2024](https://www.dpa.gov.lk/Gazet/2024-01-08/2366-08_E.pdf) | `af3dc69a4609e4d11e107d3603a1b5e8df2477527d77d9ed84d60d316a146996` |
| [Gazette 2427/34, 14 March 2025](https://www.dpa.gov.lk/Gazet/G%2043988%20%28E%29.pdf) | `072919a6a6b087bc68cbc455c4961cf5c543e57ea5f2e12a8dcf1d70452e3ca8` |
| [Gazette 2498/16, 22 July 2026](https://www.dpa.gov.lk/Gazet/2498-16_E.pdf) | `f25195fe858458a92963951d6661e1f5c0800ab747d884102c2296fcf1eda276` |
| [DPA Circular 01/2026, 7 August 2026](https://www.dpa.gov.lk/media/DPA_Circular_012026_E.pdf) | `b755bde3d3c229957b7f66ac454c1ca7f28c6509319044d1ae49cce36be17a54` |
| Official home HTML | `7899e3076a4a0fb0ab4cbe482aacebb88e0a515babb8fef26dd1355a7a9dcd97` |
| Publications HTML | `b73acbd54c0a1db3672c87030edb7f20d2ccea8bd80942eb5d0d338fb4d64901` |

`pdftotext -layout` was used for each of the seven PDFs. Hashes establish byte
identity; these English copies do not replace review of prevailing-language
texts or establish an exhaustive legal search.

## Findings and limits

**S06 [PERISHABLE: verified 2026-11] — document identities.** The inspected
principal Act is titled Personal Data Protection Act, No. 9 of 2022. The
amendment is Act No. 22 of 2025, certified 30 October 2025. Its section 2 replaces
principal section 1(3), repeals subsections (4)/(5) and includes a saving for
things duly done under Parts V, VI, VIII, IX and X. It is unsafe to use the
original Act alone as a consolidated current text.

**S07 [PERISHABLE: verified 2026-11] — contents of the inspected orders.**

- Gazette 2341/59 appoints 17 July 2023 for Part V.
- Gazette 2366/08 paragraph (a) appoints 1 December 2023 for Parts VI, VIII, IX
  and X; paragraph (b) originally appointed 18 March 2025 for Parts I, II, III
  and VII. The PDF has an inconsistent older running header; the numbered
  order and its body were inspected rather than trusting that header.
- Gazette 2427/34 expressly repeals paragraph (b) of that order. Do not retain
  the original March 2025 date as current merely because an old page quotes it.
- Gazette 2498/16 appoints **1 January 2027 for sections 2 and 3, Part I and
  Part III**. That is the text of this particular order, not an assertion that
  every provision is currently operational or that no later order exists.

The statement that Parts II/VII still await an order remains **UNVERIFIED as a
complete current-status claim**: no such later order was identified in the
bounded publisher listing/inspected documents. Absence from that sample proves
no exhaustive negative. Counsel must check subsequent gazettes and the effect
of savings/amendments before any real processing.

Circular 01/2026 section 2.2 says new dates are expected soon despite its date
being after Gazette 2498/16. This is a source inconsistency to resolve with
counsel/the Authority, not a reason to silently replace the gazetted order with
the circular's general wording. No institution was contacted.

**S08 [PERISHABLE: verified 2026-11] — inspected text mapping only.**

| Principal provision | Observed text / 2025 amendment | Engineering material |
| --- | --- | --- |
| Sections 5–10; Schedules I/II | Lawfulness, purposes, accuracy, retention, integrity/confidentiality; categories/bases need counsel selection | DPIA processing inventory; minimisation and retention controls |
| Section 11; Schedule V | Transparency; Schedule V items 1(a)–(m) and indirect collection items 4–6 | `privacy-notice.md`; no blanket claim that every automated system meets section 18 |
| Section 12 | DPMP internal controls; amendment section 3 repeals 12(2), section 11 inserts guideline power 51A | `dpmp.md`; do not rely on repealed 12(2) alone |
| Sections 13–19 | Rights, automated decisions, requests/appeals; amendment sections 4–6 alter 17–19 | Manual rights workflow and counsel questions; application/commencement to confirm |
| Section 20 | DPO criteria/functions; amendment section 7 changes categories and functions | Determine designation with counsel; no claim an entry-level maintainer is a qualified DPO |
| Sections 21–22 | Controller/processor obligations and contractual/instruction boundaries | Operator/processor register and conditional institutional agreement |
| Section 23 | Breach notification details/time depend on rules | `breach-runbook.md`; no invented statutory 72-hour period |
| Section 24 | DPIA; amendment section 8 changes DPO wording and replaces 24(5) with submission on written request | `dpia.md`; draft is not completed/approved DPIA |
| Section 25 | Amendment section 9 removes several prior-consultation subsections | Counsel must interpret the amended mechanism; do not implement obsolete original wording |
| Section 26 | Replaced by amendment section 10: cross-border flows, instruments, exceptions/public-authority provisions | Project deliberately prohibits query egress; this is a product constraint, not a claim PDPA categorically bans cloud services |

The publications page labels several DPIA, breach, DPO, appeals and cross-border
instruments as **draft/public consultation**. We inspected that listing, not a
complete final-instrument register. Binding final rules, forms, notification
deadlines and cross-border directives remain UNVERIFIED. The public-sector
circular is contextual guidance; do not infer that this prototype is a public
authority or can adopt its conclusions without an operator-specific assessment.

## Recheck procedure

Re-fetch official linked Acts/orders, retain date/URL/bytes/digests outside Git,
read operative text and amendments, and compare language versions with counsel.
Search current gazette/Authority publications for later orders and final rules.
Record both conflicts and unresolved searches. Update this mapping only on actual
evidence; `config/launch-gate.json` stays closed until independent review and the
full launch prerequisites are satisfied. T7 documentation does not set
`dpia_complete` or establish legal compliance.
