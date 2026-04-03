# Ethics and Access

## Why Spatial Visibility Is Sensitive

This project works with locations that do not share the same public status, institutional framing, or social exposure. Some points are formal cultural assets or public venues; others may be privately held, locally known, ritually meaningful, or unevenly documented. To place all of them on a map with equal precision would produce a false neutrality. Spatial visibility is not merely a technical matter. It affects access, interpretation, and potential intrusion.

The ethical requirement of this system is therefore not only to represent location, but to regulate how location becomes visible. Precision must be treated as a controlled disclosure, not an automatic output.

## Ownership-Based Filtering

Ownership is a core attribute because it affects both analytical use and exposure risk.

### Ownership Categories

| Ownership | Meaning | Default Handling |
| --- | --- | --- |
| `government` | State, provincial, or municipal control | Usually suitable for broader analytical visibility, subject to site sensitivity. |
| `corporate` | Corporate or institutional ownership | Visible with caution; access may still be restricted. |
| `private` | Individually owned or personally controlled site | Restricted by default. |
| `shared` | Joint or mixed ownership | Requires case-by-case review. |
| `unknown` | Not recorded or not interpretable | Do not assume openness. |

### Filtering Principles

- The system must allow ownership-based filtering in all analytical views.
- Ownership should influence visibility defaults, not merely serve as descriptive metadata.
- Unknown ownership must be treated conservatively.
- Mixed or shared ownership should not be collapsed into a more permissive category.

## Private and Sensitive Site Handling

Private and sensitive sites require differentiated protection.

### Protected Treatment

- Private sites should not automatically expose exact coordinates.
- Sensitive sites may require generalized spatial representation even when not privately owned.
- A site can be publicly known and still require coordinate restraint.
- Shrine records deserve heightened caution because ritual or locally embedded significance may exceed what administrative metadata reveals.

### Acceptable Representation Modes

| Representation Mode | Use Case |
| --- | --- |
| Exact point | Publicly accessible, non-sensitive site with defensible coordinates. |
| Generalized point | Approximate display for uncertain or moderately sensitive sites. |
| Area-level display | Region or neighborhood representation without site-level precision. |
| Hidden coordinates | Private, highly sensitive, or undefined cases. |

## Coordinate Exposure Control

Coordinate exposure should be treated as a publication policy layer separate from the existence of internal coordinates.

### Principle

A record may possess internally stored coordinates while still being prohibited from public point-level display.

### Visibility Policy Levels

| Visibility Policy | Meaning |
| --- | --- |
| `full` | Exact coordinates may be shown. |
| `generalized` | Coordinates may be displayed only in reduced precision or displaced form. |
| `hidden` | Coordinates are withheld from public-facing outputs. |
| `internal_only` | Exact coordinates retained only for restricted research use. |

### Control Logic

- Apply visibility rules after assessing ownership, access class, and confidence.
- Do not expose a low-confidence point as if it were exact simply because a map requires a marker.
- Do not expose private or uncertain shrine locations at full precision by default.
- Permit different visibility policies for internal analysis and public presentation.

## Access Classification

Access classification should remain explicit rather than inferred.

| Access Class | Meaning |
| --- | --- |
| `public` | Intended for open public entry or visitation. |
| `restricted` | Access depends on schedule, permission, or site conditions. |
| `sensitive` | Exposure may create cultural, social, or site-integrity concerns. |
| `private` | Not appropriate for general public access. |
| `unknown` | Access conditions cannot yet be determined. |

Ownership and access are related but not identical. A government-owned site may still be restricted or sensitive. A privately owned site may be visible at area level while remaining inaccessible.

## Research Responsibility

The project should preserve the distinction between knowing that a place exists and deciding how precisely to represent it. This distinction is especially important in a research setting where mapped visibility may influence later visitation, interpretation, and interaction intensity. Ethical mapping in this project therefore requires selective disclosure, conservative treatment of uncertainty, and a refusal to equate data availability with public entitlement to access.
