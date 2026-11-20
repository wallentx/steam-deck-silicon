"""Extract regular files by inode using read-only debugfs. Never restore links or modes."""
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

image = Path(sys.argv[1]).resolve(strict=True)
out = Path(sys.argv[2])
out.mkdir(mode=0o700)
dirs = [(2, Path("."))]
visited = set()
commands = []
sizes = {}
while dirs:
    inode, parent = dirs.pop()
    if inode in visited:
        raise ValueError(f"Repeated directory inode {inode}")
    visited.add(inode)
    listing = subprocess.check_output(["debugfs", "-R", f"ls -p <{inode}>", image],
                                      stderr=subprocess.DEVNULL, text=True)
    for line in listing.splitlines():
        if not line:
            continue
        _, child, mode, uid, gid, name, size, _ = line.split("/")
        if name in (".", "..") or child == "0":
            continue
        if not child.isdecimal() or not re.fullmatch(r'[ -~]+', name) or any(c in name for c in '"\\'):
            raise ValueError(f"Unexpected ext4 name {name!r}")
        path = parent / name
        kind = int(mode, 8)
        if stat.S_ISDIR(kind):
            (out / path).mkdir()
            dirs.append((int(child), path))
        elif stat.S_ISREG(kind):
            sizes[out / path] = int(size)
            commands.append(f'dump <{child}> "{path}"')
os.umask(0o077)
subprocess.run(["debugfs", "-f", "-", image], cwd=out, input="\n".join(commands)+"\n",
               text=True, stdout=subprocess.DEVNULL, check=True)
for file, size in sizes.items():
    if file.stat().st_size != size:
        raise ValueError(f"Incomplete extraction of {file}")
print(f"{out}: {len(commands)} regular files")
