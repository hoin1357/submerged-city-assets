# A assets — local split ZIP

This directory is the public delivery candidate. It has not been uploaded.
Keep every `A_assets_final_r4.zip.partNNNN` file plus `parts_manifest.json` and `reassemble.py` together.

1. Verify without creating a second ZIP: `python reassemble.py --verify-only`
2. On a machine with enough space: `python reassemble.py --output A_assets_final_r4.zip`
3. Extract the ZIP with a ZIP64-capable tool, then open `index.html` and `README.md`.

Chunks are sequential bytes of a single ZIP, not independently extractable archives. Each is at most 20 MiB. The helper refuses to overwrite an existing output. Reserve space for the reconstructed ZIP and extracted members on the receiving machine. The sender generated chunks directly and did not store another whole ZIP.

Only the explicit current A delivery scope is included. Missing selections, omitted formats, history, material portability limits and absence of some final preview paths are recorded in `PACKAGE_SCOPE.json`. Old/unselected assets are not additional unique types. This package does not represent completion of the entire 2,000-asset project, user approval, or a merged A/B/parent library. No manufacturer reference photos, PDFs, credentials or internal QA conversations are intended for publication.
