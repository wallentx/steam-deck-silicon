#!/usr/bin/env python3
"""Compare packaged graphics-mailbox handlers in two identified BIOS files, offline."""

import argparse
import hashlib
import struct
from pathlib import Path


IMAGES = {
    "Jupiter": (17778888, "c8b1e749ad709bf20899eed59bd9012a8482b55003d2785134f0b17876a240d9",
                (0x168c70, 0x968c70), 0x73d0),
    "Mero": (16777216, "f4b050e9b7f518b084b4184b7818a7e03cdabc975f20357d99a11f66469c5b62",
             (0x100000, 0x880000), 0x7420),
}
MESSAGES = ((1, "test"), (2, "firmware version"), (3, "interface version"),
            (6, "ISP down"), (7, "ISP up"), (14, "ISP ICLK"), (15, "ISP XCLK"), (23, "SOCCLK"))


def smu_parts(image, directory):
    if image[directory:directory + 4] != b"$PL2":
        raise ValueError("missing PSP level-two directory")
    count, = struct.unpack_from("<I", image, directory + 8)
    parts = {}
    for index in range(count):
        kind, length, location = struct.unpack_from("<IIQ", image, directory + 16 + 16 * index)
        if kind not in (8, 0x12):
            continue
        if location >> 62 != 2 or kind in parts:
            raise ValueError("unexpected directory entry")
        start = directory + (location & ((1 << 62) - 1))
        entry = image[start:start + length]
        if len(entry) != 0x40200 or entry[0x10:0x14] != b"$PS1":
            raise ValueError("unexpected SMU wrapper")
        parts[kind] = entry
    if parts.keys() != {8, 0x12}:
        raise ValueError("missing SMU firmware entry")
    return parts


def inspect(name, path):
    size, digest, directories, table_pointer = IMAGES[name]
    if not path.is_file() or path.stat().st_size != size:
        raise ValueError(f"{path}: expected the {name} capsule specified in the report")
    image = path.read_bytes()
    if hashlib.sha256(image).hexdigest() != digest:
        raise ValueError(f"{path}: SHA-256 mismatch")
    parts = smu_parts(image, directories[0])
    if parts != smu_parts(image, directories[1]):
        raise ValueError("redundant directories contain different SMU images")
    body = parts[8][0x100:-0x100]
    version, = struct.unpack_from("<I", body)
    table, = struct.unpack_from("<I", body, table_pointer)
    print(f"{name} firmware {version:#010x}, port-0 table {table:#x}")
    for msg, label in MESSAGES:
        handler, flags = struct.unpack_from("<II", body, table + 8 * msg)
        print(f"  {msg:#04x} {label:18s} handler={handler:#07x} flags={flags:#x}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jupiter", type=Path, help="F7A0133_sign.fd")
    parser.add_argument("mero", type=Path, help="build 9601 demophon_bios.FD")
    args = parser.parse_args()
    try:
        inspect("Jupiter", args.jupiter)
        inspect("Mero", args.mero)
    except (OSError, ValueError, struct.error) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
