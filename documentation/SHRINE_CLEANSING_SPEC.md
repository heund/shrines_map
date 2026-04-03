# Shrine Cleansing Specification

## Scope

This document defines the data cleansing rules for the shrine dataset in `shrine/shrines.csv`. It applies only to the preprocessing phase before any downstream spatial analysis. The purpose of this phase is to standardize address handling, assign row-level processing states, normalize ownership values, and define the output structure.

## Source Columns Used

Only the following source columns are used in this phase.

| Source Column | Output Field |
| --- | --- |
| `지역` | `region` |
| `신당명` | `shrine_name` |
| `주소` | `raw_address` |
| `소유권` | `ownership_raw` |

## Address Resolution Rules

### Search String Construction

Use the following rules to construct the address string for lookup.

- `raw_address` = original value from `주소`
- `region` = original value from `지역`
- If `raw_address` is `NULL`, empty, or whitespace only, set `combined_address = NULL`
- Otherwise set `combined_address = "<region> <raw_address>"`
- Normalize spacing in `combined_address` to single spaces

## Address Classification

Each row must be classified as `valid`, `invalid`, or `vague`.

### Valid Address

A row is `valid` only if all of the following are true.

- `raw_address` is not `NULL`
- `raw_address` is not empty
- `raw_address` is not an error placeholder
- `raw_address` is not only a vague place description
- `raw_address` contains a searchable address-like fragment

Examples:

- `김녕리 21 21`
- `평대리 975`
- `동복리1 759`

### Invalid Address

A row is `invalid` if any of the following are true.

- `raw_address` is `NULL`
- `raw_address` is empty or whitespace only
- `raw_address` is an error marker or non-address placeholder

Treat the following as invalid.

- `GPS 오류`
- `GPS error`
- equivalent error placeholders that indicate address failure rather than location content

### Vague Address

A row is `vague` if `raw_address` is not null but does not provide a searchable address fragment and instead describes only a broad location type or area.

Treat the following as vague.

- `해변`
- `beach`
- `near coast`
- coast-only, shore-only, sea-only, mountain-only, forest-only, field-only descriptions without address fragments

## Geocoding Decision Rules

- Attempt geocoding only when address classification is `valid`
- Skip geocoding when address classification is `invalid`
- Skip geocoding when address classification is `vague`

## Row Output Decision Rules

For each row, assign `resolved_address`, coordinates, and `status` using the following rules.

| Condition | `resolved_address` | `latitude` | `longitude` | `status` |
| --- | --- | --- | --- | --- |
| Valid address and geocoding succeeds | yes | yes | yes | `resolved` |
| Valid address and geocoding fails | no | no | no | `unresolved` |
| Invalid address | no | no | no | `unresolved` |
| Vague address | no | no | no | `partial` |

### Status Definitions

- `resolved`: a usable Korean resolved address exists and both coordinates exist
- `partial`: some source location information exists, but no geocoding is performed because the address is vague
- `unresolved`: no usable resolved address and no coordinates

## Ownership Standardization

Use the following final category set.

- `국가`
- `법인`
- `개인`
- `공동`
- `미상`

Keep the original source value unchanged in `ownership_raw`.

### Mapping Table

| `ownership_raw` | `ownership_standardized` |
| --- | --- |
| `국가` | `국가` |
| `제주도` | `국가` |
| `제주시` | `국가` |
| government wording or equivalent administrative ownership wording | `국가` |
| `법인` | `법인` |
| company, foundation, corporation, or other organizational wording | `법인` |
| `개인` | `개인` |
| `공동` | `공동` |
| `개인, 공동` | `공동` |
| any value containing both individual and shared wording | `공동` |
| `-` | `미상` |
| `NULL` | `미상` |
| empty string | `미상` |
| unmatched or unclear value | `미상` |

## Final Output Schema

The cleansing phase must output the following fields.

| Field | Description |
| --- | --- |
| `region` | original `지역` value |
| `shrine_name` | original `신당명` value |
| `raw_address` | original `주소` value |
| `combined_address` | `region + raw_address` if `raw_address` is valid or vague; otherwise `NULL` |
| `resolved_address` | resolved Korean address from geocoding result; otherwise `NULL` |
| `latitude` | latitude from successful geocoding; otherwise `NULL` |
| `longitude` | longitude from successful geocoding; otherwise `NULL` |
| `status` | `resolved`, `partial`, or `unresolved` |
| `ownership_raw` | original `소유권` value |
| `ownership_standardized` | standardized ownership category |

## Edge Case Rules

### NULL Address

- `combined_address = NULL`
- `resolved_address = NULL`
- `latitude = NULL`
- `longitude = NULL`
- `status = unresolved`

### Vague Location

- `combined_address = "<region> <raw_address>"`
- `resolved_address = NULL`
- `latitude = NULL`
- `longitude = NULL`
- `status = partial`

### Geocoding Failure

This applies only to rows classified as `valid`.

- `resolved_address = NULL`
- `latitude = NULL`
- `longitude = NULL`
- `status = unresolved`

### Unknown Ownership

- Keep the original source value in `ownership_raw`
- Set `ownership_standardized = 미상`
- Do not change address handling or status rules based on ownership during cleansing

## Cleansing Output Requirement

Every input row must remain in the output dataset. No rows are deleted during this phase. Rows that cannot be resolved must still be preserved with their standardized ownership value and assigned `status`.
