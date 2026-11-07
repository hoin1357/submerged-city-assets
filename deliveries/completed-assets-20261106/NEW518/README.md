# NEW518: open-ribbon Y vegetable peeler

Original static visual 3 D prop. Nine model files: LOD0, LOD1 and LOD2, each supplied as BLEND, FBX and GLB. Only the accepted final static models are included.

## Materials and use

The models use embedded scalar PBR materials. No external textures, material companion files, manufacturer photographs or reference PDFs are required or included. Blender import checks do not certify every engine or renderer. No rig, animation, physical performance, safety, manufacturing or exact commercial-product replica is guaranteed. Lower LODs may show deliberate faceting.

UV layouts are provided. Many use separated triangle charts; continuous paint-ready unwrapping and universal lightmap/baking suitability are not guaranteed.

## Asset-specific scope and limitations

- Manufacturer nominal overall dimensions are 110 x 65 x 12 mm. The chosen XYZ interpretation is 65 x 12 x 110 mm, including the side eye loop in maximum width. Component dimensions, ribbon gauge, blade slot, curvature, eye loop and pivot seats are artist estimates from photographs rather than a toleranced drawing.
- The visible blade has small estimated static pivot-style contacts, not fully covered end faces. Per end: LOD0 about 0.449258 mm 2, LOD1 about 0.436483 mm 2, LOD2 about 0.420090 mm 2. These cover about 19.1–20.4% of blade-end face and 29.4–30.3% of disc, with about 1.751–1.780 mm 2 uncovered blade-end area. Source photos have localized end pivots; all-LOD reverse macro and hero review finds the simplified seats visibly attached, not floating. Full end-face support is not a necessary visual correction. No exact pivot fit, moving mechanism, cutting function, safety or manufacturing certification is implied.
- Five other member-seat planes per model have full member face coverage within floating-point precision: two crossbar ends, two support-disc/frame faces and the eye-loop/frame seat. These are intentional coplanar contacts between separate closed material shells, not fused topology or volumetric intersections.
- World-coordinate vertex identity rounds at 1e-7 m. All closed connected components additionally have a single cyclic triangle link at every vertex. Strict self tests exclude triangles sharing a vertex and exact point/edge tangencies, and test nonadjacent coplanar positive-area overlaps. No global exact-arithmetic proof is claimed.
- Contact-plane membership uses 1e-7 m tolerance. Actual component separating halfspace margins are exactly zero in the fresh imported data at intended contacts, and noncontact pairs have positive gaps of at least 0.400001 mm. Raw BVH overlap counts include the declared coplanar seats and cannot alone be interpreted as volume penetration.
- All 432 aperture rays across grip, head, blade slot and eye loop have positive projected clearance disks, minimum radius about 0.250 mm. Slot projection is about 47.6 x 1.5 mm and normal blade wall thickness about 0.368918 mm. Sampled frame/eye wall sections are at least 1.000 / 0.800958 mm, respectively; these samples are not a universal minimum-thickness certification.
- Two scalar PBR materials provide an aluminium-looking frame and steel-looking blade/supports. Component metallurgy is not established. There are no image textures, branding, wear, external dependencies or normal-map texture detail. UV0 is bounded and nonoverlapping at positive area threshold 1e-12, not claimed as a handcrafted texture or lightmap atlas.
- Blender 4.3.2 fresh imports, independent CPU renders and direct GLB binary payload decoding were validated. No target-engine/device performance, animation, deformation, collision or runtime-lighting test was performed. Lower LODs show polygonal frame/eye-loop and support-disc faceting in macro views; LOD2 is for small-screen/distant use. Bright highlights and CPU render noise limit fine surface assessment.

## Reference attribution and rights

The following published product or catalog pages informed the original geometry and nominal dimensions. They are reference attributions, not included third-party assets or claims of endorsement. Photographs and documents remain the property of their respective rights holders; no public reuse license for those images/documents is asserted. Reference-photo licenses, if any, do not automatically license the newly authored mesh. This README grants no additional model license or trademark/design-right clearance.

- https://www.sam-turner.co.uk/products/victorinox-rex-peeler
- https://www.victorinox.com/en/Products/Cutlery/Graters-and-Peelers/REX-Peeler/p/6.0900
