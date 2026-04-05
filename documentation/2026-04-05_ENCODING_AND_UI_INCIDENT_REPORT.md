# 2026-04-05 Encoding and UI Incident Report

## Summary

On April 5, 2026, we encountered a cluster of regressions in the generated map interface. The visible symptoms were:

- Korean UI text appearing as broken characters (mojibake)
- Venue popup description text rendering with broken encoding
- A broken Unicode close button glyph
- Category color coordination disappearing, causing multiple layers to fall back to gray styling
- The Google map control order drifting away from the intended design

These issues appeared in the generated `index.html`, but the root causes were not limited to that file. The problems were traced back to the template-generation pipeline, primarily `scripts/build_index_html.py`, plus a few generated outputs that had been rebuilt from bad source strings.

## What Went Wrong

### 1. Corrupted Korean UI strings in the template layer

Some fixed Korean UI labels inside `scripts/build_index_html.py` were already stored in a corrupted form. Because `index.html` is generated from that script, every rebuild reproduced the corruption.

This means the browser was not the real problem. The build source itself contained broken text.

### 2. Template strings and data strings were mixed in the same large inline HTML/JS template

The generator embeds a large amount of HTML, CSS, JavaScript, and JSON in one place. When a few hardcoded labels became corrupted, they were harder to detect because:

- the rest of the data still looked valid
- many actual shrine and heritage names were correct
- only specific UI literals were broken

This created the false impression that the issue was random or browser-specific.

### 3. Palette keys no longer matched the real category labels

Some heritage and shrine category labels were broken or mismatched, which caused palette lookup failures. When a category key does not match the expected Korean label, the code falls back to the default gray marker style.

That is why the map lost its intended color coordination.

### 4. Unsafe glyph usage for close buttons

The close button relied on a character that had become corrupted in the template. Once that character was mis-encoded, the interface showed a broken Unicode symbol instead of a clean close icon.

### 5. A venue popup label remained broken after broader fixes

Even after the major encoding fixes were applied, one venue popup body string remained corrupted. This happened because it was a separate hardcoded literal inside the template and needed its own direct correction.

## Fixes Applied

The following fixes were completed on April 5, 2026:

### Template and generation fixes

- Repaired corrupted Korean UI literals in `scripts/build_index_html.py`
- Rebuilt `index.html` from the corrected template instead of hand-patching only the output
- Corrected the venue popup description text to `비엔날레 장소`

### UI integrity fixes

- Restored the Korean interface labels in the header, filters, sidebar, and popups
- Restored the intended order and placement of Google map controls
- Restored the route toggle and older map layout behavior requested by design reference

### Marker styling fixes

- Repaired heritage and shrine palette keys
- Restored category-based color coordination so markers no longer collapse to gray fallback styling

### Safe character fixes

- Replaced unsafe/broken close glyphs with the HTML-safe entity `&times;`
- Corrected related accessibility labels such as `닫기`

### Output verification

- Rebuilt the generated map page after fixes
- Verified that corrected Korean strings exist in both the template source and generated output
- Verified that the venue popup description string is now correct in both places

## Root Cause

The root cause was a template-source encoding failure, not a browser rendering issue.

More specifically:

- Korean UI strings inside the generator were corrupted at some earlier point
- the generator kept reproducing those corrupted strings into `index.html`
- fallback behavior in the palette logic masked category mismatches by rendering gray markers
- isolated hardcoded literals made it easy for one or two broken strings to survive broader fixes

In short: the build source was partially poisoned, and the generated file faithfully reflected that bad source.

## Why It Happened

The most likely mechanism is one of the standard UTF-8 corruption paths:

- a UTF-8 file was opened or saved with the wrong encoding
- a corrupted terminal/editor output was copied back into source
- a few literals were manually edited in a context that did not preserve UTF-8 correctly

Because the project uses large inline template blocks, a single corrupted literal can sit unnoticed inside otherwise valid code for a long time.

## Is This Fixed at the Fundamental Level?

Yes, the immediate source-level problem has been fixed.

This was not treated as a cosmetic-only `index.html` patch. The actual generator source was corrected and the output was rebuilt from the corrected source.

That means:

- future rebuilds will preserve the corrected UI strings
- the venue popup description text will remain correct when regenerated
- palette lookups will continue using the repaired category labels

However, a true "never again" standard requires prevention measures, not just a repair. Those measures are documented below.

## Prevention Plan: How This Should Never Happen Again

To prevent a recurrence, the project should adopt the following rules.

### 1. Treat UTF-8 as mandatory everywhere

All source files containing Korean text must be saved and edited as UTF-8.

Required rule:

- `scripts/build_index_html.py`
- generated HTML files
- JSON and CSV files containing Korean labels
- documentation files

must always be written and reviewed as UTF-8 text.

### 2. Centralize UI copy

Hardcoded UI labels should be moved into a small, centralized constant map instead of being scattered through a large template.

Benefits:

- easier review
- easier localization
- easier encoding validation
- fewer hidden broken literals

### 3. Add automated mojibake detection to the build step

The build process should fail if suspicious mojibake patterns appear in the output.

Examples of suspicious fragments:

- `ë`
- `ì`
- `â`
- common broken UTF-8 sequences in Korean UI text

This should be checked in:

- the template source
- the generated `index.html`

### 4. Add semantic verification for key UI strings

The build should assert the presence of required known-good labels such as:

- `비엔날레 장소`
- `비엔날레 베뉴`
- `설명`
- `닫기`
- `문화유산`
- `신당`

If those required strings are missing after a build, the build should fail.

### 5. Add validation for palette key coverage

Palette definitions should be checked against actual category values in the source data.

The build should warn or fail if:

- a heritage category has no palette mapping
- a shrine ownership category has no palette mapping
- a category falls back to gray unexpectedly

### 6. Prefer safe entities or stable icons for close buttons

Wherever possible, UI controls should use:

- HTML entities such as `&times;`, or
- stable SVG/icon markup

instead of relying on pasted special characters.

### 7. Add a post-build review script

After generating `index.html`, a lightweight verification script should check:

- known labels are intact
- no suspicious mojibake exists
- palette keys match categories
- the close button uses a safe representation

## Recommended Next Technical Step

The repository should add a dedicated verification script such as:

- `scripts/verify_generated_map.py`

This script should automatically:

- scan template files for mojibake markers
- scan generated HTML for mojibake markers
- assert the presence of critical Korean UI labels
- validate palette coverage for all current categories

The build should not be considered successful unless this verification passes.

## Files Involved in the Incident and Fixes

Primary source file:

- `scripts/build_index_html.py`

Primary generated output:

- `index.html`

Related supporting outputs and data updated during the broader repair work:

- `locations/final_shrines.json`
- `shrine/final_shrines.json`
- `scripts/export_final_shrines_json.py`
- shrine status/image export assets and related CSV outputs

## Closing Note

This incident was not caused by Korean text being inherently unstable. It was caused by a lack of validation around a generator that contains hardcoded multilingual UI strings.

The direct bug is fixed now. To ensure it does not return, the project must move from manual visual checking to explicit encoding and output validation in the build pipeline.
