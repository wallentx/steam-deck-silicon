#!/usr/bin/env python3
"""Decode a saved Mero build 9601 ISP3 slot or a normalized ring snapshot."""

import argparse
import json
import stat
import struct
from pathlib import Path


SLOT_BYTES = 64
RING_BYTES = {"command": 0x1900, "response": 0x3200}
SET_STREAM_PATH = 0x02010001
FRAME_CTRL = 0x02050001
FRAME_INFO = 0x02050002
SEND_BUFFER = 0x02060001
CMD_DONE = 0x00010001
FRAME_DONE = 0x00010002
NAMES = {
    "command": {SET_STREAM_PATH: "SET_STREAM_PATH", FRAME_CTRL: "SEND_FRAME_CTRL",
                FRAME_INFO: "SEND_FRAME_INFO", SEND_BUFFER: "SEND_BUFFER"},
    "response": {CMD_DONE: "CMD_DONE", FRAME_DONE: "FRAME_DONE",
                 0x00010003: "FRAME_INFO", 0x00010004: "ERROR"},
}
FRAME_INFO_SIZES = {"wrapped": 0x1278, "ram": 0x1230}
GLOBAL_RANGES = (
    (0x01010001, 0x01010002), (0x01020003, 0x01020007),
    (0x01030001, 0x01030004), (0x01040001, 0x01040002),
    (0x01060001, 0x01060004),
)


def read_saved(path, sizes):
    """Accept exactly one of the identified file lengths before reading."""
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size not in sizes:
        raise ValueError(f"{path}: expected a regular file of {sorted(sizes)} bytes")
    with path.open("rb") as stream:
        data = stream.read(info.st_size + 1)
    if len(data) != info.st_size:
        raise ValueError(f"{path}: file length changed during read")
    return data


def pending_offsets(kind, size, read_pointer, write_pointer):
    """Both cursors are byte offsets supplied with the saved snapshot."""
    if size == SLOT_BYTES and read_pointer is None and write_pointer is None:
        return [0]
    if size != RING_BYTES[kind]:
        raise ValueError(f"expected a single slot or a {RING_BYTES[kind]}-byte {kind} ring")
    for pointer in (read_pointer, write_pointer):
        if pointer is None or not 0 <= pointer < size or pointer % SLOT_BYTES:
            raise ValueError("a whole ring needs two normalized, 64-byte-aligned byte cursors")
    distance = (write_pointer - read_pointer) % size
    return [(read_pointer + delta) % size for delta in range(0, distance, SLOT_BYTES)]


def decode_slot(data, kind, ring=None):
    if kind not in RING_BYTES or len(data) != SLOT_BYTES:
        raise ValueError("expected a 64-byte command or response")
    if ring is not None and ring not in range(4):
        raise ValueError("the captured ring index must be 0, 1, 2 or 3")
    if sum(data[:-1]) & 0xff != data[-1]:
        raise ValueError("slot checksum mismatch")
    if not any(data):
        return {"kind": kind, "state": "zero-filled", "checksum": 0}
    sequence, message = struct.unpack_from("<II", data)
    result = {"kind": kind, "sequence": sequence, "id": f"0x{message:08x}",
              "name": NAMES[kind].get(message, "unclassified"), "checksum": data[-1]}
    if kind == "response":
        if message == CMD_DONE:
            original_seq, original_id, status, detail = struct.unpack_from("<IIHH", data, 8)
            result.update(command_sequence=original_seq, command_id=f"0x{original_id:08x}",
                          status=status, error_detail=detail, reply_hex=data[20:56].hex())
        elif message == FRAME_DONE:
            result["metadata_reference"] = f"{struct.unpack_from('<Q', data, 8)[0]:#018x}"
        else:
            result["body_hex"] = data[8:63].hex()
        return result

    tag, = struct.unpack_from("<H", data, 0x38)
    requested = 0 if tag == 0xffff else tag + 1
    result["stream_tag"] = tag
    if message >> 24 == 2:
        result["passes_wrapped_stream_class_tag_check"] = tag < 3
    if requested < 4:
        global_cmd = (message in (FRAME_INFO, SEND_BUFFER)
                      or any(lo <= message <= hi for lo, hi in GLOBAL_RANGES))
        expected_ring = 0 if global_cmd else requested
        result.update(inferred_requested_ring=requested, expected_physical_ring=expected_ring)
        if ring is not None:
            result["matches_capture_ring"] = ring == expected_ring
    if message in (SET_STREAM_PATH, SEND_BUFFER):
        length = 20 if message == SET_STREAM_PATH else 48
        result.update(form="direct", inline_hex=data[8:8 + length].hex())
        if message == SEND_BUFFER:
            result["buffer_type"], = struct.unpack_from("<I", data, 8)
            result["planes"] = []
            for start in (0x0c, 0x18, 0x24):
                address, extent = struct.unpack_from("<QI", data, 8 + start)
                result["planes"].append({"reference": f"{address:#018x}", "bytes": extent})
    elif message in (FRAME_CTRL, FRAME_INFO):
        address, length = struct.unpack_from("<QI", data, 8)
        result.update(form="indirect", payload_reference=f"{address:#018x}",
                      payload_size=length, payload_checksum=data[20])
        if message == FRAME_CTRL:
            result["matches_frame_ctrl_issuer"] = length == 0xa50
        else:
            result["matching_frame_info_sizes"] = [
                key for key, size in FRAME_INFO_SIZES.items() if size == length
            ]
    else:
        result.update(form="unclassified", body_hex=data[8:56].hex())
    return result


def check_payload(record, payload):
    """The caller supplies file bytes independently of the recorded address."""
    if record.get("form") != "indirect":
        raise ValueError("no verified indirect form for this record")
    if len(payload) != record["payload_size"] or sum(payload) & 0xff != record["payload_checksum"]:
        raise ValueError("external payload length or checksum mismatch")
    record["external_payload_verified"] = True
    if record["name"] == "SEND_FRAME_INFO" and len(payload) in FRAME_INFO_SIZES.values():
        # These fields are read by the host diagnostic. Pixel direction and
        # equivalence to the firmware's internal per-build layout are unknown.
        address, = struct.unpack_from("<Q", payload, 0x77c)
        record["r64_host_debug_view"] = {
            "reference": f"{address:#018x}",
            "length_operands": [struct.unpack_from("<I", payload, i)[0]
                                for i in (0x784, 0x790, 0x79c)],
        }


def number(value):
    return int(value, 0)


def check_owned_range(record, base, size):
    """Compare numeric extents only. The range must come from independent evidence."""
    if record.get("name") != "SEND_BUFFER":
        raise ValueError("an owned-range comparison requires a SEND_BUFFER descriptor")
    if base < 0 or size <= 0 or base + size > 1 << 64:
        raise ValueError("invalid 64-bit allocation extent")
    for index, plane in enumerate(record["planes"]):
        address = int(plane["reference"], 16)
        if plane["bytes"] and not (base <= address and address + plane["bytes"] <= base + size):
            raise ValueError(f"nonempty plane {index} is outside the supplied allocation")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=RING_BYTES)
    parser.add_argument("file", type=Path)
    parser.add_argument("--ring", type=number, choices=range(4), help="known physical ring index")
    parser.add_argument("--read-pointer", type=number, help="normalized byte offset in a whole ring")
    parser.add_argument("--write-pointer", type=number, help="normalized byte offset in a whole ring")
    parser.add_argument("--payload", type=Path, help="separately saved indirect body for a single slot")
    parser.add_argument("--owned-range", type=number, nargs=2, metavar=("BASE", "BYTES"),
                        help="compare one SEND_BUFFER's nonempty planes with a known same-domain allocation")
    args = parser.parse_args()
    try:
        data = read_saved(args.file, (SLOT_BYTES, RING_BYTES[args.kind]))
        offsets = pending_offsets(args.kind, len(data), args.read_pointer, args.write_pointer)
        records = []
        for offset in offsets:
            try:
                record = decode_slot(data[offset:offset + SLOT_BYTES], args.kind, args.ring)
            except ValueError as exc:
                raise ValueError(f"byte offset {offset:#x}: {exc}") from exc
            records.append(dict(offset=offset, **record))
        if args.payload:
            if len(records) != 1 or records[0].get("form") != "indirect":
                raise ValueError("--payload requires one indirect record")
            record = records[0]
            known_sizes = (0xa50,) if record["name"] == "SEND_FRAME_CTRL" else FRAME_INFO_SIZES.values()
            if record["payload_size"] not in known_sizes:
                raise ValueError("external body size is outside the verified layouts for this command")
            check_payload(record, read_saved(args.payload, (record["payload_size"],)))
        if args.owned_range:
            if len(records) != 1:
                raise ValueError("--owned-range requires one buffer descriptor")
            check_owned_range(records[0], *args.owned_range)
            records[0]["within_supplied_numeric_range"] = True
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
