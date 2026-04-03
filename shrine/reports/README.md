# Shrine Reports

This folder contains reporting generated after the first shrine cleansing pass.

- `FIRST_PASS_REPORT.md`: documents the premise of the initial preprocessing run, the rules applied, and the actual return profile.
- `FAILURE_IDENTIFICATION_REPORT.md`: documents the follow-up review of unresolved rows, identifies where the failures came from, and distinguishes true null cases from geocoding failures on rows that did have combined addresses.
- `SECOND_PASS_REPORT.md`: documents the Kakao-based rerun as a separate second pass and records the updated return profile after changing the geocoder.
- `THIRD_PASS_REPORT.md`: documents the Kakao + Google fallback rerun as a separate third pass and records the updated return profile after adding Google Geocoding fallback.
