# Corpus inventory

Observed on 18 November 2026 through public GitHub HTML, pinned raw files and
native read-only Git requests. Repository commits and content hashes below
identify the inspected snapshots. Real source bodies remain outside Git.

## Maintainer repositories

The public repository listing exposed eleven repositories. Their root trees and
root READMEs were inspected. No root PDF or explicitly corpus-named root was
found. A README reference to Sri Lanka appeared in the web project and LAi.
That reference establishes no legal-document collection. Nested contents and
unlisted/private repositories remain UNVERIFIED. The maintainer was asked for
the document repository URLs, and no URLs had been supplied when this report
was written. No absent credential was inferred from that missing information.

| Repository under BlueZoft | Inspected commit | Root entries |
| --- | --- | --- |
| Cloud_Storefront | `91658e357e010d1943b593add4da3173d371aedd` | 13 |
| Data_Pipeline_with_Medallion_Architecture | `68eb676db25c6a7c7b35b321594aa2ce957af125` | 12 |
| EOApp-Cloud_Backend | `79cbc59862ee2c94dde3d1f58cbb4706292e1984` | 24 |
| EOApp-Cloud_Frontend | `ea49a2b97209724ebf32dff74516a8a17e0f54f7` | 25 |
| EOApp-Mobile_Backend | `789a90ee180a62ec02e82d9589772233368d7391` | 6 |
| EOApp-Mobile_Frontend | `70cfdd922c6890d9f962068e12cb1c65cf9cdcf0` | 9 |
| ETL_Data_Pipeline | `fbadcef8a8e60f46daffd549888fa0f25a550456` | 14 |
| Past_Perfect_BackEnd | `9e89ee413e7f647dc4a8f8c85047f687f528ff23` | 17 |
| Past_Perfect_Web | `12b5c8ec98494676bc4e3a262c07b5a1dd9dc19b` | 11 |
| azuredatafactoryUF0 | `606d89ffd525f03990897d67b2c30463a79e8639` | 12 |
| lAi | `c36b4cb2a2356276abce0ef19fb5e6626996ee06` | 18 |

This table records public discovery scope. Maintainer corpus selection remains
pending. [Public repository listing](https://github.com/BlueZoft?tab=repositories)

## Dataset index and coverage

`nuuuwan/datasets` returned 404 on GitHub. Account discovery located
`nuuuwan/lk_datasets`, whose README at commit
`8ac80cbfcad2f817fdb65ac2000821cd4f6685f8` reports 26 datasets, 303,457 documents
and 86.3 GB. Parsing all 26 count entries independently sums to 303,457. The
following dates and sizes are upstream index claims, with the selected detailed
checks described below. [Inspected index](https://github.com/nuuuwan/lk_datasets/tree/8ac80cbfcad2f817fdb65ac2000821cd4f6685f8)

| Dataset | Indexed documents | Reported size | Reported date range |
| --- | --- | --- | --- |
| lk_hansard_2020s | 273 | 3.6 GB | 2023-11-17 to 2026-11-05 |
| lk_hansard_2010s | 10 | 153.2 MB | 2019-09-05 to 2019-11-11 |
| lk_hansard_2000s | 10 | 135.4 MB | 2009-10-20 to 2009-12-08 |
| lk_appeal_court_judgements | 18,827 | 14.1 GB | 2010-10-16 to 2026-11-04 |
| lk_supreme_court_judgements | 2,729 | 1.7 GB | 2009-01-27 to 2026-05-27 |
| lk_police_press_releases | 1,434 | 513.0 MB | 2025-05-01 to 2026-08-08 |
| lk_acts | 3,979 | 6.8 GB | 1981-01-22 to 2026-04-09 |
| lk_bills | 4,236 | 2.0 GB | 2010-05-10 to 2026-04-29 |
| lk_extraordinary_gazettes_2020s | 49,513 | 11.6 GB | 2020-01-01 to 2026-04-28 |
| lk_extraordinary_gazettes_2010s | 56,379 | 17.4 GB | 2010-01-01 to 2019-12-31 |
| lk_cabinet_decisions | 11,212 | 144.0 MB | 2010-09-27 to 2026-11-09 |
| lk_treasury_press_releases | 183 | 182.4 MB | 2015-09-08 to 2026-11-06 |
| lk_pmd_press_releases | 2,182 | 55.9 MB | 2024-09-23 to 2025-09-24 |
| lk_news | 136,162 | 2.1 GB | 2021-09-12 to 2026-11-18 |
| lk_tourism_weekly_reports | 47 | 121.3 MB | 2023-01-01 to 2026-11-01 |
| lk_tourism_monthly_reports | 141 | 372.2 MB | 2015-01-01 to 2026-10-01 |
| lk_dmc_situation_reports | 4,738 | 3.2 GB | 2018-01-02 to 2026-11-16 |
| lk_dmc_weather_forecasts | 6,504 | 8.0 GB | 2023-03-26 to 2026-11-18 |
| lk_dmc_river_water_level_and_flood_warnings | 1,116 | 416.2 MB | 2025-06-10 to 2026-11-18 |
| lk_dmc_landslide_warnings | 760 | 568.5 MB | 2019-09-26 to 2026-11-14 |
| cbsl_annual_reports | 1,137 | 3.5 GB | 1950-01-01 to 2023-01-01 |
| lk_fisheries_annual_statistics_reports | 9 | 15.1 MB | 2017-01-01 to 2024-01-01 |
| lk_fisheries_monthly_fish_production_reports | 102 | 9.7 MB | 2019-01-01 to 2025-12-01 |
| lk_fisheries_weekly_fish_prices_reports | 277 | 23.9 MB | 2019-01-01 to 2026-04-08 |
| lk_fisheries_monthly_export_import_reports | 71 | 55.7 MB | 2019-01-01 to 2026-02-01 |
| lk_edupub | 1,426 | 9.4 GB | 2025-01-01 to 2025-01-01 |

Acts are the first intake candidate. Gazettes are candidates for version and
commencement evidence. Bills and Hansard require explicit contextual status.
Judgments remain deferred from automatic v0 navigation. Other topics are outside
the selected legal corpus. No source has been enabled for public retrieval.

## Detailed government-document pipeline

The index points Acts to `nuuuwan/lk_legal_docs` branch `data_lk_acts`, observed
at `abb6fd5000acb717c2c1f19e90d36be1139e3296`. Its complete 923,880-byte
`docs_all.tsv` contains 3,979 rows and unique document IDs/PDF URLs. Language
counts are English 1,229, Sinhala 1,567 and Tamil 1,183. These are language-version
rows. Distinct legal-instrument coverage needs identity and version review.
The dates in the file range from 1981-01-22 to 2026-04-09. All listed PDF and
metadata URL hosts are `documents.gov.lk` and no PDF URL field is empty.
[Pinned Acts data](https://github.com/nuuuwan/lk_legal_docs/tree/abb6fd5000acb717c2c1f19e90d36be1139e3296/data/lk_acts)

The TSV and sampled `doc.json` have these fields.

```text
doc_type, doc_id, num, date_str, description,
url_metadata, lang, url_pdf, doc_number
```

The sampled directory includes `doc.json`, `doc.pdf`, `doc.txt` and `blocks.json`.
No acquisition timestamp, extraction-tool version or content-hash field appears
in that sampled metadata. LAi computes hashes and retains acquisition details
separately. The pipeline source imports `scraper`, and the inspected workflow
and source functions expose year discovery and document pipeline processing.
Full dependency/engine reproducibility remains UNVERIFIED.

Selected downloaded `summary.json` files report these counts. They describe
stored artefacts and require independent quality checks.

| Dataset | Indexed | PDFs | Text artefacts |
| --- | --- | --- | --- |
| Acts | 3,979 | 3,973 | 3,973 |
| Bills | 4,236 | 4,232 | 4,232 |
| Extraordinary gazettes, 2020s | 49,513 | 13,952 | 13,952 |
| Supreme Court judgments | 2,729 | 1,909 | 1,909 |
| Appeal Court judgments | 18,827 | 14,541 | 14,541 |

The judgment summary metadata includes `parties` and `judgement_by`. Appeal
metadata additionally includes `keywords` and the upstream spelling `legistation`.
No values from those personal-data fields appear in this repository, fixtures or
turn logs. Any future judgment ingestion needs minimisation and privacy review.

## Separate Parliament Acts pipeline

`nuuuwan/lk_acts` at `d62c23c744fc4b5aaddbb08da70d1bc94cc74d6e`
links to `nuuuwan/lk_acts_data` at
`cf29a5407cc0402a47c5bfa51577f6c714ddf8d0`. Its README reports
2,865 Acts/2.7 GB, with 2,437 PDFs, 728 native text artefacts, 1,709 OCR text
artefacts and 392 structured Act JSON artefacts. Metadata extends to the 1940s.
The README reports no PDFs for its 88 entries in that decade and substantially
different extraction counts by decade. These totals were read from its report,
with representative files inspected separately.
[Pipeline snapshot](https://github.com/nuuuwan/lk_acts/tree/d62c23c744fc4b5aaddbb08da70d1bc94cc74d6e)

The inspected metadata has `num`, `date`, `description`, `url_pdf_en`, `act_id`
and `act_type`. Its native blocks sample has 140 entries with `bbox`, `fonts`,
`page_number`, `sizes` and `text`. Source modules include separate native text,
OCR and parsing paths, and dependencies name PyMuPDF, Selenium, pytesseract and
pdf2image. Sinhala/Tamil PDFs are described as not yet downloaded in that README.
The two pipelines need explicit source adapters and hash/identity deduplication.

Older metadata expands the research leads. Foundational prescription, criminal,
civil-procedure, land and labour coverage remains OPEN until each instrument,
language and amendment/commencement chain has been reviewed.

## Sample measurements

Measurements used the committed `measure_corpus_sample.py` and the final
`quality-v1` policy. No real text became a test fixture.

| Sample | UTF-8 bytes | Quality score | Structural result | Eligibility findings |
| --- | --- | --- | --- | --- |
| Government pipeline, English | 4,235 | 1.0 | 4 sections, no parser issue | Actual intake stays quarantined for unreviewed source and incomplete instrument identity |
| Government pipeline, Sinhala | 12,912 | 0.75 | Parser unsupported | Replacement character detected |
| Government pipeline, Tamil | 17,611 | 0.75 | Parser unsupported | Replacement character detected |
| Older Parliament pipeline, English | 14,983 | 1.0 | 17 candidate sections | Section-number gap and order issues quarantine the result |

The English PDF acquired from the pinned government-data mirror is 301,116 bytes.
Its SHA-256 is
`5835db66e0ad2f4cbda93a9896940e049f7229fb145510e101bf412b8491d160`.
It was staged through the real CLI with exact raw/text hashes and remained
ineligible. The original publisher request failed with CONNECT 403. Instrument
identity and source authority remain UNVERIFIED. No legal effect was inferred.

The initial heuristic flagged a 78-character underscore divider in the English
sample. The corrected repeated-letter rule and combining-mark treatment were
checked with invented regression fixtures before these final measurements.
Four samples cannot establish corpus-wide OCR accuracy, legal recall or safety.

## Canonical sources, licences and remaining gaps

Prefer an inspected official publisher as the canonical source. Retain the
actual acquisition URL and pinned mirror revision independently. For equivalent
content, choose reviewed eligible official provenance first. Preserve all
observations, quarantine quality/identity conflicts and avoid fuzzy merging.
Use the older Parliament pipeline for targeted foundational research while its
coverage and extraction weaknesses remain explicit.

The inspected `lk_datasets`, `lk_legal_docs` and `lk_acts` code-repository licence
files declare MIT and have the same SHA-256 shown below. Preserve their copyright
and licence notices outside Git alongside covered acquired material. Original
government PDF terms remain UNVERIFIED. No MIT conclusion about every original
PDF follows from the repository licence.

HuggingFace discovery failed with CONNECT 403. The GitHub API and original
publisher destination are outside the current allowlist. GitHub HTML, raw files
and native Git reads work. Full mirror equivalence, maintainer corpus URLs,
foundational coverage, manual conversion quality, OCR and legal status remain
UNVERIFIED. Full corpus downloading, OCR/inference and integration measurements
remain TARGET B tasks.

## Reproducibility identifiers

| Artefact | SHA-256 |
| --- | --- |
| Dataset-index README | `0dac1ffd1bb837fe08a975884ca5e806cc082ffdacd6d076573eee7238e7e5ab` |
| Older Acts README | `abf5fe6eefaa069e92eeb7d6e3ee91a72a77d3660b9e8119425a92104c93fcaa` |
| Complete government Acts TSV | `501aab1161af6df09ab79fe20999e3d6f670f796cd30240f5159459870caae9a` |
| Inspected MIT licence files | `48c61df00681372cdd1bc8246dc25015c81d14c5e9e664273a5dc09e6b91a442` |
| English sampled text | `05e246c4028c7bf0e28f643198175344688ca16bf560bee156a7e1413c9dd30e` |
| Sinhala sampled text | `4eec9083c0df556471f182a9ec93697061bab4444afa3efe7ee9ef3b621e06c2` |
| Tamil sampled text | `ec4023f2f3aaaefcb122aec32a432a8d4bdae356e92bb88b4ee09c1796c8f0ae` |
| Older sampled English text | `e7b85768fa059d56d13f0f429eb8e2769199222099be30e98dd06338f0e9a77b` |

Observed data-branch commits include bills
`96e94c7814c342ca737353419dfe6cde9bb81065`, 2020s gazettes
`0bca930376deb39493206b1b70e2b3cf04e27d3f`, Supreme Court judgments
`dd3d2b605e94e67ddbc61c51f8bbc68d324e12cb` and Appeal Court judgments
`1a081fe4c1bfefd0d628d11deab15005952c413c`. Counts from those summaries were
observed on the named date. A full file-tree census and corpus audit remain
pending.
