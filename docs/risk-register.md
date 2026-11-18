# Risk register

All owners below are accountable roles, with no individual assigned yet. Every
item is OPEN on 18 November 2026. T1 implements the release restriction, with
the remaining controls assigned to their delivery turns.

| ID | Harm | Mechanism | Mitigation and evidence | Owner |
| --- | --- | --- | --- | --- |
| R01 | User relies on invented legal advice | Model generates a conclusion, deadline or recommendation | T4 deterministic forbidden classes, T5 verbatim assembly and reviewed glosses, T6 bounded contracts and fallbacks | Safety engineering and reviewing attorney |
| R02 | Crisis help is delayed | Retrieval/model executes for urgent distress | T4 six immediate-escalation classes and downstream-call spy tests with malformed/adversarial input | Safety engineering and safeguarding reviewer |
| R03 | Outdated law is presented as current | Flat corpus ignores amendment or commencement | T2 version graph, uncertain states, source evidence and staleness; T3/T5 gate display | Corpus engineering and reviewing attorney |
| R04 | Missing foundational law produces false reassurance | Upstream pre-1981 gaps or incomplete domain coverage | Explicit gap register, manual seeding, domain eligibility and attorney-approved closure | Corpus steward |
| R05 | Sinhala intent maps to the wrong source | Cross-lingual retrieval or transliteration errors | Multiple candidates, hybrid ranking, confidence abstention and real legal golden set | Retrieval engineering and Sinhala reviewer |
| R06 | Corrupted text is displayed as law | Scanned PDFs, empty extraction or legacy encodings | T2 quality score, verified conversion or quarantine and section/source anchors | Corpus engineering |
| R07 | Personal or sensitive facts escape | Query logs, analytics, inference APIs, backups or sessions | Local runtime, no paid/remote model path, ephemeral use, T7 egress tests, minimised logs and deletion tests | Operations and privacy reviewer |
| R08 | Human help cannot be reached | Stale numbers or invented contact data | T4 primary-source verified, dated referral directory and recheck policy; absent contacts stay unavailable | Referral steward |
| R09 | Compliance is overstated | Perishable PDPA facts copied without verification or legal interpretation assumed | Source register, T7 skeletons, DPIA and qualified counsel questions | Privacy lead and qualified counsel |
| R10 | Laptop becomes unusable or disrupts live services | Models exceed 4 GB VRAM or stack targets production | TARGET B measurements and budgets, sequential residency, dedicated local synthetic stack, production off limits | Operations |
| R11 | Private data or oversized assets enter history | Corpus/model/database artefacts or secrets committed | Ignore rules, file category/size guard and staged review; T7 safe logging; no LFS | Maintainer |
| R12 | Prototype is mistaken for validated public service | Attractive demo or repository claims obscure gaps | Exact launch gate in README, strict defaults, explicit implemented/planned status, private repository recommendation | Maintainer and reviewing attorney |
| R13 | Malicious source content controls the system | Retrieved text contains prompt instructions or false citations | Treat source text as data, deterministic assembly, version/hash anchors and constrained model contracts | Corpus and model engineering |
| R14 | An amendment changes a previously reviewed explanation | Gloss keyed only to a section number | Version/hash-bound gloss review, invalidation on text change, text-and-referral fallback | Template steward and reviewing attorney |

The repository file guard enforces file categories, size and simple binary/LFS
checks. It cannot establish absence of arbitrary secrets or personal information.
Human staged-content review remains required. No legal accuracy or safety
validation for real user scenarios has been completed.

T4 adds executed spy tests for R01/R02 and review/expiry gates for R08/R12.
All risks remain OPEN. Lexical coverage has unmeasured false negatives and false
positives; fixed Sinhala/English copy has no completed human review; official
referral verification is blocked by live network access. Navigation and public
release remain disabled. See `safety.md` and `turn-logs/T4.md` for evidence.
