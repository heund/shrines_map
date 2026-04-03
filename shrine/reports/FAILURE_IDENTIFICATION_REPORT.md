# Failure Identification Report

## Purpose

This report documents the follow-up review of first-pass failures in `shrine/cleaned_shrines.csv`. Its purpose is to identify what actually failed, where it failed, and why those rows remained `unresolved`.

## Review Method

The failure review was performed against the first-pass outputs, not against a redesigned pipeline.

The review checked:

- which unresolved rows had truly null source addresses
- which unresolved rows still had non-null `combined_address`
- what address forms were common among unresolved valid rows
- what the geocoder returned for representative unresolved queries

## Main Finding

The unresolved set contains two very different groups.

### Group A. True Null or Empty Address Failures

- Count: 26
- `raw_address = NULL`
- `combined_address = NULL`
- no geocoding attempted

These are genuine source-address absences.

### Group B. Geocoding Failures on Non-Null Combined Addresses

- Count: 151
- `raw_address` present
- `combined_address` present
- row still returned as `unresolved`

These are not null-address failures. These are lookup failures.

## Why the 151 Rows Failed

### Cause 1. The Query String Was Minimal

The first pass used only `region + raw_address`.

Examples:

- `구좌읍 동복리1 759`
- `구좌읍 김녕리 571 -2`
- `구좌읍 월정리 774-4`
- `구좌읍 한동리 656`

This follows the written spec, but it omits stronger contextual framing such as `제주`, `제주시`, or a normalized lot-address form.

### Cause 2. The Geocoder Was Not Returning a Single Korean Match

The first pass geocoder returned weak or multiple matches for many Jeju lot-style queries. When representative unresolved queries were checked, the service returned unrelated global results rather than a single Jeju result.

Examples observed during review:

- `구좌읍 동복리1 759` returned unrelated results outside Korea
- `구좌읍 김녕리 571 -2` returned unrelated results outside Korea
- `구좌읍 한동리 1 387-2` returned unrelated results outside Korea
- `구좌읍 월정리 774-4` returned unrelated results outside Korea

### Cause 3. The Acceptance Rule Was Strict

The script accepts a result only when exactly one feature is returned. If the query returns zero or multiple features, the output is forced to:

- `resolved_address = NULL`
- `latitude = NULL`
- `longitude = NULL`
- `status = unresolved`

This explains why rows that are easy to find in a consumer search engine can still fail in the current output.

## Failure Pattern Counts

The unresolved rows with non-null `combined_address` are concentrated in the following address shapes.

| Pattern | Count |
| --- | ---: |
| Plain lot number | 71 |
| Hyphenated lot number | 61 |
| Multi-token address fragment | 54 |
| Split numeric tokens | 23 |

These patterns overlap. They are not separate row groups.

## Regional Concentration of Unresolved Non-Null Rows

Top regions in the unresolved-with-combined set:

| Region | Count |
| --- | ---: |
| 옛 제주시 | 37 |
| 애월읍 | 33 |
| 조천읍 | 27 |
| 구좌읍 | 22 |
| 한림읍 | 13 |
| 한경면 | 10 |
| 우도면 | 6 |
| 추자면 | 3 |

## Representative Resolved Cases

These show the kinds of inputs the first pass could resolve successfully.

| Region | Shrine | Combined Address |
| --- | --- | --- |
| 구좌읍 | 김녕 본향 사장빌레큰당 | `구좌읍 김녕리 21 21` |
| 구좌읍 | 동김녕 궤눼깃당 | `구좌읍 김녕리 21 21` |
| 구좌읍 | 세화리 본향 천자또 산신당 | `구좌읍 세화리 1 049-2` |
| 구좌읍 | 세화리 고는곶 일뤠 | `구좌읍 세화리 1 049-2` |
| 구좌읍 | 하도리 각시당 | `구좌읍 하도리 450-3` |
| 조천읍 | 와흘리 본향 한거리 하로산당 | `조천읍 와흘리 1 274-1` |

## Representative Unresolved Cases With Combined Address

These show the rows that looked search-capable but still failed in the first pass.

| Region | Shrine | Combined Address |
| --- | --- | --- |
| 구좌읍 | 동복리 본향 굴묵밧할망당 | `구좌읍 동복리1 759` |
| 구좌읍 | 동김녕리 성세깃당 | `구좌읍 김녕리 571 -2` |
| 구좌읍 | 서김녕 본향 노모리동산 일뤠당 | `구좌읍 김녕리 3417` |
| 구좌읍 | 월정 본향 서당머체큰당 | `구좌읍 월정리 1 79-8` |
| 구좌읍 | 월정리 베롱개 해신당 | `구좌읍 월정리 774-4` |
| 구좌읍 | 한동 본향 괴로본산국당 | `구좌읍 한동리 21 23` |
| 구좌읍 | 한동 망애물 해신당 | `구좌읍 한동리 1 387-2` |
| 구좌읍 | 평대 본향 신선백관 하르방당 | `구좌읍 한동리 656` |

## Actioned Identification Outcome

The failure identification step confirmed the following:

1. The unresolved population is dominated by geocoding failures on rows that did have searchable combined addresses.
2. Only a minority of unresolved rows are true null-address cases.
3. The current first-pass output should not be interpreted as evidence that the 151 combined-address failures are unsearchable.
4. The first-pass result is constrained by the specific geocoder and the exact-one-result acceptance rule used in `scripts/clean_shrines.py`.

## Operational Conclusion

The first pass succeeded as a strict cleansing implementation, but it did not achieve broad location recovery for Jeju lot-style shrine addresses. The follow-up identification step shows that the major recovery opportunity lies in the 151 unresolved rows that already contain non-null combined addresses.
