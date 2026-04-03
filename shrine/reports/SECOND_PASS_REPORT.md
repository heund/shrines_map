# Second Pass Report

## Purpose

This report documents the second preprocessing pass on `shrine/shrines.csv`. It is separate from the first pass and records the rerun performed after changing the geocoder to Kakao Local API.

## Basis of the Second Pass

The second pass kept the same cleansing and status rules as the first pass.

What changed was the geocoding layer:

- geocoder changed to Kakao Local API
- the script loaded the Kakao REST API key from the project `.env`
- the row retention, classification rules, and output schema remained unchanged

The implementation used `scripts/clean_shrines.py`.

Relevant script sections:

- `.env` loading: `scripts/clean_shrines.py` lines 67-85
- Kakao endpoint configuration: `scripts/clean_shrines.py` lines 63-64
- Kakao geocoding request: `scripts/clean_shrines.py` lines 160-174
- row-level status assignment: `scripts/clean_shrines.py` lines 202-221

## Returned Outputs

The second pass refreshed:

- `shrine/cleaned_shrines.csv`
- `shrine/cleaned_shrines.json`

## Row Totals

| Measure | Count |
| --- | ---: |
| Total input rows | 192 |
| `resolved` rows | 86 |
| `partial` rows | 1 |
| `unresolved` rows | 105 |

## Address Presence Profile

| Measure | Count |
| --- | ---: |
| Rows with `raw_address = NULL` | 26 |
| Rows with non-null `combined_address` | 166 |
| `resolved` rows with non-null `combined_address` | 86 |
| `partial` rows with non-null `combined_address` | 1 |
| `unresolved` rows with non-null `combined_address` | 79 |

## Change From the First Pass

Compared with the first pass:

| Measure | First Pass | Second Pass | Change |
| --- | ---: | ---: | ---: |
| `resolved` | 14 | 86 | +72 |
| `partial` | 1 | 1 | 0 |
| `unresolved` | 177 | 105 | -72 |
| `unresolved` with non-null `combined_address` | 151 | 79 | -72 |

## Main Result

The second pass confirms that a substantial share of the first-pass failures came from the geocoder rather than from the shrine data itself.

Kakao recovered 72 rows that had previously remained unresolved. This materially changes the interpretation of the unresolved set:

- true null-address rows remain unresolved
- vague-address handling remains unchanged
- a large portion of valid Jeju lot-style addresses are now resolved successfully

## Representative Newly Resolved Cases

Examples now resolved in the second pass include:

| Region | Shrine | Combined Address | Resolved Address |
| --- | --- | --- | --- |
| 구좌읍 | 동김녕리 성세깃당 | `구좌읍 김녕리 571 -2` | `제주특별자치도 제주시 구좌읍 김녕리 571-2` |
| 구좌읍 | 서김녕 본향 노모리동산 일뤠당 | `구좌읍 김녕리 3417` | `제주특별자치도 제주시 구좌읍 김녕리 3417` |
| 구좌읍 | 월정리 베롱개 해신당 | `구좌읍 월정리 774-4` | `제주특별자치도 제주시 구좌읍 월정리 774-4` |
| 구좌읍 | 행원리 본향 큰당 | `구좌읍 행원리 573-6` | `제주특별자치도 제주시 구좌읍 행원리 573-6` |
| 구좌읍 | 평대 본향 신선백관 하르방당 | `구좌읍 한동리 656` | `제주특별자치도 제주시 구좌읍 한동리 656` |
| 구좌읍 | 평대(동동) 수대깃당 | `구좌읍 평대리 975` | `제주특별자치도 제주시 구좌읍 평대리 975` |
| 구좌읍 | 하도리 본향 삼싱불도할망당 | `구좌읍 하도리 2884` | `제주특별자치도 제주시 구좌읍 하도리 2884` |
| 구좌읍 | 송당리 상덕천 체오름 산신당 | `구좌읍 송당리 산 61` | `제주특별자치도 제주시 구좌읍 송당리 산 61` |

## Remaining Unresolved Cases

The second pass still leaves 79 rows unresolved despite having non-null `combined_address`.

Representative remaining cases include:

| Region | Shrine | Combined Address |
| --- | --- | --- |
| 구좌읍 | 동복리 본향 굴묵밧할망당 | `구좌읍 동복리1 759` |
| 구좌읍 | 김녕 본향 사장빌레큰당 | `구좌읍 김녕리 21 21` |
| 구좌읍 | 동김녕 궤눼깃당 | `구좌읍 김녕리 21 21` |
| 구좌읍 | 월정 본향 서당머체큰당 | `구좌읍 월정리 1 79-8` |
| 구좌읍 | 한동 본향 괴로본산국당 | `구좌읍 한동리 21 23` |
| 구좌읍 | 한동 망애물 해신당 | `구좌읍 한동리 1 387-2` |
| 구좌읍 | 세화리 본향 천자또 산신당 | `구좌읍 세화리 1 049-2` |
| 구좌읍 | 하도리 남당 | `구좌읍 하도리 1 778` |

## Operational Reading of the Second Pass

The second pass should be understood as a materially improved geocoding run under the same cleansing framework. It does not change the classification logic. It changes the geocoding success rate.

The result is a stronger resolved dataset, while still preserving:

- all input rows
- unresolved null-address rows
- the single vague row as `partial`
- the original output schema
