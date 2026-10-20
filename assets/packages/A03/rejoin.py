"""Join downloaded archive parts. Run: python rejoin.py"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'PARTS.json').read_text(encoding='utf-8'))
output = root / manifest['archive']
if output.exists():
    raise SystemExit('Output already exists; choose another folder. No file was overwritten.')
# Verify all inputs before creating output.
for part in manifest['parts']:
    path = root / part['name']
    if path.stat().st_size != part['bytes']:
        raise SystemExit('Wrong size: ' + part['name'])
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != part['sha256']:
        raise SystemExit('Wrong SHA256: ' + part['name'])
whole = hashlib.sha256()
with output.open('xb') as destination:
    for part in manifest['parts']:
        with (root / part['name']).open('rb') as stream:
            while chunk := stream.read(1024 * 1024):
                destination.write(chunk)
                whole.update(chunk)
if output.stat().st_size != manifest['bytes'] or whole.hexdigest() != manifest['sha256']:
    raise SystemExit('Joined archive failed verification. Do not extract it.')
print('Verified:', output.name, whole.hexdigest())
print('Extract this ZIP. Preserve the Blender file and textures relative locations.')
