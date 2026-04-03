# Data Pipeline

## Pipeline Purpose

The data pipeline converts heterogeneous source materials into a structured spatial research dataset while preserving uncertainty, ownership, and sensitivity. The goal is not maximal standardization at any cost. The goal is accountable comparability across layers.

## Processing Stages

### 1. Source Ingestion

Each layer is first ingested in its native form.

- Heritage sites are ingested from the Korea Heritage Service source referenced in `documentation/heritage_sites.md`.
- Biennale venues are ingested from `documentation/venue_location.md`.
- Shrines are ingested from `shrine/shrines.csv`, using only the columns for region, shrine name, address, and ownership.

During ingestion, source records should be copied into a raw staging structure without premature correction. Source wording, null values, and ambiguous entries must be preserved for auditability.

### 2. Field Mapping and Normalization

Each source is mapped to a shared internal schema.

- Assign a stable `record_id`.
- Set `layer_type` to `heritage_site`, `venue`, or `shrine`.
- Map source-specific names into the canonical `name` field.
- Capture provenance through `source_name` and `source_reference`.
- Normalize ownership into the shared ownership model while retaining the original source wording where relevant.

This stage should standardize structure without flattening meaning. For example, ownership normalization should not erase the distinction between a source term that explicitly states individual ownership and one that implies joint or ambiguous control.

### 3. Data Cleaning

Cleaning addresses format inconsistency and missingness, but it does not remove records simply because they are incomplete.

- Trim spacing irregularities and obvious formatting artifacts.
- Preserve nulls explicitly rather than replacing them with guessed content.
- Retain ambiguous records in the working dataset.
- Separate source values from normalized values where reinterpretation may be needed later.

For venues and heritage sites, cleaning will likely be minimal relative to shrines. For shrines, cleaning must remain conservative because overcorrection can create false certainty.

### 4. Shrine-Specific Address Construction

Shrine records require a dedicated location-preparation step before geocoding.

- Read `region` and `address_raw` from the source.
- If `address_raw` is null, set `full_address_ko` to `undefined`.
- If `address_raw` is present, construct `full_address_ko` as `region + address_raw`.
- Preserve the original `address_raw` field separately for traceability.
- Do not discard records with vague fragments, coastal descriptions, or internally inconsistent notation.

This step is necessary because shrine addresses are often partial and only become minimally legible when combined with the region label.

### 5. Geocoding and Coordinate Assignment

Coordinate assignment should follow the evidentiary strength of the available location data.

- Use source-provided coordinates directly when they already exist and are trusted.
- Geocode constructed shrine addresses only when the address is sufficiently specific to justify a point.
- If geocoding returns a broad or weak match, record the result as approximate rather than exact.
- If no defensible coordinate can be assigned, leave latitude and longitude unset.

Coordinates must not be fabricated to satisfy schema completeness. A missing or approximate coordinate is preferable to a false exact one.

### 6. Uncertainty Scoring

Every record receives both a coordinate method and a confidence level.

- `exact` plus `high`: direct coordinates from a trusted source.
- `geocoded` plus `medium`: address-based point with reasonable specificity.
- `approximate` plus `low`: area-based or fragment-derived estimate.
- `undefined` plus `undefined`: no valid coordinate or intentionally withheld location.

Uncertainty scoring must incorporate both source quality and transformation history. A record derived from a fragmentary address should not receive the same status as one supplied with coordinates in the original source.

### 7. Access and Visibility Classification

After location resolution, each record should be evaluated for access status and visibility policy.

- Determine whether the site is public, restricted, sensitive, private, or unknown.
- Use ownership as one signal, not the only signal.
- Restrict coordinate exposure for sensitive or private locations.
- Allow uncertainty and access restrictions to coexist. A site may be both uncertain and access-sensitive.

This stage is especially important for shrines, where ethical exposure may be more consequential than analytical completeness.

### 8. Analytical Output Generation

The pipeline produces a normalized research dataset suitable for spatial comparison and later interaction analysis.

Outputs should include:

- layer-consistent records for heritage sites, venues, and shrines
- coordinates where defensible
- full Korean address or `undefined` where unresolved
- ownership and access classifications
- uncertainty indicators
- provenance and notes fields for review

The output dataset must support filtering, controlled visibility, and later relational analysis without requiring the system to re-interpret raw source ambiguity from scratch.

## Shrine Processing Logic

Shrines require the most careful procedural handling because they combine incompleteness with interpretive significance.

### Decision Rules

| Condition | Processing Rule | Output Consequence |
| --- | --- | --- |
| Address is null | Do not geocode. | `full_address_ko = undefined`, coordinates unset, confidence `undefined`. |
| Address exists but is fragmentary | Construct `region + address`, attempt cautious geocoding only if plausible. | Coordinates may be approximate; confidence likely `low` or `medium`. |
| Address resolves clearly | Accept geocoded point as provisional, not source-exact. | `coordinate_method = geocoded`, confidence `medium`. |
| Location is sensitive or private | Apply access restriction even if coordinates are known. | Coordinates may be generalized or hidden in published outputs. |
| Ownership is mixed or unclear | Preserve source phrase and normalize conservatively. | Use `shared` or `unknown` rather than forcing false precision. |

### Handling Undefined Cases

Undefined shrine records remain analytically valuable. They indicate places where location is culturally known, administratively partial, socially protected, or insufficiently documented. The pipeline must therefore treat `undefined` as an intentional state of knowledge rather than as a processing failure.

## Quality Assurance Principles

- Do not discard records solely because they cannot be geocoded.
- Do not upgrade approximate locations into exact ones.
- Do not infer public accessibility from the existence of a coordinate.
- Do not collapse raw ownership language into simplified categories without retaining the source form.
- Do not expose all resolved coordinates equally across research, internal, and public-facing outputs.
