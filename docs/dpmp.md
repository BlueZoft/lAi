# Data Protection Management Programme — draft

19 November 2026. Incomplete governance skeleton for PDPA section 12, read with
the 2025 amendment and inserted section 51A. See `pdpa-verification.md` for
inspected text and unresolved commencement/final instruments. No compliance
certification or release approval is implied.

| Owner role | Required responsibility | Current state |
| --- | --- | --- |
| Controller / accountable operator | Purposes, bases, notice, rights, processor selection and risk acceptance | UNASSIGNED; maintainer is engineering owner only |
| Qualified counsel | Applicability, categories, commencement/rules, DPO criteria, rights/breach decisions | Review available in the user's team; no actual approval recorded |
| DPO or responsible privacy contact | Advice, monitoring, training, assessment and Authority liaison as applicable | Designation/qualification/contact UNVERIFIED |
| Engineering maintainer | Locked builds, source provenance, offline controls, tests, restore evidence, safe change review | Private synthetic controls executed; laptop evidence pending |
| Attorney/Sinhala/safeguarding reviewers | Taxonomy, safety, gloss, language and referral suitability | Available; approvals remain pending |

Maintain a dated processing inventory using `dpia.md`: purpose, categories,
subjects (including children/third parties), recipients, retention, locality,
basis/conditions, risk, safeguards and evidence. Separate source ingestion,
private model research, runtime navigation, operations and any future institution
handoff. Record vendors/processors and their contracts before access. No paid
runtime API, cross-border query transfer or real personal sample is authorised.

| Control cycle | Owner action / retained evidence |
| --- | --- |
| Before any real use | Complete DPIA/notice/bases and DPO decision; actual legal/language/safeguarding review, laptop isolation/restore tests and all T8 gates |
| Every code/config/model change | Conventional commit, offline tests/CI, version/hash pins, source/legal currency review where affected; reassess changed processing |
| Every local startup | Owner-only paths, no unexpected published ports/interfaces, source mounts/credentials, stale sockets; keep default copy/navigation closed |
| Daily when operating | Run scoped retention preview/apply through the owner account; confirm success without recording file contents; failure stops claims of timed deletion |
| At least weekly while piloting | Check pending source/referral expiries and alerts, counters only, installed controls and secrets permissions; no query/identity sampling |
| Before relying on recovery / after relevant change | Encrypted synthetic restore in a fresh test project; verify logical hashes and corruption rejection; separate key-custody drill |
| On incident or rights request | Use counsel-led runbook/rights workflow; collect minimum needed incident/contact metadata separately under a justified retention decision |

Privacy policy is `config/privacy-policy.json`: no server query persistence,
accounts or browser storage; five-minute browser inactivity clearing; one-hour
optional metrics retention; seven-day owned operations reports/encrypted backups.
`lai.operations.retention` defaults to preview and touches only timestamped files
under marked owned directories. Installation of a daily scheduler and monitoring
of its success belong to the laptop operator. Corpus/provenance and keys are
excluded from automatic deletion; they need an explicit inventory/rotation policy.

Rights workflow: publish a real controller/privacy contact only after review.
Explain that the navigator holds no identifiable session history; never invent
an account lookup or retain new IDs merely to prove a nonexistent record. Have
counsel decide proportionate identification, applicable rights, requests about
public-source content, response/extension/appeal periods under amended section
17, erasure exceptions and current commencement. Keep any necessary manual
request record separate, minimal, access-limited and subject to its own policy.
No request form or contact transmission is enabled by this draft.

Training covers non-authoritative scope, urgent-route preservation, no raw
query/debug logs, no screenshots/real examples in tickets, verification rather
than guessed law/contacts, source rights, key custody and breach escalation.
Record only role/date/version/evidence references, without reviewer personal
details in Git. Complaints, audit outcomes and improvement actions need an
operator-owned register; no real complaint data belongs in repository fixtures.

The programme remains incomplete until the accountable operator and counsel
accept the actual processing and evidence. The maintainer must not describe this
document or its tests as proof of legal compliance.
