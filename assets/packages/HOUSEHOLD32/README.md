# Household selection — 32 existing asset IDs

Representative archive of six table IDs, four shelving IDs, eight bathroom/laundry IDs, seven cookware IDs, and seven kitchen-tool IDs. Each ID contributes one adopted version; multi-object sets remain one ID. All entries are visual candidates, not finished or runtime-certified assets. No preservation-only draft is included in this selection.

Includes editable Blender files, LOD0/1/2 and existing collision FBX files, required local textures, and one representative render per ID. Preserve the folder layout for relative texture paths. ASSETS.json maps every ID and file; SHA256SUMS.json records file integrity.

Unity integration, runtime performance, collision optimization, player recognition, and commercial readiness remain unverified. Existing collision resources are not guarantees of optimized physics. Geometry, UVs, normals, material settings, transforms, texture pixels and assigned color spaces were compared during package preparation; independent extraction and reimport checks were performed.

External reference photos, internal reviews, source research, logs, and intermediate versions are excluded. This selection adds no new designs.

## Download and integrity
Download every .part file, PARTS.json and combine.py to one folder. Run `python combine.py` using Python 3.8+. The tool checks part and whole ZIP SHA-256 and refuses to overwrite an existing ZIP. Uploaded Git object hashes are compared with local byte-derived hashes; this is not a fresh full-byte download test.
