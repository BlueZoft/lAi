# Legal Aid Dialogue publication verification

19 November 2026 (Asia/Colombo). This follow-up closes the publication-search
gap recorded in T8. The inspected UNDP publications establish a reform
recommendation, not a currently operating service, procurement programme or
commitment to integrate LAi. No institutional message or telephone call was made.

## Primary sources inspected

UNDP's public site-search client returned the actual publication URLs. Search
results were used for discovery only; the publisher pages and their directly
linked PDFs were fetched separately with TLS verification enabled. The three
pages and two PDFs are retained outside Git in
`data/research/partnership/2026-11-19/follow-up/`, with a local evidence manifest.

| Source | Publisher date shown | SHA-256 of inspected bytes |
| --- | --- | --- |
| [Reimagining Legal Aid in Sri Lanka](https://www.undp.org/srilanka/publications/reimagining-legal-aid-sri-lanka) | 12 July 2026 | `bf0cd2e7ffe6efbe5674fb70d3e8f01de52bb2695f391e1d07a73f4795d00e19` |
| [Reimagining Legal Aid in Sri Lanka—Summary](https://www.undp.org/srilanka/publications/reimagining-legal-aid-sri-lanka-summary) | 12 July 2026 | `5d1054bd51fd781cbaf3efbdeec2a9f1db1bbd2254a0b84e2028d4ac4c4ec24b` |
| [Legal Aid Dialogue: Reimagining the Future of Access to Justice in Sri Lanka](https://www.undp.org/srilanka/press-releases/legal-aid-dialogue-reimagining-future-access-justice-sri-lanka) | 23 February 2026 | `12824fb5fe7487a9892b7a34237aee812a16bc8bdcb0f2a88f3bd9e907902803` |
| [Full report PDF](https://www.undp.org/sites/g/files/zskgke326/files/2026-07/legal_aid_dialogue-long_report.pdf) | Linked from full-report page | `5cd241e5ada4df60ab1e9e37ed250290036a8cc8172a043bdcd276c66f48cbb1` |
| [Summary PDF](https://www.undp.org/sites/g/files/zskgke326/files/2026-07/legal_aid_dialogue-short_report.pdf) | Linked from summary page | `0fbdfcc4fc123784072e0b94ec725658470c48dc4af3d43a2907c85d0a73605f` |

The press release describes the Dialogue on 20–21 February 2026, convened by
the Legal Aid Commission with the Support to Justice Sector Project (JURE),
funded by the European Union, in partnership with the Ministry of Justice and
implemented by UNDP and UNICEF Sri Lanka. This describes the Dialogue's
institutional context. It does not make LAi a participant or partner.

## What S11 now supports

**[PERISHABLE: verified 2026-11] — publisher and document-text observations.**
The summary PDF's physical page 7 is headed **“Priority Actions (2026–2028)”**.
Under **“Immediate (within 12 months)”**, its first bullet is:

> launch legal aid hotline and digital intake system;

This wording was checked both in `pdftotext -layout` output and by viewing a
rendering of page 7. The full report, physical page 8, paragraph 35, also
describes proposed multi-point referral pathways and digital intake mechanisms
such as hotlines and online platforms, with staffing, travel and data-protection
constraints. The summary's physical page 5 lists intake/referral SOPs and legal
aid hotlines/digital access platforms among priority actions.

S11's report-existence and immediate-priority wording therefore have primary
publication evidence. The earlier broad label “UNDP programme” should be read
more precisely as an **UNDP-published Legal Aid Dialogue reform recommendation**.
The “within 12 months” wording is a reported planning horizon. The inspected
text does not establish an implementation date or the date from which to count
that horizon; no calendar launch deadline is derived here.

## What remains UNVERIFIED

- Whether the proposed hotline or digital intake system is now operational,
  its operator, number/URL, eligibility, hours, safeguarding or service quality.
- Current implementation/funding/procurement decisions, an available technical
  interface or permission for a third-party connector.
- Any UNDP/LAC/BASL commitment to LAi, partnership agreement, referral acceptance,
  attorney review programme or approval to process/forward personal information.

Do not add a hotline number or active referral from this recommendation. Keep
the existing expiry/scope-gated referral register unchanged. Official listing
checks in T4 remain distinct from live availability and reviewer acceptance.

The conditional approach in `partnership.md` can now cite this published
priority, while actual implementation and any future handoff require separate
verification, institutional agreement, privacy/safeguarding review and explicit
user direction for outreach. NO-GO and all existing launch/review flags remain
unchanged. The published T8/prototype tags preserve the earlier evidence state;
this follow-up does not move those tags or claim their source search had succeeded.
