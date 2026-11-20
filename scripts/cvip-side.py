#!/usr/bin/env python3
"""Inventory the CVIP images from ML2 build 9601. Run with PACKAGE_DIR NEW_OUTPUT_DIR > inventory.tsv."""
import argparse
import csv
import hashlib
from pathlib import Path
import re
import stat
import struct
import subprocess
import sys

SPARSE_HASHES = {
    "cvip_ro": "5d0e59e8287a819e64cc5916d840ae7faa50521e816dce215e78ce40a1158731",
    "cvip_rw": "3a440ea0c29f2b55828d7225c6160e16cbcff385a4b43b754a4f3a9ff37faf4b",
    "cvip_props": "241c5d5acff229b547e51d9da90760fa054cc1cac15df590d066edd331eb156f",
}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def unpack_ext(image, destination):
    """Read only regular files from the known image. Never recreate links or device nodes."""
    destination.mkdir(mode=0o700)
    pending = [(2, destination)]
    seen = set()
    while pending:
        inode, folder = pending.pop()
        if inode in seen:
            raise ValueError(f"Repeated directory inode {inode}")
        seen.add(inode)
        listing = subprocess.check_output(
            ["debugfs", "-R", f"ls -p <{inode}>", image], text=True,
            stderr=subprocess.DEVNULL,
        )
        if not listing.strip():
            raise ValueError(f"Unreadable directory inode {inode}")
        for line in listing.splitlines():
            if not line:
                continue
            _, number, mode, _, _, name, size, _ = line.split("/")
            if (number == "0" and not name) or name in (".", ".."):
                continue
            if not re.fullmatch(r"[a-zA-Z0-9_.+-]+", name):
                raise ValueError(f"Unexpected name {name!r}")
            target = folder / name
            kind = stat.S_IFMT(int(mode, 8))
            if kind == stat.S_IFDIR:
                target.mkdir(mode=0o700)
                pending.append((int(number), target))
            elif kind == stat.S_IFREG:
                # Only the numeric inode enters the debugfs command language.
                with target.open("xb") as out:
                    subprocess.run(["debugfs", "-R", f"cat <{int(number)}>", image],
                                   stdout=out, stderr=subprocess.DEVNULL, check=True)
                target.chmod(0o600)
                if target.stat().st_size != int(size):
                    raise ValueError(f"Short read at {target}")
            else:
                raise ValueError(f"Unexpected special inode {number}")


def identify(path, relative):
    with path.open("rb") as stream:
        head = stream.read(256)
    if head[16:20] == b"$PS1":
        return ("AMD firmware wrapper", "inner ISA unverified", f"type={head[124]:#x}; enc={head[24]}; sig={head[48]}", "compare header and flash partition")
    if head[:4] == bytes.fromhex("3aff26ed"):
        return ("Android sparse v1", "container", "sparse magic at 0", "inspect decoded image")
    if head[:4] == b"\x7fELF":
        machine = struct.unpack_from("<H", head, 18)[0]
        return ("ELF64 LE" if head[4:6] == b"\x02\x01" else "ELF", {183: "AArch64", 62: "x86-64"}.get(machine, str(machine)), f"entry={struct.unpack_from('<Q', head, 24)[0]:#x}", "inspect ELF symbols, dependencies and call sites")
    if path.suffix == ".bin" and "/bin/" in relative and re.search(r"_[cq][56]\.bin$", relative):
        core = "Xtensa C5" if "_c5.bin" in relative else "Xtensa Q6"
        if "_profile_" in path.name:
            words = struct.unpack(f"<{len(head) // 4}I", head)
            return ("DSP profiling address table", f"{core} data",
                    f"{len(words)} little-endian words; first={words[0]:#x}",
                    "compare address words with corresponding program")
        return ("flat DSP program", core, f"first LE word={int.from_bytes(head[:4], 'little'):#x}", "compare program with job list and debug helper")
    if path.suffix == ".jobs":
        return ("DSP job map", "C5/Q6 symbol metadata", "typed C++ symbols with hex values", "demangle with c++filt")
    if "/model_params/" in relative:
        return ("model resource ZIP" if head.startswith(b"PK") else "model parameter bytes", "data", "Kraken model_params", "match literals in per-package library")
    if path.suffix == ".ihex":
        return ("Intel HEX variant", "unknown", "Orion directory; 24-bit address records", "identify peripheral separately")
    if path.suffix == ".img":
        role = "raw properties" if "props" in relative else "ext4"
        return (role, "data", path.stem, "compare filesystem metadata and marker")
    if path.name == "demophon_gpt.bin":
        return ("partition metadata", "data", "UTF-16LE partition labels", "compare flash target names")
    return ("script or configuration" if head.startswith(b"#!") or path.suffix in (".yaml", ".service", ".py", ".sh") else "text or resource",
            "data", path.suffix or path.name, "inspect references and consuming service")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    for name, digest in SPARSE_HASHES.items():
        if sha(args.package / f"{name}.img.hbin") != digest:
            parser.error(f"{name} differs from build 9601")
    args.output.mkdir(mode=0o700)
    inputs = [("package/" + p.relative_to(args.package).as_posix(), p)
              for p in sorted(args.package.glob("*.hbin"))]
    for name in ("flashall_amd.sh", "demophon_gpt.bin", "Linux/bootdr.py",
                 "Linux/cvip/dsp/xt_utils.sh", "Linux/cvip/dsp/dsp_addr2line.sh"):
        inputs.append(("package/" + name, args.package / name))
    for name in SPARSE_HASHES:
        raw = args.output / (name + ".img")
        subprocess.run(["simg2img", args.package / (raw.name + ".hbin"), raw], check=True)
        inputs.append(("decoded/" + raw.name, raw))
        if name in ("cvip_ro", "cvip_rw"):
            tree = args.output / name
            unpack_ext(raw, tree)
            inputs.extend((p.relative_to(args.output).as_posix(), p)
                          for p in sorted(tree.rglob("*")) if p.is_file())
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(("path", "bytes", "sha256", "type", "architecture", "evidence", "confidence", "next inspection"))
    for rel, path in inputs:
        kind, architecture, evidence, next_step = identify(path, rel)
        confidence = "STRONG EVIDENCE" if kind == "flat DSP program" else "CONFIRMED"
        writer.writerow((rel, path.stat().st_size, sha(path), kind, architecture,
                         evidence, confidence, next_step))


if __name__ == "__main__":
    main()
