"""Follow cvip_driver_init in recovered x86 ELF, then decode the original PCI ID table."""
import csv
import re
import struct
import subprocess
import sys
from pathlib import Path

out = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
out.writerow(["build", "driver_init_va", "driver_file_offset", "table_file_offset",
              "probe_va", "vendor:device", "subvendor:subdevice", "class:mask"])
for arg in sys.argv[1:]:
    root = Path(arg)
    elf = (root / "boot/vmlinux").read_bytes()
    named = root / "boot/vmlinux.symbols"
    phoff, = struct.unpack_from("<Q", elf, 32)
    entsize, count = struct.unpack_from("<HH", elf, 54)
    segments = [struct.unpack_from("<II6Q", elf, phoff+i*entsize) for i in range(count)]

    def offset(va):
        for typ, flags, off, base, phys, filesz, memsz, align in segments:
            if typ == 1 and base <= va < base+filesz:
                return off+va-base
        raise ValueError(f"No segment for {va:#x}")

    asm = subprocess.check_output(["objdump", "-d", "--disassemble=cvip_driver_init", named], text=True)
    assert "<__pci_register_driver>" in asm
    start = re.search(r"^([0-9a-f]+) <cvip_driver_init>:", asm, re.M)[1]
    for va in re.findall(r"mov\s+\$(0xffffffff[0-9a-f]+),%rdi", asm):
        record = offset(int(va,16))
        name, table, probe = struct.unpack_from("<QQQ", elf, record+16)
        try:
            nameoff = offset(name)
        except ValueError:
            continue
        if elf[nameoff:nameoff+5] == b"cvip\0":
            break
    else:
        raise ValueError(f"No cvip driver record for {arg}")
    idx = offset(table)
    for i in range(64):
        vendor,dev,sv,sd,cls,mask,data = struct.unpack_from("<6IQ",elf,idx+32*i)
        if not any((vendor,dev,sv,sd,cls,mask,data)):
            break
        out.writerow([root.name if root.name!="work" else "1.12.1",start,hex(record),hex(idx+32*i),
                      hex(probe),f"{vendor:04x}:{dev:04x}",f"{sv:x}:{sd:x}",f"{cls:x}:{mask:x}"])
    else:
        raise ValueError("Unterminated PCI ID table")
