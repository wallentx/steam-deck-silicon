"""Decode a cached AMD discovery blob and optionally compare a stock BIOS record."""
import argparse
import hashlib
import struct
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("capture", type=Path)
parser.add_argument("--bios", type=Path)
parser.add_argument("--offset", type=lambda n: int(n, 0), default=0x234770,
                    help="stock discovery offset (default applies to LCD F7A0131/F7A0133)")
args = parser.parse_args()


def record(data):
    if len(data) < 60 or data[:4] != bytes.fromhex("07142128"):
        raise ValueError("Missing discovery header")
    checksum, length = struct.unpack_from("<HH", data, 8)
    if not 60 <= length <= len(data) or sum(data[10:length]) % 65536 != checksum:
        raise ValueError("Invalid discovery size or checksum")
    tables = []
    for i in range(6):
        start, checksum, size, _ = struct.unpack_from("<4H", data, 12 + 8*i)
        if start == 0:
            continue
        table = data[start:start+size]
        if start < 60 or start+size > length or sum(table) % 65536 != checksum:
            raise ValueError(f"Invalid discovery table {i}")
        tables.append(table)
    return data[:length], tables


def show(label, data):
    body, tables = record(data)
    print(f"{label}: {len(body)} structured bytes, SHA-256 {hashlib.sha256(body).hexdigest()}")
    harvest = next(table for table in tables if table.startswith(b"HARV"))
    if len(harvest) != 136:
        raise ValueError("Unexpected harvest table size")
    entries = [(hw, instance) for hw, instance, _ in struct.iter_unpack("<HBB", harvest[8:]) if hw]
    print(f"Harvest entries (hardware ID, instance): {entries}")
    return body


runtime = show("Runtime", args.capture.read_bytes())
if args.bios:
    if args.offset < 0:
        parser.error("BIOS offset must be nonnegative")
    stock = show("BIOS", args.bios.read_bytes()[args.offset:])
    for pos, (before, after) in enumerate(zip(stock, runtime)):
        if before != after:
            print(f"{pos:#06x}: {before:#04x} -> {after:#04x}")
    if len(stock) != len(runtime):
        print(f"Record lengths differ: {len(stock)} and {len(runtime)}")
