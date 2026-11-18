# Private extractive answers

T5 assembles source text and reviewed fixed copy. It runs no language model and
generates no legal explanation, conclusion, deadline, recommendation or source
translation. The default application is closed. README's complete private-
prototype launch gate still applies. Legal applicability, real model/language
quality and actual reviewer approvals remain UNVERIFIED.

## Run and review

```sh
make setup
make verify
make review-packet
make serve
```

The UI is served with the existing loopback default. `GET /health` still reports
`navigator_enabled: false`. The Sinhala-first form stays disabled while private
navigation/copy review is unavailable. `POST /api/answers` returns `review_required`
without quotes, messages or referrals when required safety copy is unreviewed.
`GET /api/capabilities` reports private configuration/copy readiness and always
keeps public launch false. OpenAPI/interactive API documentation remains disabled.

The private `.local/t5-review.html` file contains invented source text, four
UNREVIEWED English/Sinhala gloss seeds, 12 safety messages and interface labels.
It is an offline document with no scripts/forms. Generation changes no review or
launch flag, writes mode 0600 and refuses to overwrite an unrelated file.
Reviewing synthetic seeds approves no real legal provision.

Pending from your side: actual reviewer sign-off on taxonomy/escalations and
safety/UI copy; real provision-bound glosses; safe specialist routes for detention
and destitution; reliable regional phones and current eligibility/access. The
reviewers are already available and corpus URLs supplied. Use
`reviewer-handoff.md`; no new credential or environment decision blocks T5.
T6 supplies the next laptop/model measurement work.

## API and routing contract

```json
{
  "scenario": {
    "text": "SYNTHETIC documents catalogue",
    "language": "en",
    "urgent": {"child_protection": false}
  },
  "display_language": "si"
}
```

The scenario follows T4's strict 1024-character/boolean contract. Optional `region`
is a bounded locality label for exact filtering on professional routes; it is
not a jurisdiction finding. Display language is Sinhala or English. Tamil/
Singlish follow T4's conservative language rules. Unknown fields/coercions are
rejected without echoing input.

The route permits JSON POST bodies, limits streamed bytes to 16 KiB even without
Content-Length, rejects duplicate keys/nesting beyond 16 and URL query parameters,
and checks hosts/origins. Trusted hosts default to loopback names and the test
transport host. There is no account, cookie or persistent session. Errors expose
fixed codes. `make serve` keeps access logging disabled. T7 still must verify
full-stack logs, retention, deletion and runtime egress restrictions.

Bounded known urgency fields are inspected before validating the surrounding
envelope. Recognised urgency wins even when another envelope field is malformed.
Urgent, forbidden, referral and invalid routes never enter downstream analysis,
model or retrieval work. Required reviewed copy is checked before permitting a
private procedural retrieval. No public enablement switch is exposed to a request.

## Sources, glosses and abstention

Every selected candidate is reloaded against CAS and scoped document/provision
evidence immediately before display. Text, section span/hash and the complete
citation must match the fresh source. Corruption, altered labels, missing bytes
or stale version evidence closes the entire answer. The contract requires at
least two distinct logical provisions. A single match is never shown as an answer.

Quotes preserve whitespace and original language. Selecting Sinhala never
machine-translates an English provision. Each card retains instrument type/ID/
number/year/section, language, actual/canonical URLs, acquisition date/ID, revision,
raw/text/section hashes, source span, amendment/commencement status and currency/
coverage warnings. The UI has a prominent bilingual currency warning and full
expandable details. Acquisition date never establishes current legal force.
Ranking scores are not displayed as probabilities or legal confidence.

`schemas/gloss-library.schema.json` binds each gloss to acquisition/chunk, source
revision/language/section hash and target language. Approval requires actual
attorney/language dates, an evidence reference and SHA-256 of the exact reviewed
text. Future/pre-acquisition dates do not match. Text changes invalidate the
approval checksum; different source identities, revisions, languages or hashes
do not match. There is no interpolation, translation or inferred review.
These metadata assertions still require independent real reviewer evidence.

Without a matching gloss, the card uses `text_and_referral`: original text plus
the fixed professional-referral message and current contact listings. T4 expiry
and urgency scope apply. Missing/expired contacts produce an unavailable state;
no numbers are guessed and no representation is promised. No fee/timeline field
or calculation is added. Any real offered fee/timeline claim still needs dated
primary evidence and review before the domain is offered.

## Browser checks and limits

The UI loads local assets and uses DOM text nodes, not HTML interpolation. Queries
use same-origin POST bodies and no localStorage, sessionStorage, cookies or history
URLs. Clear and language changes abort pending work and erase the textarea/results;
late responses cannot repopulate them. Use invented scenarios only in this prototype.

The optional browser check needs Node, Playwright and Chromium, already available
in this cloud environment. Default Python setup/CI does not install or require them.

```sh
PORT=8015 make serve
# In another terminal in this checkout:
node scripts/check_ui.cjs http://127.0.0.1:8015
```

The check first tests the actual closed page, then intercepts browser responses
with the tiny synthetic fixture. It verifies desktop/mobile layout, exact quote
DOM text, all citation fields, hostile-markup escaping, clear/cancel, empty storage
and no external page requests. Mocks do not enable the server or approve real copy.
API tests independently use the actual safety/retrieval/source pipeline with
synthetic bytes. The hostile mock is a DOM attack test, not source-valid evidence.

378 offline tests and 269 safety tests passed; three new schemas match their
typed contracts. Real laptop/model integration, legal recall, corpus rights/gaps,
actual reviews and complete runtime privacy remain pending. Commands, failures,
screenshots and delivery receipts are in `turn-logs/T5.md`.
