# Data Structure

## Overview

The project combines three spatial datasets: heritage sites, biennale venues, and shrines. Each layer must retain source-specific meaning while supporting a shared analytical structure. Standardization is necessary for comparison, but standardization must not erase differences in confidence, ownership, or access sensitivity.

The common model therefore separates:

- source-provided facts
- normalized spatial attributes
- uncertainty and provenance metadata
- access and ownership controls

## Shared Core Fields

The following fields should be available across all layers where applicable.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `record_id` | string | yes | Stable internal identifier. |
| `layer_type` | string | yes | One of `heritage_site`, `venue`, `shrine`. |
| `name` | string | yes | Canonical site or venue name. |
| `source_name` | string | yes | Data source label, such as Korea Heritage Service, Jeju Biennale venue list, or shrine CSV. |
| `source_reference` | string | no | Source URL, file path, or document reference. |
| `latitude` | number | no | WGS84 latitude. May be withheld for sensitive cases. |
| `longitude` | number | no | WGS84 longitude. May be withheld for sensitive cases. |
| `coordinate_method` | string | yes | `exact`, `geocoded`, `approximate`, or `undefined`. |
| `confidence_level` | string | yes | `high`, `medium`, `low`, or `undefined`. |
| `full_address_ko` | string | no | Full Korean address or resolved location string. |
| `region` | string | no | Administrative or dataset-supplied regional label. |
| `ownership` | string | no | Core filter field. Normalize to `government`, `corporate`, `private`, `shared`, `unknown`, or `not_applicable`. |
| `access_class` | string | yes | `public`, `restricted`, `sensitive`, `private`, or `unknown`. |
| `visibility_policy` | string | yes | Defines whether coordinates may be fully shown, generalized, or hidden. |
| `notes` | string | no | Retains source ambiguity, caveats, or interpretive remarks. |

## Layer Schema: Heritage Sites

### Purpose

Represents formally recognized cultural assets retrieved from the Korea Heritage Service.

### Required Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `record_id` | string | yes | Internal identifier. |
| `layer_type` | string | yes | Always `heritage_site`. |
| `name` | string | yes | Heritage site name. |
| `category` | string | yes | Source-provided type or heritage classification. |
| `latitude` | number | yes if available from source | Exact coordinates expected where provided. |
| `longitude` | number | yes if available from source | Exact coordinates expected where provided. |
| `coordinate_method` | string | yes | Usually `exact`; otherwise document derivation. |
| `confidence_level` | string | yes | Usually `high` when coordinates come directly from source. |
| `full_address_ko` | string | no | Include if available from source or later enrichment. |
| `ownership` | string | no | Use source or contextual enrichment when known; otherwise `unknown` or `not_applicable`. |
| `access_class` | string | yes | Cultural designation does not guarantee unrestricted access. |
| `visibility_policy` | string | yes | Default may be full visibility unless later restricted. |

### Notes on Uncertainty

Heritage records are expected to carry relatively high locational confidence, but categorical certainty should not be confused with access certainty. Even a formally recognized site may require restricted or generalized display depending on site conditions.

## Layer Schema: Biennale Venues

### Purpose

Represents Jeju Biennale venues as contemporary exhibition or event locations.

### Required Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `record_id` | string | yes | Internal identifier. |
| `layer_type` | string | yes | Always `venue`. |
| `name` | string | yes | Venue name. |
| `latitude` | number | yes | Coordinates are explicitly listed in the source document. |
| `longitude` | number | yes | Coordinates are explicitly listed in the source document. |
| `google_maps_url` | string | yes | Source-provided reference URL. |
| `coordinate_method` | string | yes | Normally `exact` from the source list. |
| `confidence_level` | string | yes | Normally `high`. |
| `full_address_ko` | string | no | Optional enrichment if later resolved. |
| `ownership` | string | yes | Core governance field; use `unknown` if not yet resolved. |
| `access_class` | string | yes | Most venues will likely be `public` or `restricted`, but this must remain explicit. |
| `visibility_policy` | string | yes | Usually full visibility, subject to site-specific constraints. |

### Notes on Uncertainty

Venue coordinates are relatively stable in the current source format, but venue openness may vary by event schedule, programming period, or institutional control. Access and ownership therefore remain independent fields rather than assumptions.

## Layer Schema: Shrines

### Purpose

Represents shrine sites recorded in the shrine CSV, including ambiguous, incomplete, and uncertain cases.

### Source Columns Used

Only the following source columns are used from `shrine/shrines.csv`.

| Source Column | Normalized Field | Notes |
| --- | --- | --- |
| `지역` | `region` | Administrative or local area label. |
| `신당명` | `name` | Shrine name. |
| `주소` | `address_raw` | May be null, incomplete, or non-standard. |
| `소유권` | `ownership_raw` | Must be normalized into the ownership model. |

### Required Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `record_id` | string | yes | Internal identifier. |
| `layer_type` | string | yes | Always `shrine`. |
| `name` | string | yes | Shrine name from source. |
| `region` | string | yes | Source region. |
| `address_raw` | string | no | Original address fragment from source. |
| `full_address_ko` | string | yes | Construct as `region + address` when address exists; otherwise `undefined`. |
| `ownership` | string | yes | Normalize from source values such as national, provincial, personal, shared, or missing. |
| `ownership_raw` | string | no | Preserve original wording for audit and reinterpretation. |
| `latitude` | number | no | May be absent when unresolved or intentionally withheld. |
| `longitude` | number | no | May be absent when unresolved or intentionally withheld. |
| `coordinate_method` | string | yes | `exact`, `geocoded`, `approximate`, or `undefined`. |
| `confidence_level` | string | yes | Must reflect geocoding quality and source clarity. |
| `access_class` | string | yes | Particularly important for shrine sensitivity. |
| `visibility_policy` | string | yes | May require generalized or hidden coordinates. |
| `uncertainty_note` | string | no | Explains why the record is geocoded, approximate, or undefined. |
| `notes` | string | no | Preserve unresolved ambiguity rather than discarding it. |

### Shrine Address Rules

- If `주소` is null, `full_address_ko` must be set to `undefined`.
- If `주소` exists, construct `full_address_ko` by combining `지역 + 주소`.
- Incomplete addresses are retained and marked through uncertainty fields rather than removed.
- Ambiguous records remain in the dataset even if coordinates cannot be confidently resolved.

### Ownership Normalization

Shrine ownership is a core analytical and ethical attribute. Source terms should be normalized into the following categories.

| Normalized Value | Use |
| --- | --- |
| `government` | National, provincial, municipal, or other state-linked ownership. |
| `corporate` | Corporate or organizational ownership where identified. |
| `private` | Individually held ownership. |
| `shared` | Joint ownership, including mixed private or communal cases. |
| `unknown` | Ownership not recorded or unclear. |

Source phrases such as `국가`, `제주도`, `개인`, or compound entries like `개인, 공동` should be preserved in `ownership_raw` even after normalization.

## Uncertainty Model

Uncertainty is not ancillary metadata. It is part of the project's interpretive integrity.

| Confidence Level | Meaning | Typical Condition |
| --- | --- | --- |
| `high` | Exact location confirmed from source or trusted coordinate record. | Source supplies coordinates directly. |
| `medium` | Location produced through address-based geocoding with acceptable specificity. | Full address resolves to a plausible point. |
| `low` | Only approximate location can be inferred. | Fragmentary address, area-only reference, or conflicting cues. |
| `undefined` | No defensible coordinate can be assigned. | Null address, unresolved ambiguity, or intentional suppression. |

The pair `coordinate_method` and `confidence_level` should always be interpreted together. A shrine may have coordinates present but still carry low confidence if the point represents only an approximate area rather than an exact site.
