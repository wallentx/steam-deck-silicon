#!/usr/bin/env python3
"""Read the five hash-identified ISP artifacts from an extracted ML2 build 9601."""

import argparse
import csv
import hashlib
import struct
import zlib
from pathlib import Path


KERNEL = "boot/vmlinux"
MODULE = "vendor/lib/modules/5.4.19-android-x86_64/kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.ko"
WRAPPED = "vendor/lib/firmware/amdgpu/mero_isp.bin"
RAM = "vendor/lib/firmware/isp/isp_firmware_nawb_isp3.ram"
PROPERTIES = "system/system/build.prop"


def read_inputs(root):
    index = Path(__file__).resolve().parents[1] / "evidence" / "host-index.tsv"
    with index.open(encoding="utf-8") as source:
        rows = {row["path"]: row for row in csv.DictReader(source, delimiter="\t")}
    inputs = {}
    for name in (KERNEL, MODULE, WRAPPED, RAM, PROPERTIES):
        path = root / name
        expected = rows[name]
        if not path.is_file() or path.stat().st_size != int(expected["bytes"]):
            raise ValueError(f"{name}: missing or wrong file size for build 9601")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected["sha256"]:
            raise ValueError(f"{name}: SHA-256 differs from the build 9601 inventory")
        inputs[name] = data
    return inputs


def inspect_camera(kernel, props):
    # Offsets below are relative to VA 0xffffffff81000000 in this ELF's first
    # executable PT_LOAD, which begins at file offset 0x200000.
    text = memoryview(kernel)[0x200000:]
    key = "persist.hardware.camera.enable_cvip"
    for line_number, line in enumerate(props.decode().splitlines(), 1):
        if line.startswith(key + "="):
            print(f"system/build.prop line {line_number}: {line}")

    gate = 0xa8019f
    if bytes(text[gate:gate + 6]) != bytes.fromhex("83 78 08 01 0f 85"):
        raise ValueError("unexpected stream setup comparison")
    skip = gate + 10 + struct.unpack_from("<i", text, gate + 6)[0]
    print(f"config+8 != 1 branches to kernel text+0x{skip:x}")
    for site in (0xa801b4, 0xa80276, 0xa802e1, skip + 6):
        if text[site] != 0xe8:
            raise ValueError(f"expected a direct call at text+0x{site:x}")
        target = site + 5 + struct.unpack_from("<i", text, site + 1)[0]
        print(f"  text+0x{site:x} calls text+0x{target:x}")

    # reset_camera_info stores the sentinel at +0x8664. The resolver supplies
    # immediates for IDs 0/1/2. Its ID-3 edge returns the existing sentinel.
    reset_ring = struct.unpack_from("<I", text, 0xa7719b + 7)[0]
    assigned = []
    for site in (0xa7c5d2, 0xa7c584, 0xa7c5df):
        assigned.append(struct.unpack_from("<I", text, site + 2)[0])
    selector = 0xa7c597
    if bytes(text[selector:selector + 5]) != bytes.fromhex("41 83 f8 03 74"):
        raise ValueError("unexpected memory-camera branch")
    exit_at = selector + 6 + struct.unpack_from("<b", text, selector + 5)[0]
    if bytes(text[exit_at:exit_at + 2]) != bytes.fromhex("89 d8"):
        raise ValueError("memory camera does not branch to the expected return")
    default_ring = struct.unpack_from("<I", text, 0xa7c56f + 1)[0]
    if default_ring != reset_ring:
        raise ValueError("reset and resolver disagree about the unassigned ring")
    compare = text[0xa874b3:0xa874b3 + 5]
    if bytes(compare[:2]) != b"\x83\xfe" or bytes(compare[3:]) != b"\x0f\x82":
        raise ValueError("unexpected unsigned ring bound in command insertion")
    ring_limit = compare[2]
    print(f"From reset, camera 0/1/2/3 resolve to {[*assigned, default_ring]}. "
          f"Command insertion requires ring < {ring_limit}.")


def inspect_firmware(image, ram):
    total, header, major, minor, ip_major, ip_minor, version, size, start, crc = (
        struct.unpack_from("<II4H4I", image)
    )
    wrapper = image[start:]
    if total != len(image) or size != len(wrapper) or zlib.crc32(wrapper) != crc:
        raise ValueError("AMDGPU firmware extent or CRC mismatch")
    if wrapper[0x10:0x14] != b"$PS1":
        raise ValueError("missing PSP header")
    body_size = struct.unpack_from("<I", wrapper, 0x14)[0]
    body = wrapper[0x100:0x100 + body_size]
    body_hash = hashlib.sha256(body).digest()
    if body_hash != wrapper[0xd0:0xf0]:
        raise ValueError("PSP body SHA-256 mismatch")
    encrypted = struct.unpack_from("<I", wrapper, 0x18)[0]
    signed = struct.unpack_from("<I", wrapper, 0x30)[0]
    load_address = struct.unpack_from("<I", wrapper, 0x68)[0]
    prefix = next((i for i, pair in enumerate(zip(body, ram)) if pair[0] != pair[1]),
                  min(len(body), len(ram)))
    print(f"AMDGPU header {major}.{minor}, {header} bytes, IP {ip_major}.{ip_minor}, "
          f"ucode {version:#x}, payload CRC32 {crc:08x}")
    print(f"PSP body {body_size} bytes, SHA-256 {body_hash.hex()}, "
          f"encrypted flag {encrypted}, signed flag {signed}, load field {load_address:#x}, "
          f"trailer {len(wrapper) - 0x100 - body_size} bytes")
    print(f"Raw RAM image {len(ram)} bytes, identical leading body bytes {prefix}")


def inspect_tables(module):
    # readelf -SW and -sW on the pinned module locate .rodata and mero_message_map.
    rodata = 0x58cdf0
    for name, index in (("power down", 0x66), ("power up", 0x67), ("SOCCLK", 0x76),
                        ("ISP ICLK", 0x97), ("ISP XCLK", 0x98)):
        valid, message = struct.unpack_from("<II", module, rodata + 0x5fb00 + 8 * index)
        if not valid:
            raise ValueError(f"unmapped Mero SMU index {index:#x}")
        print(f"Mero {name}: driver index {index:#04x}, firmware message {message:#04x}")
    interface, = struct.unpack_from("<I", module, 0x8d2b10 + 0x3e0 + 4 * (0x1c - 0x15))
    fw_type, = struct.unpack_from("<I", module, rodata + 0x29e18 + 4 * 0x21)
    print(f"Mero driver expects SMU interface {interface}, ISP PSP firmware type {fw_type:#x}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path, help="extraction root containing boot/, vendor/ and system/")
    args = parser.parse_args()
    try:
        files = read_inputs(args.work)
        inspect_camera(files[KERNEL], files[PROPERTIES])
        inspect_firmware(files[WRAPPED], files[RAM])
        inspect_tables(files[MODULE])
    except (OSError, ValueError, struct.error) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
