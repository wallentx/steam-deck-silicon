#!/usr/bin/env python3
"""Look for R64 frame-info and frame-control slots in saved data, at any byte alignment."""

import argparse
import csv
import hashlib
import json
import struct
import tarfile
from collections import Counter
from pathlib import Path


OPERATIONS = (("frame_info", 0x02050002, (4728, 4656)), ("frame_ctrl", 0x02050001, (2640,)))
RELEASE_DIGEST = "9747b3652e20746596b64b0b244bd23a047ba47d4eb3d392271cac08a615f28c"


def scan(stream, chunk_size=1024 * 1024):
    if chunk_size < 1:
        raise ValueError("chunk size must be positive")
    size = 0
    digest = hashlib.sha256()
    counts = Counter()
    examples = []
    tail = b""
    for chunk in iter(lambda: stream.read(chunk_size), b""):
        digest.update(chunk)
        data = tail + chunk
        for name, command_id, lengths in OPERATIONS:
            needle = struct.pack("<I", command_id)
            for field, label in ((4, name), (12, "done_" + name)):
                pos = data.find(needle, field)
                while pos >= 0:
                    start = pos - field
                    if start + 64 > len(data):
                        break
                    pos = data.find(needle, pos + 1)
                    if field == 12 and data[start + 4:start + 8] != b"\x01\x00\x01\x00":
                        continue
                    counts[label + "_id"] += 1
                    if field == 4:
                        length, = struct.unpack_from("<I", data, start + 16)
                        if length not in lengths:
                            continue
                        counts[label + "_size"] += 1
                    if sum(data[start:start + 63]) & 0xff == data[start + 63]:
                        counts[label + "_checksum"] += 1
                        if len(examples) < 20:
                            examples.append((label, size - len(tail) + start))
        # Exactly 63 carried bytes: a slot spanning a boundary is counted once.
        tail = data[-63:]
        size += len(chunk)
    return {"bytes": size, "sha256": digest.hexdigest(), "counts": dict(counts), "first_hits": examples}


def scan_release(path):
    with path.open("rb") as source:
        if hashlib.file_digest(source, "sha256").hexdigest() != RELEASE_DIGEST:
            raise ValueError("expected the original ML2 build 9601 release archive")
    inventory = Path(__file__).resolve().parents[1] / "evidence" / "host-index.tsv"
    with inventory.open(encoding="utf-8") as source:
        expected = {r["path"][8:]: r for r in csv.DictReader(source, delimiter="\t")
                    if r["path"].startswith("package/")}
    members = {}
    with tarfile.open(path, "r|gz") as archive:
        for member in archive:
            if not member.isreg():
                continue
            name = member.name.partition("/")[2]
            entry = expected.pop(name, None)
            if entry is None:
                raise ValueError(f"unexpected member: {name}")
            with archive.extractfile(member) as source:
                result = scan(source)
            if result["sha256"] != entry["sha256"] or result["bytes"] != int(entry["bytes"]):
                raise ValueError(f"member identity mismatch: {name}")
            members[name] = result
    if expected:
        raise ValueError("archive omitted indexed members")
    return members


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--release", action="store_true", help="verify and scan the 60 decompressed tar members")
    args = parser.parse_args()
    try:
        if not args.file.is_file():
            raise ValueError("expected a regular archive or capture file")
        if args.release:
            report = scan_release(args.file)
        else:
            with args.file.open("rb") as source:
                report = scan(source)
        print(json.dumps(report, indent=2))
    except (OSError, ValueError, tarfile.TarError) as exc:
        parser.exit(1, f"{exc}\n")
