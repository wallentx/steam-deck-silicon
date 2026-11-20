"""Extract only regular files from the known gzip/newc host ramdisk into a new tree."""
import gzip
from pathlib import Path, PurePosixPath
import stat
import sys

src, dest = map(Path, sys.argv[1:])
dest.mkdir(mode=0o700)
data = gzip.decompress(src.read_bytes())
off = 0
while True:
    if data[off:off+6] != b"070701":
        raise ValueError(f"Unexpected newc header at {off:#x}")
    fields = [int(data[pos:pos+8], 16) for pos in range(off+6, off+110, 8)]
    mode, size, namesize = fields[1], fields[6], fields[11]
    start = off+110
    if namesize < 1 or data[start+namesize-1:start+namesize] != b"\0":
        raise ValueError("Invalid filename")
    name = PurePosixPath(data[start:start+namesize-1].decode())
    if name.is_absolute() or ".." in name.parts:
        raise ValueError(f"Unsafe path {name}")
    body = (start + namesize + 3) & ~3
    if name.as_posix() == "TRAILER!!!":
        break
    if body+size > len(data):
        raise ValueError("Truncated ramdisk")
    if stat.S_ISREG(mode):
        out = dest/name
        out.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with out.open("xb") as f:
            f.write(data[body:body+size])
    off = (body+size+3) & ~3
