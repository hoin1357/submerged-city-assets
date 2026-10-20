"""Reconstruct archived delivery ZIPs. Python 3.11+; no file is overwritten."""
import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parent
m = json.loads((root / 'BACKUP_PARTS.json').read_text(encoding='utf-8'))
for archive in m['archives']:
    output = root / archive['archive']
    if output.exists():
        with output.open('rb') as stream:
            sha = hashlib.file_digest(stream, 'sha256').hexdigest()
        if output.stat().st_size == archive['bytes'] and sha == archive['sha256']:
            print('Already verified:', output.name)
            continue
        raise SystemExit('Existing output does not match; use a clean folder: ' + output.name)
    for part in archive['parts']:
        path = root / part['name']
        if path.stat().st_size != part['bytes']:
            raise SystemExit('Wrong part size: ' + part['name'])
        with path.open('rb') as stream:
            sha = hashlib.file_digest(stream, 'sha256').hexdigest()
        if sha != part['sha256']:
            raise SystemExit('Wrong part SHA256: ' + part['name'])
    whole = hashlib.sha256()
    with output.open('xb') as destination:
        for part in archive['parts']:
            with (root / part['name']).open('rb') as stream:
                while chunk := stream.read(1024 * 1024):
                    destination.write(chunk)
                    whole.update(chunk)
    if output.stat().st_size != archive['bytes'] or whole.hexdigest() != archive['sha256']:
        raise SystemExit('Joined ZIP failed verification: ' + output.name)
    print('Verified:', output.name, whole.hexdigest())
print('All archive bytes verified. Follow the delivery extraction/install instructions next.')
