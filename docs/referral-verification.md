# Referral publisher verification — 19 November 2026

These checks establish what the inspected publishers list. They do not establish
telephone reachability, opening/access, eligibility, representation, a safe route
for an individual case or approval to display the unreviewed product copy.
The user reports attorney and Sinhala reviewers are available; actual review is
still pending. README's private-prototype launch gate remains closed.

## Checked listings

| Publisher / channel | Published contact retained | Scope and limit |
| --- | --- | --- |
| [Legal Aid Commission contact page](https://legalaid.gov.lk/contact-us) | +94-70-3655111; +94-70-5655111; No 129, Hulftsdorp Street, Colombo 12 | Head-office enquiries. Eligibility and representation need Commission confirmation. |
| Commission-linked regional map | 84 centre locations; no regional telephone fields | 85 exported entries include head office. Locality labels do not establish jurisdiction/catchment. |
| [BASL contact page](https://basl.lk/contact/) | 011 2 447134; 153, Mihindu Mawatha, Colombo 12 | General-office enquiry about an attorney or review. No referral/review programme or partnership commitment was verified. |
| [Sri Lanka Police services](https://police.lk/emergency-services/) | 119 | Listed immediate emergency-response channel. Not automatically selected for detention or self-harm. |
| Same Police page | 109 | Listed women/children abuse complaints channel. Distinct from ambulance dispatch or guaranteed immediate response. |
| [NCPA Childline](https://childprotection.gov.lk/en/what-we-do/1929-call-centre-helpline) | 1929 | Publisher states free access, all-day/all-week and Sinhala/Tamil/English. These are publisher statements, not call-test results. |
| [NIMH helpline](https://nimh.health.gov.lk/en/1926-national-mental-health-helpline/) | 1926 | National Mental Health Helpline, also in the current site footer. Article dated 2021; hours/dispatch are not asserted. |
| [Suwa Seriya FAQ](https://www.1990.lk/faq/) | 1990 | Publisher lists toll-free pre-hospital emergency ambulance access. No response-time guarantee is imported. |

The register contains 93 records: 91 checked listings and two pending specialist
routes for unlawful detention and imminent destitution. General legal-aid contact
is not a verified 24-hour specialist service for those situations. Safeguarding
review must settle suitable alternatives. Emergency records require an explicit
matching urgency; no urgency means no emergency selection. These are candidate
channels for review, not an individual recommendation to contact police.

## Regional directory and conflicts

The Commission's contact page embeds a map with ID
`16qiVyy9LRVhzKMRLOlH1ApApQ6ZFTVI`. Its [public KML export](https://www.google.com/maps/d/kml?mid=16qiVyy9LRVhzKMRLOlH1ApApQ6ZFTVI&forcekml=1)
contains 85 named entries, including head office. The 84 other entries' names and
addresses are preserved exactly in the register, with the Commission page hash
and map hash. No personal staff names/emails or coordinates are imported.

Every map phone field uses scientific notation. The head-office field, when
expanded numerically, corresponds to a number explicitly labelled as a fax on
the current Commission contact page. No regional number is reconstructed,
zero-prefixed or promoted to a telephone contact. The Jaffna address repeats its
locality in the source; the exact text is retained with a repetition caution.

The same page's “View all Locations” PDF is publisher-linked from a vendor host.
It downloaded successfully (168,258 bytes), but text extraction returned no text
and the single-page render was blank. It provides no usable directory evidence.

The [Ministry's Commission page](https://moj.gov.lk/index.php/en/departments-institutes/institutions/legal-aid-commission-of-sri-lanka)
has older phone/count information and an income threshold. The Commission's own
contact page governs the retained contact fields. The Ministry threshold is not
adopted as current eligibility or legal advice. Current eligibility remains
UNVERIFIED pending authoritative evidence and counsel review. BASL's alternative
body/footer numbers differ; only the number common to both is retained.

## Evidence and expiry

Raw HTML, KML and the unreadable PDF remain outside Git under
`data/research/referrals/2026-11-19/`. The manifest records URL, filename, SHA-256
and observed date. The Commission English page was acquired using its own
language selector and an anonymous cookie; cookie files are not retained as
evidence or committed. Observation dates use Asia/Colombo.

| Artefact | SHA-256 |
| --- | --- |
| Commission English contact page | `af3d7f69fa12d91d995cf50f6ae0664a19df0c0d084688b0a33af1741294a1b4` |
| Commission-linked map export | `400b2badc02d4c2a81d533cc64e6cbf3546eb4e237f1d6bfdba799df6b916746` |
| Ministry Commission page | `cb708acefff553fd59041cefbfe5f2cd0100117110d2c46e9e87c950f8ce753e` |
| BASL contact page | `ece62bdec8cb291e4d4020060bd294b73df0c9cd383c7b25d4e6b622e9e78630` |
| Police emergency page | `e83b5115e735aa8f2ad5912fe8d38bf62e2324d4a1a441efc2775d445113bee5` |
| NCPA helpline page | `2199a9837eb8f2adff4f46b0167d916c455f1b9e59198fba594ef3c8fb15c077` |
| NIMH helpline page | `7d91076ebaeb59baaeac80519e1a107585d18cf18eed6b7b1c04fa8293b04c02` |
| Suwa Seriya FAQ | `4c61da91057385d862bde896feb0aed05c009271b1810404025e2b15afa7e2c7` |
| Unreadable directory PDF | `1bb569682d22007610691f6c12ae7b3f898bd9ef4b1371ae65713910fc4f7cb2` |

General/directory listings expire after 19 December 2026; emergency/support
listings expire after 3 December 2026. The selector includes the due date and
withholds records after it. These 30/14-day engineering intervals require
review and do not promise that a contact remains available until expiry.

The explicit offline evidence checker passed for all 91 listings/84 regional
locations. It checks stored bytes, date/URL bindings, phones, exact addresses and
the authority link. Service descriptions and hours also received manual page
inspection; no automated check establishes legal or safeguarding correctness.
No telephone call, email, form submission or institution outreach was performed.
