# T4 continuation — referral verification

Performed on 19 November 2026 (Asia/Colombo). Started clean on `main` at
`866a9161f6749952bb9169a42b93a119436d2564`, matching remote `t4-safety`.
Inspected AGENTS, existing contracts/tests, T2 inventory, NEXT, ADRs, source
register and the T4 log. Completed triage was preserved. The previous tag stays
immutable; this additive continuation uses annotated `t4-referrals`.

## Environment and acquisition

Waited for the newly selected environment. Current status identified the new
instance with enforced unrestricted networking. The previous T4 denials were
historical. No settings were reapplied or environment published. `make setup`
used frozen dependencies and retained local configuration. Native remote Git
read matched HEAD. Dependencies/lockfile were preserved. No production, home-lab,
database, GPU, model or live user data was used.

TLS-verified curl requests to Ministry, Commission and BASL roots returned 200.
Followed actual links to the exact pages recorded in
`docs/referral-verification.md`. The Commission defaults to Sinhala; its own GET
language selector (`lang=en`) and an anonymous cookie supplied the English page.
No contact form, telephone call, email or institution outreach was performed.

Acquisition commands included these exact invocations:

```sh
curl --silent --show-error --location --max-time 30 -o /tmp/lai-t4-referrals/moj.html -w 'moj %{http_code} %{url_effective}\n' https://moj.gov.lk/
curl --fail --silent --show-error --location --max-time 30 -o /tmp/lai-t4-referrals/basl-contact.html -w 'basl-contact %{http_code} %{url_effective}\n' https://basl.lk/contact/
curl --fail --silent --show-error --location --max-time 30 --max-filesize 10000000 -o /tmp/lai-t4-referrals/lac-map.kml -w 'lac-map %{http_code} %{content_type} %{size_download}\n' 'https://www.google.com/maps/d/kml?mid=16qiVyy9LRVhzKMRLOlH1ApApQ6ZFTVI&forcekml=1'
pdftotext -layout /tmp/lai-t4-referrals/lac-directory.pdf /tmp/lai-t4-referrals/lac-directory.txt
pdftoppm -scale-to 2400 -png -singlefile /tmp/lai-t4-referrals/lac-directory.pdf /tmp/lai-t4-referrals/lac-directory-preview
```

Ministry Commission, NCPA Childline, Police emergency, NIMH helpline and Suwa
Seriya FAQ pages also returned 200. Final bodies, URLs, SHA-256 and observed
dates are retained outside Git in
`data/research/referrals/2026-11-19/manifest.json`. Cookie files are not retained
as evidence or committed. Product metadata excludes staff names, emails and
coordinates. Institutional contacts are the requested versioned referral data.

## Findings and corrections

The Commission-linked map exported 85 entries including head office. Every phone
field is scientific notation; the head-office value corresponds to a fax
explicitly labelled on the contact page. Regional phones were withheld without
reconstructing digits or adding a leading zero. The other 84 exact names and
addresses were retained, with a caution for the source's repeated Jaffna locality.
The linked PDF downloaded successfully (168,258 bytes), but extraction returned
no text and the single-page render inspected with `view_image` was blank.

The contact page supplies two head-office numbers. The Ministry's conflicting
older contacts/count/income threshold do not establish current eligibility.
BASL is a general office, with no promised review/referral programme. Five
emergency/support listings were checked against their publishers and assigned
distinct channels and explicit urgency scopes. NCPA's 24-hour statement is
attributed to its page. NIMH's article is dated 2021; hours are not inferred.

The register contains 93 records: 91 checked listings (84 regional) and two
pending specialist urgent routes. Detention and destitution require safeguarding
decisions; generic legal aid is not a verified 24-hour specialist service. Police
records are not automatically selected for detention or self-harm. All safety
copy and launch flags remain unapproved/closed.

Early helper attempts had a misspelled GitHub search username (HTTP 422) and a
local helper-import mismatch. Corrected both before using the results. Rejected
file-edit patches were reapplied after inspecting their exact context. No check,
TLS verification or source requirement was disabled to obtain a pass.

## User steering and corpus reconciliation

The user supplied Supreme Court (twice), Appeal Court and Acts links under
`nuuuwan`, requested additional legal repositories, directed use of both T2 and
these links with official sources governing conflicts, and confirmed reviewers
are available. Deduplicated the links and reused the unchanged Acts pipeline
snapshot. Pinned court main/data branches and inspected their READMEs and MIT
code licences. No judgment PDF, party data or case text was downloaded.

Executed native `git ls-remote --symref ... HEAD` and explicit data-branch lookups;
the exact SHAs and pinned-document hashes are in `docs/corpus-inventory.md`.
Public GitHub API searches for legal, judgement, acts, gazette, bills and hansard
identified additional account repositories. Search metadata/READMEs/licences
remain ignored in `data/research/inventory/2026-11-19/`. Court README totals agree
with T2's reported index totals; they were not presented as a fresh recount.
Supreme Court apex and `www` roots returned HTTP 403; Appeal Court root returned
200. No official/mirror equivalence, publication rights or review approval was
inferred. The specific outstanding reviewer tasks are in `reviewer-handoff.md`.

## Executed verification

Version 2 adds per-kind source hosts, channels, cautions, extra published phones,
directory evidence, scoped urgency and locality filters. The selector withholds
pending/future/expired records and emergency records without a matching urgency.
The explicit offline audit checks body hashes, source/date bindings, phones,
regional addresses and the publisher-to-map link. Manual inspection still
determines service scope/hours; neither establishes live availability or safety.

```sh
make verify
make safety
uv --cache-dir .local/uv-cache run --frozen --offline python scripts/check_referral_evidence.py --directory data/research/referrals/2026-11-19
uv --cache-dir .local/uv-cache build --wheel --offline
docker compose config --quiet
git diff --check
```

```text
Success: no issues found in 57 source files
324 passed, 5 deselected in 2.06s
221 passed, 108 deselected in 1.06s
verified_listings_checked: 91
regional_locations_checked: 84
live_availability: UNVERIFIED
Successfully built dist/lai_navigator-0.0.0-py3-none-any.whl
Wheel package-only members: 37; register records: 93
```

New synthetic tests reject changed bytes, path escape and wrong source binding,
and check regional phone withholding, emergency scope, filtering and expiry.
CI needs no raw evidence, network, GPU, database or model. The archive has only
package/distribution members, with no raw research artefacts. Compose and
whitespace checks exited 0. After completing the documentation, `make verify`
again passed all 324 tests in 1.95s and the real stored-evidence audit again
checked 91 listings and 84 regional locations. The file guard passed 105 files.
Staged checks and CI receipts follow after execution.

## Remaining work

No environment access change is required for the completed referral checks.
Reviewers are available; actual taxonomy/escalation/copy approval, safe specialist
routes, regional phones and current eligibility/access still need evidence.
Supreme Court access and corpus rights/equivalence remain unresolved. T5 private
engineering can continue; README's full gate still blocks public deployment.
No application/environment publication or visibility change occurred.
