# Heritage Merge Report

## Purpose

This report documents the merge of the two heritage JSON sources in the `heritage` folder and records the overlap count, duplicate handling rule, and final merged output count.

## Source Files

Primary source:

- `heritage/jeju_heritage_sites.json`

Secondary source:

- `heritage/jeju_historic_locations.json`

Merged output:

- `heritage/combined_heritage_sites.json`

## Merge Rule

The merge used the following rule:

- if a record in the secondary file overlapped with a record in the primary file, the primary file won

Duplicate detection was conservative and used:

- normalized name matching
- exact coordinate matching

## Source Counts

| Source | Count |
| --- | ---: |
| `jeju_heritage_sites.json` | 368 |
| `jeju_historic_locations.json` | 120 |

## Duplicate Counts

| Duplicate Type | Count |
| --- | ---: |
| Name duplicates | 5 |
| Exact coordinate duplicates | 0 |
| Total duplicates removed from secondary source | 5 |

## Secondary Records Added

| Measure | Count |
| --- | ---: |
| Secondary records kept and added to merged output | 115 |

## Final Merged Count

| Output | Count |
| --- | ---: |
| `combined_heritage_sites.json` | 483 |

## Duplicate Examples

The following overlaps were identified and therefore retained only from the primary source:

- `법화사지`
- `와흘본향당`
- `연북정`
- `명월 팽나무군락` / `명월팽나무군락`
- `구억리 검은굴` / `구억리검은굴`

## Result

The merged heritage JSON contains:

- all 368 primary heritage records
- 115 non-duplicate records from the secondary heritage-location JSON
- 483 records total after overlap removal
