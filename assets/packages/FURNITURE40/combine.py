"""Reassemble downloaded package parts and verify SHA-256 (Python 3)."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "PARTS.json").read_text(encoding="utf-8"))
for archive in manifest["archives"]:
    name = archive["name"]
    if Path(name).name != name:
        raise ValueError("Unsafe archive name")
    target = root / name
    if target.exists():
        raise FileExistsError(f"Keep or rename existing file first: {name}")
    temp = target.with_suffix(target.suffix + ".assembling")
    total = hashlib.sha256()
    size = 0
    with temp.open("xb") as output:
        for part in archive["parts"]:
            if Path(part["name"]).name != part["name"]:
                raise ValueError("Unsafe part name")
            digest = hashlib.sha256()
            part_size = 0
            with (root / part["name"]).open("rb") as source:
                while data := source.read(1024 * 1024):
                    digest.update(data)
                    total.update(data)
                    output.write(data)
                    size += len(data)
                    part_size += len(data)
            if part_size != part["bytes"] or digest.hexdigest() != part["sha256"]:
                raise ValueError(f"Part verification failed: {part['name']}")
    if size != archive["bytes"] or total.hexdigest() != archive["sha256"]:
        raise ValueError(f"Archive verification failed: {name}")
    temp.rename(target)
    print(f"Verified: {name} ({size} bytes)")
