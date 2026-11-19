# T8 follow-up — Legal Aid Dialogue primary publication

19 November 2026 (Asia/Colombo). The user requested continuation after inspecting
existing work. Inspected clean `main` at
`37fb8e842ef62f750beaadde9749a1e1648afd79`, AGENTS/NEXT/ROADMAP/HANDOFF,
decisions, T8 evidence and source/review registers. Native remote reads confirmed
main plus both peeled T8/prototype tags matched. T1–T8 engineering was complete;
actual reviews, legal labels, source/referral gaps and laptop evidence remain.
No existing implementation, tag, setting or review approval was reapplied.

The next independently actionable backlog item was S11's primary-publication
search. This follow-up does not fabricate the legal golden set or perform the
reviewer's work. No runtime/model/corpus/stack change was needed.

## Investigation and finding

The publisher's home page and global search page were accessible. Google/Bing/
DuckDuckGo discovery attempts did not yield usable source candidates. Headless
Chromium could not validate the publisher certificate in its own trust store;
validation was not disabled. No CA/system/network configuration was changed.

Read the publisher's actual JavaScript search configuration/client through
TLS-verified curl and used its public search interface for the intended public
query. Search results supplied the correct full-report, summary and press-release
URLs. Fetched each publisher page and the two directly linked PDFs separately.
The earlier guessed 404 URLs were therefore not evidence that publications were
unavailable. Search results themselves were not used as content verification.

Both publication pages display 12 July 2026. The press release displays 23
February 2026 and describes the Dialogue on 20–21 February. The summary PDF's
physical page 7 lists “launch legal aid hotline and digital intake system” under
“Immediate (within 12 months)” within its 2026–2028 priorities. Verified the
wording in extracted text and by viewing a rendering of that page. Physical page
5 also lists intake/referral SOPs and legal aid hotlines/digital access platforms.
Full-report physical page 8, paragraph 35, describes proposed digital intake/
multi-point referral mechanisms and constraints.

S11's publication/recommendation wording is now supported by actual primary
evidence. Current implementation, operating channels, service terms, technical
interfaces and any agreement with LAi remain UNVERIFIED. No launch calendar date,
hotline number or programme/integration commitment was inferred. No institutional
message/call, automatic forwarding, visibility change or publication occurred.

## Executed verification

Used bounded curl GETs with TLS verification enabled for the three exact pages
and two PDFs listed in `docs/partnership-verification.md`. Each successful source
request used `--fail --silent --show-error --location --max-time 25` (30 for PDFs).
Raw discovery and publisher artefacts stay ignored under
`data/research/partnership/2026-11-19/follow-up/`. The temporary decoded search
configuration was discarded after discovery; no API configuration was added to Git.

Executed extraction, locator checks and visual inspection:

```sh
pdftotext -layout data/research/partnership/2026-11-19/follow-up/long-report.pdf data/research/partnership/2026-11-19/follow-up/long-report.txt
pdftotext -layout data/research/partnership/2026-11-19/follow-up/short-report.pdf data/research/partnership/2026-11-19/follow-up/short-report.txt
pdfinfo data/research/partnership/2026-11-19/follow-up/short-report.pdf
pdftoppm -f 7 -l 7 -scale-to 1800 -singlefile -png data/research/partnership/2026-11-19/follow-up/short-report.pdf /tmp/lai-partnership-priorities
make hygiene
git diff --check
```

Viewed `/tmp/lai-partnership-priorities.png`. Summary is ten PDF pages and
891,532 bytes; full report is 514,575 bytes. A local mode-0600 manifest records
all five exact source URLs/byte sizes/digests. Independently re-read its entries
and checked all byte hashes, both publisher-to-PDF links and the three physical
page locators. Output:

```text
Audited 5 primary artefact digests, 2 publisher-to-PDF links and 3 physical-page locators; public search configuration discarded
Repository hygiene passed (184 files; 1 MB cap)
```

That hygiene count precedes this log; staged hygiene follows. Documentation-only
source corrections need no new unit tests or repeat of model/DB/browser runtime
acceptance. The full existing CI suite still runs on each push and tag. No claim
of a fresh local `make verify`, legal recall, current service availability or
independent review is made here.

## Updated handoff and remaining work

Added the primary-source evidence note, updated the conditional partnership note,
S11 register, NEXT delivery/pending state and roadmap. Historical T8 failure
records remain intact. Published tags remain immutable. No referral, safety/gloss
copy, legal-source display or launch configuration changed; public outcome is
still NO-GO. Pending actual reviewer/legal-label/corpus/privacy/laptop evidence
is unchanged. Future institutional outreach needs separate user direction.

Native Git commit/push and a new annotated `t8-partnership` record this follow-up;
main CI is observed before annotating, then tag-triggered CI and peeled remote
refs are checked before the final delivery manifest.

## Observed delivery receipt

Staged only the six documentation files and inspected their diff. Ran
`git diff --cached --check` and `make hygiene`: 185 files passed. Checked that
every URL/digest in the five-item manifest appears in the evidence note and its
local Markdown link resolves. No raw PDF, HTML, search configuration or runtime
file was staged. Native remote main still matched the starting SHA; the new
follow-up tag did not exist. Committed and pushed:

```text
3aeeeac2241dcc0f18b856af7f4e783d30261f0f
docs: verify legal aid dialogue hotline and intake priority
6 files changed, 205 insertions(+), 13 deletions(-)
37fb8e8..3aeeeac main -> main
```

Read the GitHub push-workflow list and exact API run
`/repos/BlueZoft/lAi/actions/runs/44439418287`, comparing full SHA, branch main,
status completed and conclusion success.
[Successful source-follow-up CI](https://github.com/BlueZoft/lAi/actions/runs/44439418287).
This receipt-only update changes no executable behaviour. Final main CI is
retained in the immutable new annotation; its subsequent tag workflow is checked
before reporting delivery. Original T8/prototype tags remain at their original SHA.
