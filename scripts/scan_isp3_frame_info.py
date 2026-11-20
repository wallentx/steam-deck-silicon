#!/usr/bin/env python3
"""Find frame-info literals in hash-identified ML2 ELF sections. Uses read-only debugfs."""

import argparse
import csv
import hashlib
import struct
import subprocess
from pathlib import Path


PARTITIONS = {"system": "system.raw", "vendor": "vendor.raw", "userdata": "userdata.raw",
              "cvip_ro": "cvip.raw"}
FRAME_INFO_LE = b"\x02\x00\x05\x02"


def sections(data):
    """Yield name, executable flag and extent for allocated SHT_PROGBITS of at least four bytes."""
    if data[:4] != b"\x7fELF" or data[5] != 1:
        return
    if data[4] == 2:
        table, = struct.unpack_from("<Q", data, 40)
        stride, count, strings = struct.unpack_from("<3H", data, 58)
        fmt = "<II4QII2Q"
    elif data[4] == 1:
        table, = struct.unpack_from("<I", data, 32)
        stride, count, strings = struct.unpack_from("<3H", data, 46)
        fmt = "<10I"
    else:
        return
    if not count or strings >= count or stride < struct.calcsize(fmt) or table + stride * count > len(data):
        return
    headers = [struct.unpack_from(fmt, data, table + i * stride) for i in range(count)]
    str_start, str_size = headers[strings][4:6]
    names = data[str_start:str_start + str_size]
    for name, kind, flags, _, offset, size, *_ in headers:
        if kind == 1 and flags & 2 and size >= 4:
            if offset + size > len(data):
                raise ValueError("section extends beyond member")
            end_name = names.find(b"\0", name)
            label = names[name:end_name].decode("ascii", errors="replace") if end_name >= 0 else ""
            yield label or "<unnamed>", bool(flags & 4), offset, size


def scan(directory):
    evidence = Path(__file__).resolve().parents[1] / "evidence"
    files = eligible = hit_files = 0
    for partition in PARTITIONS.values():
        if not (directory / partition).is_file():
            raise ValueError(f"expected regular image file {partition}")
    for index in ("host-index.tsv", "cvip-side.tsv"):
        with (evidence / index).open(encoding="utf-8") as src:
            for row in csv.DictReader(src, delimiter="\t"):
                part, _, path = row["path"].partition("/")
                if part not in PARTITIONS or "ELF" not in row.get("format", row.get("type", "")).upper():
                    continue
                if any(ch in path for ch in '"\\\r\n'):
                    raise ValueError(f"unsupported archive path: {path!r}")
                args = ["debugfs", "-R", f'cat "/{path}"', str(directory / PARTITIONS[part])]
                data = subprocess.run(args, capture_output=True, check=True).stdout
                if hashlib.sha256(data).hexdigest() != row["sha256"]:
                    raise ValueError(f"member hash mismatch: {row['path']}")
                files += 1
                alloc = list(sections(data))
                eligible += bool(alloc)
                hit = False
                for name, executable, offset, size in alloc:
                    end = offset + size
                    pos = data.find(FRAME_INFO_LE, offset, end)
                    if pos < 0:
                        continue
                    hit = True
                    if executable:
                        while pos >= 0:
                            print(f"{row['path']} {name} file+{pos:#x}", flush=True)
                            pos = data.find(FRAME_INFO_LE, pos + 1, end)
                hit_files += hit
    print(f"{files} verified ELF members, {eligible} with eligible sections, {hit_files} with literals")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="directory containing the four expanded ext4 image files")
    args = parser.parse_args()
    try:
        scan(args.directory)
    except (OSError, ValueError, struct.error, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"{exc}\n")
