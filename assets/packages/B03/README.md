# B03 교통시설 76종

모든 .part 파일과 PARTS.json, combine.py를 같은 폴더에 내려받고 Python 3.8 이상에서 `python combine.py`를 실행하세요. 각 조각과 완성 ZIP의 SHA-256을 확인합니다. 이미 있는 ZIP은 덮어쓰지 않습니다.

커밋된 Git 객체 해시를 로컬 바이트의 객체 해시와 대조합니다. 전체 바이트 재다운로드 검증과는 다릅니다.

B03 Transit76

76 transit/environment assets. Consumer package: 152 LOD0/LOD1 FBX, 76 static collision FBX, 22 MOVING_REVIEW geometry FBX, 3 shared-support assemblies (9 FBX), 50 PBR texture PNGs and 76 individual preview PNGs. Editable companion: 79 Blender files (76 assets + 3 assemblies) and the same 50 textures.

Extract the entire package before use; preserve its folder layout. Texture references are relative. Authoring units are metres; Blender Z-up, FBX axis conversion for Unity. Keep import scale 1. Some Blender files are collection libraries; use File > Append > Collection if no scene appears.

Textures: basecolor is sRGB. Normal, roughness and metallic maps are Non-Color/linear. metallic_smoothness uses R=metallic, A=1-roughness. The extra packed map is for engine-specific material setup. FBX does not preserve the Blender glass shader completely; configure transmission/transparency manually in the target engine.

Operating limits
These are inert visual assets, not operational systems. No controller, sensors, avoidance or transport-safety behaviour is included. MOVING_REVIEW files contain functional moving-part geometry, not dynamic-ready collision. Static nonconvex collision meshes are not rigidbody-ready. Unity runtime integration has not been verified. No safety, accessibility or building-code certification is implied.

For B025-03/04/08 adjacent to B025-01, use the supplied complete shared-support assemblies, not overlapping raw ballast/sleepers. Do not hide or remove an owner section: shared supports may otherwise disappear. Support meshes are partitioned while rails, gauge and ports remain unchanged.

Reference dimensions: sidewalk 0.15 m, reserved walking route 2 m, platform 1.10 m, rail top 0 m, gauge 1.435 m. Subway clearance 3.70 m, commuter threshold 1.25 m and cargo clearance 3.84 m are distinct constraints. B024-04 tray operates geometrically between 0.15 and 1.10 m, not the commuter threshold. Its conceptual sequence is low entry flap, close both flaps, lift, high exit flap, lower; no runtime sequence is implemented.

B024-01 half-height bay is 3.32 m wide; B024-02 full-height bay is 3.60 m. Open passage is 1.60 m, movement 0.80 m, and closed-door guide support 55 mm; no floor threshold is supplied.

Public packages exclude production scripts, private QA, reference material and installation preview scenes. Geometry, transforms, UVs, material parameters, normals and image colorspaces were checked across editable save/reopen. Import validation does not substitute for engine integration testing.
