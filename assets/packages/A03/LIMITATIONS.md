# A03 independent asset QA

Status: **PASS_WITH_DOCUMENTED_LIMITATIONS**  
Reviewed: 2026-10-17T18:18:48Z  
Scope: A017–A024, exactly **66 unique original landmark shells**. A017 has 10; each other family has 8. LOD1, collision and editable components are companions, not additional assets.

## Verified results

- **198 actual exported FBXs** reimported from a relocated copy with texture image-search fallback disabled: 66 LOD0, 66 LOD1 and 66 colliders. Exact audited bytes remain current.
- LOD0: **2,581,610 triangles**, range **18,417–57,146** per shell. LOD1: **686,174**; colliders: **1,107,380**. Per-asset LOD reduction: **49.32–93.26%**.
- **66 distinct normalized triangle geometries and vertex sets**. No size-only, material/color-only, horizontal-rotation-only or mirror-only duplicate vertex sets were detected. Final visual review covered all 66 asset tiles.
- All reimported coordinates and UV0 values are finite; no loose vertices or triangles below **1e-10 m²** using conservative double/float32 area checks. All actual colliders have zero boundary and nonmanifold edge counts.
- **65,178/65,178 declared-route rays clear**, evenly split among LOD0, LOD1 and colliders. These include actual openings, atrium paths, ramps and swim-well routes, rather than purely painted portals. A supplemental **4,842/4,842 rays clear** check covers the four LOD1-specific lower-sampling helix polylines.
- Zero local origins and unit scale retained; all four source scenes use metres. Maximum render-bound discrepancy against its own LOD manifest is **0.000007090 m**. LOD1 has its own measured bounds rather than a claim of exact LOD0 envelope equality.
- **Zero exposed coplanar overlap pairs** across all 132 render FBXs. Double-precision, consistently projected plane matching and exterior/interior visibility samples include rear and raised-underside surfaces. Numeric overlaps narrower than 20 μm are separately recorded (1404 LOD0; 1238 LOD1), avoiding false flags for float-conversion microstrips.
- LOD projected occupancy sampled **1,824,768 paired ray positions** across three 96×96 projections per asset. Lowest IoU is **88.137%**, A024-06, axis 1. Higher-resolution masks and rendered comparisons were reviewed where thin-detail removal produces larger differences.

## Source, materials, references and visual review

The final master Blend was copied to another folder and reopened with copied textures. All 198 expected asset meshes and 24 referenced source images resolve locally. All 58,954 material-bearing mesh objects, including editable components, use exact canonical SC_ material names compatible with the optional Unity helper; no appended .001/.002 slot-name mismatch was found.

Eight original shared material sets supply 40 valid 1024×1024 PNGs, byte-identical to A01. Metallic RGB packing is exact; smoothness alpha matches inverse roughness within one 8-bit level. Surface materials use image textures, Principled shading and normal-map nodes. UV0 is intentionally tiled.

All 66 per-ID provenance entries and all 17 photo files/hashes were checked, and all 17 actual reference photographs were independently viewed. Documentation separates observed structural cues from authored proportions, layouts and synthesis, including non-NYC precedents. It does not imply 66 different photo locations. Photographs are excluded from distribution.

Final visual review covers every shell across eight family contact sheets and the final representative/LOD previews recorded in qa/visual_review_final.json. Source and image hashes bind those observations to this signoff.

The optional Unity helper passed **static review only**. Its namespace, class and menu are distinct from earlier batches; execution is manual with confirmation and scoped writes. See qa/UNITY_HELPER_STATIC_REVIEW.md.

## Required limitations

- Unity Editor is unavailable here. C# compilation, Unity importing/rendering, physics/collider cooking, play mode, builds and target-hardware performance were not executed.
- Route rays test declared clear line corridors at center plus eight perpendicular offsets. They do not certify capsule sweeps, walkable slopes, climbing, jumping, movement-controller behavior or a completed playable level. Tower upper access is intentionally through open vertical swim wells, without a full stair system.
- LOD1 is optional and intended for distant use; retain LOD0 for close cameras or appearance consistency. It removes thin facade ribs, column profiles, crown tiers, trim and some slim railings. A023-08 visibly changes facade material-area distribution when pale reveal frames are removed. Projected occupancy is not identical: minimum sampled IoU is 88.14%. Primary structure and declared routes were retained in the tested samples; LOD distances and visible transition quality need target-scene tuning.
- A020-04 retains a minor visible stepped/faceted shoulder where differently sampled barrel and groin outer profiles meet. It is not described as a seamless roof transition; no route-blocking or coplanar-overlap defect was detected there.
- UV0 is intentionally tiled/overlapping at 2 repeats per metre. No unique UV1/lightmap atlas is supplied. Project lighting, shader remaps, texture/platform settings, LOD thresholds and dense-scene budgets need integration review.
- Colliders are separate non-convex static architectural meshes, intended without Rigidbody. Render components may retain intentional buried/contact intersections and are not promised to be one watertight Boolean-unioned shell. Sampled overlap/ray tests are not exhaustive all-angle or gameplay proofs.
- The architecture is original synthesis guided by 17 actual viewed photo references, not measured replicas or photogrammetry. All 66 reference mappings and 17 photo/hash records were checked. Photograph license metadata is provenance, not legal clearance; source photographs are excluded from delivery.
- Each original shell counts once. LOD1, colliders, editable components, materials and reused prefabs do not increase the 66-asset count. No engineering approval, universal engine compatibility or production/Steam shipping-ready certification is made. Final archive integrity is checked separately.

## Signoff and evidence

No remaining blocking findings in the stated tests. FINAL_QA_STATUS.json binds the exact final master, manifests, reference map, texture manifest, helper and supporting evidence hashes. The asset manifest binds all exported files and individual previews. Later edits require the relevant recheck and refreshed signoff. Archive integrity is a separate final packaging check.

Supporting evidence under qa/:

- `qa/reimport_summary.json`
- `qa/fbx_reimport_audit.json`
- `qa/exposed_fbx_final_lod0.json`
- `qa/exposed_fbx_final_lod1.json`
- `qa/lod_silhouette_audit.json`
- `qa/source_portability_audit.json`
- `qa/provenance_audit.json`
- `qa/manifest_provenance_binding.json`
- `qa/texture_audit.json`
- `qa/photo_visual_review.json`
- `qa/visual_review_final.json`
- `qa/UNITY_HELPER_STATIC_REVIEW.md`
- `qa/unity_helper_static_review.json`
- `qa/lod1_route_sampling_audit.json`

QA modified neither delivered A01/A02 nor production A03. Transient smoke files, superseded diagnostics, relocated copies and machine-specific audit scripts are excluded from distribution.
