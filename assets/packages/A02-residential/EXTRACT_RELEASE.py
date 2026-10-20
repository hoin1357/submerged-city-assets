#!/usr/bin/env python3
"""Verify and safely join independent residential ZIP parts into one directory.

Python 3.9+ standard library only; downloads nothing. No binary concatenation.
All archives and member hashes are checked before extraction. Extraction uses a
private staging directory and a final rename. Existing different, unexpected or
incomplete output is never overwritten. An identical complete output is a no-op.
Use bundle and destination directories you control, with no concurrent changes
by other processes. Path checks do not defend against hostile parent-directory
replacement. Hashes detect corruption; a trusted externally supplied inventory hash can also
be pinned with --expected-inventory-sha256. Hashes alone are not a signature.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
import zipfile

TOP = "A02_residential_54_v2"
LIMIT = 20_000_000
MAX_MEMBER = 512 * 1024 * 1024
MAX_TOTAL = 4 * 1024 * 1024 * 1024
MAX_INDEX = 16 * 1024 * 1024
SUPPORT = {"EXTRACT_RELEASE.py", "EXTRACT_RELEASE.ps1", "EXTRACT_RELEASE_WINDOWS.cmd", "EXTRACT_ALL_README.txt", "WINDOWS_README_KO.txt"}
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10)),
            *(prefix + suffix for prefix in ("COM", "LPT") for suffix in ("\u00b9", "\u00b2", "\u00b3"))}


class IntegrityError(ValueError):
    pass


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise IntegrityError(f"Duplicate JSON key: {key}")
        value[key] = item
    return value


def json_bytes(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique_object)


def safe_relative(name):
    if not isinstance(name, str) or not name or "\\" in name:
        raise IntegrityError(f"Unsafe path: {name!r}")
    p = PurePosixPath(name)
    if p.is_absolute() or str(p) != name or any(part in ("", ".", "..") for part in p.parts):
        raise IntegrityError(f"Noncanonical/traversing path: {name!r}")
    for part in p.parts:
        if any(ord(c) < 32 or c in '<>:"|?*' for c in part) or part.endswith((".", " ")):
            raise IntegrityError(f"Unsafe cross-platform filename: {name!r}")
        if part.split(".", 1)[0].upper() in RESERVED:
            raise IntegrityError(f"Reserved Windows filename: {name!r}")
    return p


def no_links(path, require_exists=True):
    """Reject symlinks, Windows junctions/reparse points and symlink ancestors."""
    path = Path(os.path.abspath(path))
    for current in [path, *path.parents]:
        try:
            info = current.lstat()
        except FileNotFoundError:
            if current == path and not require_exists:
                continue
            raise IntegrityError(f"Path/parent does not exist: {current}")
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise IntegrityError(f"Symlink/junction/reparse point is not permitted: {current}")
    return path


def regular_file(path):
    path = no_links(path)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise IntegrityError(f"Not a regular file: {path}")
    return path


def sha256(path):
    h = hashlib.sha256()
    with regular_file(path).open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def checked_record(row, key="path"):
    if not isinstance(row, dict):
        raise IntegrityError("Inventory record must be an object")
    safe_relative(row.get(key))
    if type(row.get("bytes")) is not int or not 0 <= row["bytes"] <= MAX_MEMBER:
        raise IntegrityError(f"Invalid/unbounded byte count: {row.get(key)}")
    if not re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", "")):
        raise IntegrityError(f"Invalid SHA256: {row.get(key)}")
    return row


def limited_bytes(path, limit=MAX_INDEX):
    target = regular_file(path)
    if target.stat().st_size > limit:
        raise IntegrityError(f"Index is too large: {target.name}")
    return target.read_bytes()


def hash_lines(data):
    result = {}
    for line in data.decode("utf-8").splitlines():
        if "  " not in line:
            raise IntegrityError("Malformed SHA256SUMS line")
        digest, name = line.split("  ", 1)
        safe_relative(name)
        if not re.fullmatch(r"[0-9a-f]{64}", digest) or name in result:
            raise IntegrityError(f"Duplicate/invalid checksum entry: {name}")
        result[name] = digest
    return result


def chunk_path(bundle, canonical, expected):
    """Only canonical names or an exact ' (digits)' download suffix are eligible."""
    p = PurePosixPath(canonical)
    if len(p.parts) != 1:
        raise IntegrityError("ZIP names must not contain directories")
    expression = re.compile(re.escape(p.stem) + r"(?: \(([1-9][0-9]*)\))?" + re.escape(p.suffix) + r"\Z")
    candidates = sorted((path for path in bundle.iterdir() if expression.fullmatch(path.name)), key=lambda x: (x.name != canonical, x.name))
    if not candidates:
        raise IntegrityError(f"Missing ZIP part: {canonical}. Keep its exact name or an exact numeric download suffix such as ' (1)'.")
    good = []
    for path in candidates:
        regular_file(path)
        if path.stat().st_size == expected["bytes"] and sha256(path) == expected["sha256"]:
            good.append(path)
    if not good:
        raise IntegrityError(f"No hash/size-matching copy of {canonical}; do not extract the damaged/mismatched download")
    return good[0]


def inspect_info(info, record):
    safe_relative(info.filename)
    kind = stat.S_IFMT(info.external_attr >> 16)
    if info.is_dir() or kind not in (0, stat.S_IFREG) or info.external_attr & 0x400:
        raise IntegrityError(f"Link, directory, device or reparse ZIP entry is forbidden: {info.filename}")
    if info.flag_bits & 1 or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
        raise IntegrityError(f"Encrypted/unsupported ZIP member: {info.filename}")
    if info.file_size != record["bytes"] or info.file_size > MAX_MEMBER:
        raise IntegrityError(f"Member uncompressed size mismatch: {info.filename}")


def consume_member(archive, info, expected, output=None, capture=False):
    if capture and expected["bytes"] > MAX_INDEX:
        raise IntegrityError(f"Inner index is too large: {info.filename}")
    h, count, pieces = hashlib.sha256(), 0, []
    with archive.open(info, "r") as stream:
        while True:
            data = stream.read(1024 * 1024)
            if not data:
                break
            count += len(data)
            if count > expected["bytes"]:
                raise IntegrityError(f"Member exceeds its declared size: {info.filename}")
            h.update(data)
            if output is not None:
                output.write(data)
            if capture:
                pieces.append(data)
    if count != expected["bytes"] or h.hexdigest() != expected["sha256"]:
        raise IntegrityError(f"Member hash/size mismatch: {info.filename}")
    return b"".join(pieces) if capture else None


def verify_bundle(bundle, expected_inventory_sha256=None):
    bundle = no_links(bundle)
    if not bundle.is_dir():
        raise IntegrityError("Bundle path must be a directory")
    raw_inventory = limited_bytes(bundle / "chunk_inventory.json")
    inventory_hash = hashlib.sha256(raw_inventory).hexdigest()
    if expected_inventory_sha256 is not None and inventory_hash != expected_inventory_sha256.lower():
        raise IntegrityError("Inventory differs from the externally supplied trusted SHA256")
    inventory = json_bytes(raw_inventory)
    if inventory.get("schema") != "residential54.zip-inventory.v1" or inventory.get("top_directory") != TOP or inventory.get("byte_limit") != LIMIT:
        raise IntegrityError("Incorrect inventory schema, top directory or ZIP byte limit")
    cap = inventory.get("requested_byte_cap")
    if type(cap) is not int or not 1_000_000 <= cap <= LIMIT:
        raise IntegrityError("Invalid requested ZIP byte cap")
    chunks = inventory.get("chunks", [])
    if not isinstance(chunks, list) or not 1 <= len(chunks) <= 999:
        raise IntegrityError("Invalid chunk count")
    expected_names = {f"{TOP}_part{i:02d}_of{len(chunks):02d}.zip" for i in range(1, len(chunks) + 1)}
    if len({c.get("file") for c in chunks}) != len(chunks) or {c.get("file") for c in chunks} != expected_names:
        raise IntegrityError("ZIP names/count must exactly cover the canonical part01..partNN sequence")
    support_rows = inventory.get("support_files", [])
    if len(support_rows) != len(SUPPORT) or {r.get("file") for r in support_rows} != SUPPORT:
        raise IntegrityError("Required extractor, Windows launcher and instruction inventory is incomplete")
    support = {}
    for row in support_rows:
        checked_record(row, "file")
        path = regular_file(bundle / row["file"])
        if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
            raise IntegrityError(f"Support helper/instruction hash mismatch: {row['file']}")
        support[row["file"]] = row
    outer_sums = hash_lines(limited_bytes(bundle / "SHA256SUMS.txt"))
    if set(outer_sums) != expected_names | SUPPORT | {"chunk_inventory.json"}:
        raise IntegrityError("Outer SHA256SUMS inventory differs from the exact bundle file set")
    if outer_sums["chunk_inventory.json"] != inventory_hash:
        raise IntegrityError("Inventory fails outer SHA256SUMS verification")
    for name, row in support.items():
        if outer_sums[name] != row["sha256"]:
            raise IntegrityError(f"Support file SHA256SUMS mismatch: {name}")
    members, folded, selection = {}, set(), []
    directory_spellings = {}
    total = 0
    for chunk in chunks:
        checked_record(chunk, "file")
        if not 0 < chunk["bytes"] <= cap or outer_sums[chunk["file"]] != chunk["sha256"]:
            raise IntegrityError(f"Chunk is oversized or fails the outer checksum inventory: {chunk['file']}")
        path = chunk_path(bundle, chunk["file"], chunk)
        rows = chunk.get("members", [])
        if not isinstance(rows, list) or not rows:
            raise IntegrityError("Every ZIP must have a nonempty member inventory")
        current = {}
        for row in rows:
            checked_record(row)
            name = row["path"]
            if not name.startswith(TOP + "/") or len(PurePosixPath(name).parts) < 2:
                raise IntegrityError(f"Member is outside the required top directory: {name}")
            if name in members or name.casefold() in folded:
                raise IntegrityError(f"Duplicate/case-colliding ZIP payload: {name}")
            folded.add(name.casefold())
            for parent in PurePosixPath(name).parents:
                spelling = str(parent)
                prior = directory_spellings.setdefault(spelling.casefold(), spelling)
                if prior != spelling:
                    raise IntegrityError(f"Case-colliding directory spellings: {prior} / {spelling}")
            members[name] = row
            current[name] = row
            total += row["bytes"]
            if total > MAX_TOTAL or len(members) > 100_000:
                raise IntegrityError("Declared extraction exceeds safety bounds")
        selection.append((chunk, path, current))
    declared_paths = inventory.get("complete_member_paths", [])
    if len(declared_paths) != len(members) or set(declared_paths) != set(members):
        raise IntegrityError("Complete member inventory differs from chunk member inventories")
    # Also forbid a file and a child of that file, including case-only variants.
    for name in members:
        for ancestor in PurePosixPath(name).parents:
            if str(ancestor).casefold() in folded:
                raise IntegrityError(f"File/directory prefix collision: {name}")
    inner = {}
    for chunk, path, current in selection:
        with zipfile.ZipFile(regular_file(path)) as archive:
            infos = archive.infolist()
            if len(infos) != len(current) or {i.filename for i in infos} != set(current):
                raise IntegrityError(f"Unexpected/missing/duplicate ZIP members: {path.name}")
            for info in infos:
                record = current[info.filename]
                inspect_info(info, record)
                relative = info.filename[len(TOP) + 1:]
                capture = relative in ("STAGING_MANIFEST.json", "FILE_SHA256SUMS.txt")
                data = consume_member(archive, info, record, capture=capture)
                if capture:
                    inner[relative] = data
        if sha256(path) != chunk["sha256"]:
            raise IntegrityError(f"ZIP changed during verification: {path.name}")
    if set(inner) != {"STAGING_MANIFEST.json", "FILE_SHA256SUMS.txt"}:
        raise IntegrityError("Missing inner staging manifest/checksum inventory")
    staging = json_bytes(inner["STAGING_MANIFEST.json"])
    if staging.get("schema") != "residential54.staging-allowlist.v1" or staging.get("top_directory") != TOP:
        raise IntegrityError("Invalid inner staging-manifest identity")
    staged_rows = staging.get("files", [])
    staged = {}
    for row in staged_rows:
        checked_record(row)
        if row["path"] in staged:
            raise IntegrityError("Duplicate staging-manifest path")
        staged[row["path"]] = row
    generated = staging.get("generated_index_files")
    if generated != ["STAGING_MANIFEST.json", "FILE_SHA256SUMS.txt"]:
        raise IntegrityError("Unexpected generated staging-index file set")
    if {TOP + "/" + p for p in set(staged) | set(generated)} != set(members):
        raise IntegrityError("ZIP members differ from the explicit staging allowlist")
    for relative, row in staged.items():
        record = members[TOP + "/" + relative]
        if row["bytes"] != record["bytes"] or row["sha256"] != record["sha256"]:
            raise IntegrityError(f"Staging manifest hash/size differs: {relative}")
    inner_sums = hash_lines(inner["FILE_SHA256SUMS.txt"])
    if set(inner_sums) != set(staged) | {"STAGING_MANIFEST.json"}:
        raise IntegrityError("Inner FILE_SHA256SUMS set differs from the complete staged file list")
    for relative, expected in inner_sums.items():
        if members[TOP + "/" + relative]["sha256"] != expected:
            raise IntegrityError(f"Inner manifest checksum mismatch: {relative}")
    return {"bundle": bundle, "inventory": inventory, "inventory_sha256": inventory_hash,
            "members": members, "selection": selection, "uncompressed_bytes": total}


def existing_identical(target, members):
    if not target.exists() and not target.is_symlink():
        return False
    no_links(target)
    if not target.is_dir():
        raise IntegrityError(f"Existing target is not a directory; refusing overwrite: {target}")
    expected = {name[len(TOP) + 1:]: row for name, row in members.items()}
    expected_dirs = {str(parent) for relative in expected for parent in PurePosixPath(relative).parents if str(parent) != "."}
    actual = set()
    for directory, subdirs, files in os.walk(target, followlinks=False):
        for name in subdirs:
            subdir = no_links(Path(directory) / name)
            if subdir.relative_to(target).as_posix() not in expected_dirs:
                raise IntegrityError(f"Existing output contains an unexpected directory: {subdir}")
        for name in files:
            path = regular_file(Path(directory) / name)
            rel = path.relative_to(target).as_posix()
            actual.add(rel)
            if rel not in expected or path.stat().st_size != expected[rel]["bytes"] or sha256(path) != expected[rel]["sha256"]:
                raise IntegrityError(f"Existing output differs or contains an unexpected file; refusing overwrite: {rel}")
    if actual != set(expected):
        raise IntegrityError("Existing output is incomplete. Choose a new empty destination parent; partial output is not merged or overwritten.")
    return True


def publish_without_overwrite(source, destination):
    """Atomic OS-enforced no-replace rename, including a racing empty directory."""
    if os.name == "nt":
        # Windows os.rename fails whenever the destination already exists.
        os.rename(source, destination)
        return
    library = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux") and hasattr(library, "renameat2"):
        call = library.renameat2
        call.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        call.restype = ctypes.c_int
        result = call(-100, os.fsencode(source), -100, os.fsencode(destination), 1)  # RENAME_NOREPLACE
    elif sys.platform == "darwin" and hasattr(library, "renamex_np"):
        call = library.renamex_np
        call.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        call.restype = ctypes.c_int
        result = call(os.fsencode(source), os.fsencode(destination), 4)  # RENAME_EXCL
    else:
        raise IntegrityError("This OS/runtime lacks an exclusive atomic rename. Refusing a racy fallback; use the Windows native helper or verified manual extraction.")
    if result != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))


def extract_bundle(bundle, destination, expected_inventory_sha256=None, verify_only=False):
    checked = verify_bundle(bundle, expected_inventory_sha256)
    result = {"status": "verified_only" if verify_only else "pending_extraction", "parts": len(checked["selection"]),
              "files": len(checked["members"]), "uncompressed_bytes": checked["uncompressed_bytes"],
              "inventory_sha256": checked["inventory_sha256"],
              "selected_parts": [{"canonical": chunk["file"], "actual": path.name} for chunk, path, _ in checked["selection"]]}
    if verify_only:
        return result
    destination = no_links(destination)
    if not destination.is_dir():
        raise IntegrityError("Destination parent must already exist as a real directory")
    target = destination / TOP
    if existing_identical(target, checked["members"]):
        return dict(result, status="already_present_identical_no_changes", directory=str(target))
    lock = destination / f".{TOP}.extract.lock"
    lock_fd = None
    temporary = None
    try:
        lock_fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(lock_fd, f"pid={os.getpid()}\n".encode("ascii"))
        if target.exists() or target.is_symlink():
            raise IntegrityError("Output appeared during validation; refusing overwrite")
        temporary = Path(tempfile.mkdtemp(prefix=f".{TOP}.extract-staging-", dir=destination))
        staged_top = temporary / TOP
        staged_top.mkdir()
        for chunk, path, current in checked["selection"]:
            if sha256(path) != chunk["sha256"]:
                raise IntegrityError(f"ZIP changed before extraction: {path.name}")
            with zipfile.ZipFile(regular_file(path)) as archive:
                infos = archive.infolist()
                if len(infos) != len(current) or {i.filename for i in infos} != set(current):
                    raise IntegrityError(f"ZIP members changed after verification: {path.name}")
                for info in infos:
                    record = current[info.filename]
                    inspect_info(info, record)
                    relative = info.filename[len(TOP) + 1:]
                    output = staged_top.joinpath(*safe_relative(relative).parts)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    with output.open("xb") as stream:
                        consume_member(archive, info, record, output=stream)
                    output.chmod(0o644)
            if sha256(path) != chunk["sha256"]:
                raise IntegrityError(f"ZIP changed during extraction: {path.name}")
        # Recheck every written byte against the fully validated manifest before
        # exposing anything. Existing output is never merged or replaced.
        if not existing_identical(staged_top, checked["members"]):
            raise IntegrityError("Internal staged extraction is missing")
        if target.exists() or target.is_symlink():
            raise IntegrityError("Output appeared during extraction; refusing overwrite")
        no_links(destination)
        publish_without_overwrite(staged_top, target)
        return dict(result, status="extracted_and_verified", directory=str(target))
    finally:
        if temporary is not None and temporary.exists():
            shutil.rmtree(temporary)
        if lock_fd is not None:
            os.close(lock_fd)
            lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).absolute().parent)
    parser.add_argument("--destination", type=Path, help="Existing parent directory; a new A02_residential_54_v2 folder is created inside")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--expected-inventory-sha256", help="Optional trusted hash supplied separately by the sender")
    args = parser.parse_args()
    try:
        result = extract_bundle(args.bundle, args.destination or args.bundle, args.expected_inventory_sha256, args.verify_only)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, RuntimeError) as error:
        parser.exit(2, "SAFE EXTRACTION BLOCKED: " + str(error) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
