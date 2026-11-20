"""Check the registration, PCI table and BIOS addresses for ML2 OS 1.12.1."""
import hashlib
from pathlib import Path
import struct
import sys

work = Path(sys.argv[1])
elf = (work / 'boot/vmlinux').read_bytes()
# These recorded VAs identify the registration and LEA/MOV immediates in this build.
def offset(va):
    phoff, = struct.unpack_from('<Q', elf, 32)
    entsz, count = struct.unpack_from('<HH', elf, 54)
    for i in range(count):
        typ, flags, off, base, phys, filesz, memsz, align = struct.unpack_from('<II6Q', elf, phoff+i*entsz)
        if typ == 1 and base <= va < base+filesz:
            return off+va-base
    raise ValueError(hex(va))

pos = offset(0xffffffff82faeff6)
assert elf[pos:pos+3] == b'\x48\xc7\xc7'
ptr, = struct.unpack_from('<i', elf, pos+3)
driver = offset(ptr % 2**64)
name, table, probe = struct.unpack_from('<QQQ', elf, driver+16)
assert elf[offset(name):offset(name)+5] == b'cvip\0'
vendor, device, subvendor, subdevice, cls, mask, driver_data = struct.unpack_from('<6IQ', elf, offset(table))
assert (vendor, device, subvendor, subdevice, cls, mask) == (0x1022, 0x149d, 0xffffffff, 0xffffffff, 0, 0)
assert elf[offset(table)+32:offset(table)+64] == bytes(32)
print(f"cvip PCI {vendor:04x}:{device:04x}, table file offset {offset(table):#x}, probe {probe:#x}")
bios = (work / 'package/demophon_bios.FD').read_bytes()
directory = 0x100000
assert bios[directory:directory+4] == b'$PL2'
for n in range(struct.unpack_from('<I', bios, directory+8)[0]):
    kind, size, addr = struct.unpack_from('<IIQ', bios, directory+16+16*n)
    if kind == 0x30:
        assert addr >> 62 == 2
        start = directory+(addr & (2**62-1))
        entry = bios[start:start+size]
        for marker in [b'ABL - Get CVIP Partition Table Info', b'Current CVIP Image copy done']:
            print(f"{marker.decode()}: {start+entry.index(marker):#x}")
        print(f"PSP directory type 0x30: offset={start:#x} size={size:#x} sha256={hashlib.sha256(entry).hexdigest()}")
        break
else:
    raise ValueError("Missing expected type 0x30")
