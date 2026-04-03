# First Pass Report

## Purpose

This report records the premise, execution basis, and return profile of the first preprocessing pass on `shrine/shrines.csv`.

## Premise of the First Pass

The first pass was run as a strict implementation of the cleansing specification in `documentation/SHRINE_CLEANSING_SPEC.md`.

The pass used these fixed rules:

- input source: `shrine/shrines.csv`
- search string: `region + raw_address`
- geocoding allowed only for rows classified as `valid`
- no geocoding for `invalid` or `vague` rows
- no row deletion
- original values preserved
- `status` restricted to `resolved`, `partial`, or `unresolved`

The implementation used `scripts/clean_shrines.py`.

Relevant script sections:

- address classification: `scripts/clean_shrines.py` lines 67-96
- combined address construction: `scripts/clean_shrines.py` lines 99-102
- geocoding request and acceptance rule: `scripts/clean_shrines.py` lines 121-159
- row-level status assignment: `scripts/clean_shrines.py` lines 183-206

## Returned Outputs

The first pass generated:

- `shrine/cleaned_shrines.csv`
- `shrine/cleaned_shrines.json`

## Row Totals

| Measure | Count |
| --- | ---: |
| Total input rows | 192 |
| `resolved` rows | 14 |
| `partial` rows | 1 |
| `unresolved` rows | 177 |

## Address Presence Profile

| Measure | Count |
| --- | ---: |
| Rows with `raw_address = NULL` | 26 |
| Rows with non-null `combined_address` | 166 |
| `resolved` rows with non-null `combined_address` | 14 |
| `partial` rows with non-null `combined_address` | 1 |
| `unresolved` rows with non-null `combined_address` | 151 |

## What the First Pass Actually Returned

The first pass did not fail primarily because the dataset lacked addresses. It failed primarily because most geocoding attempts on valid rows did not produce exactly one accepted result.

The output separates into three operational groups:

### 1. Invalid Rows

- Count: 26
- These rows had no usable `raw_address`
- `combined_address` was set to `NULL`
- `status` was set to `unresolved`

### 2. Vague Rows

- Count: 1
- This row had descriptive location text rather than an address fragment
- `combined_address` was retained
- no geocoding was attempted
- `status` was set to `partial`

### 3. Valid Rows

- Count: 165
- Geocoding was attempted on all 165 rows
- Only 14 resolved
- 151 remained unresolved despite having non-null `combined_address`

## Immediate Cause of the Low Resolution Rate

The main bottleneck was the geocoding acceptance rule, not the cleansing classification.

The implementation accepted a geocode result only if the geocoder returned exactly one feature. If the result set contained:

- zero matches, or
- more than one match

the row was treated as a geocoding failure and remained `unresolved`.

That rule is enforced in `scripts/clean_shrines.py` lines 143-145.

## What This Means

The first pass output should be read as:

- a correct implementation of the written cleansing spec
- a weak geocoding return on Jeju shrine address fragments
- not a proof that most shrine rows are inherently unlocatable

This distinction matters because many unresolved rows did contain searchable combined addresses, but they did not satisfy the strict first-pass geocoding rule.
