# Third Pass Report

## Purpose

This report documents the third preprocessing pass on `shrine/shrines.csv`. It is separate from the first and second pass reports and records the rerun performed after adding Google Geocoding as fallback after Kakao.

## Basis of the Third Pass

The third pass kept the same cleansing and status rules as the earlier passes.

What changed was the geocoding stack:

- Kakao Local API remained the primary geocoder
- Google Geocoding API was added as fallback when Kakao did not return one accepted result
- the row retention, classification rules, and output schema remained unchanged

The implementation used `scripts/clean_shrines.py`.

Relevant script sections:

- `.env` loading: `scripts/clean_shrines.py` lines 69-88
- Kakao endpoint configuration: `scripts/clean_shrines.py` lines 63-66
- Kakao geocoding request: `scripts/clean_shrines.py` lines 160-194
- Google fallback geocoding request: `scripts/clean_shrines.py` lines 197-224
- geocoder fallback order: `scripts/clean_shrines.py` lines 227-231
- row-level status assignment: `scripts/clean_shrines.py` lines 249-260

## Returned Outputs

The third pass refreshed:

- `shrine/cleaned_shrines.csv`
- `shrine/cleaned_shrines.json`

## Row Totals

| Measure | Count |
| --- | ---: |
| Total input rows | 192 |
| `resolved` rows | 165 |
| `partial` rows | 1 |
| `unresolved` rows | 26 |

## Address Presence Profile

| Measure | Count |
| --- | ---: |
| Rows with `raw_address = NULL` | 26 |
| Rows with non-null `combined_address` | 166 |
| `resolved` rows with non-null `combined_address` | 165 |
| `partial` rows with non-null `combined_address` | 1 |
| `unresolved` rows with non-null `combined_address` | 0 |

## Change From the Second Pass

Compared with the second pass:

| Measure | Second Pass | Third Pass | Change |
| --- | ---: | ---: | ---: |
| `resolved` | 86 | 165 | +79 |
| `partial` | 1 | 1 | 0 |
| `unresolved` | 105 | 26 | -79 |
| `unresolved` with non-null `combined_address` | 79 | 0 | -79 |

## Main Result

The third pass resolved every row that had a non-null `combined_address`.

This means:

- all rows with address text retained in the structured output are now geocoded
- the only remaining unresolved rows are the rows with true null or invalid source addresses
- the single vague row remains `partial`

## Representative Resolved Cases

Examples resolved in the third pass include:

| Region | Shrine | Combined Address | Resolved Address |
| --- | --- | --- | --- |
| 구좌읍 | 동복리 본향 굴묵밧할망당 | `구좌읍 동복리1 759` | `1759 Dongbok-ri, Gujwa-eup, Cheju, Jeju-do, South Korea` |
| 구좌읍 | 김녕 본향 사장빌레큰당 | `구좌읍 김녕리 21 21` | `2121 Gimnyeong-ri, Gujwa-eup, Cheju, Jeju-do, South Korea` |
| 구좌읍 | 월정 본향 서당머체큰당 | `구좌읍 월정리 1 79-8` | `179-8 Woljeong-ri, Gujwa-eup, Cheju, Jeju-do, South Korea` |
| 구좌읍 | 한동 본향 괴로본산국당 | `구좌읍 한동리 21 23` | `2123 Handong-ri, Gujwa-eup, Cheju, Jeju-do, South Korea` |
| 구좌읍 | 한동 망애물 해신당 | `구좌읍 한동리 1 387-2` | `1387-2 Handong-ri, Gujwa-eup, Cheju, Jeju-do, South Korea` |
| 구좌읍 | 세화리 본향 천자또 산신당 | `구좌읍 세화리 1 049-2` | `1049-2 Sehwa-ri, Gujwa-eup, Cheju, Jeju-do, South Korea` |
| 조천읍 | 와흘리 본향 한거리 하로산당 | `조천읍 와흘리 1 274-1` | `1274-1 Wahul-ri, Jocheon-eup, Cheju, Jeju-do, South Korea` |
| 애월읍 | 고내리 본향 큰당 | `애월읍 고내리 11 1 4` | `1114 Gonae-ri, Aewol-eup, Cheju, Jeju-do, South Korea` |

## Remaining Unresolved Cases

The remaining unresolved rows are now limited to rows with null or invalid source address values.

No rows with non-null `combined_address` remain unresolved after the third pass.

## Operational Reading of the Third Pass

The third pass is the strongest geocoding run in the current sequence. It preserves the same cleansing framework while materially improving location recovery through the addition of Google fallback.

It also introduces one new output characteristic:

- resolved address formatting is now mixed across providers
- Kakao tends to return Korean-formatted address strings
- Google fallback can return English-formatted internationalized address strings

This means the spatial resolution problem is substantially improved, but output address formatting is now heterogeneous and may require a later normalization step if Korean-only presentation is required.
