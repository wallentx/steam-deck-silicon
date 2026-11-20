#!/usr/bin/env bash
# Verify this exact ML Hub release, then unpack regular files into a new directory.
set -euo pipefail
archive=${1:?usage: inventory.sh ARCHIVE NEW_DIRECTORY}
dest=${2:?usage: inventory.sh ARCHIVE NEW_DIRECTORY}
sha=9747b3652e20746596b64b0b244bd23a047ba47d4eb3d392271cac08a615f28c
umask 077
printf '%s  %s\n' "$sha" "$archive" | sha256sum --check --status
mkdir -- "$dest"
python3 - "$archive" "$dest" <<'PY'
import pathlib, shutil, sys, tarfile
archive, dest = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
if shutil.disk_usage(dest).free < 7 * 1024**3:
    sys.exit("Extraction requires 7 GiB free")
root = 'demophon_aosp-user_10_B3E.251015.01_9601_release-keys'
with tarfile.open(archive, 'r|gz') as src:
    for m in src:
        p = pathlib.PurePosixPath(m.name)
        if not p.parts or p.parts[0] != root or '..' in p.parts:
            sys.exit(f"Unexpected archive path {p!s}")
        out = dest.joinpath(*p.parts[1:])
        if m.isdir():
            out.mkdir(parents=True, exist_ok=True)
        elif m.isfile():
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open('xb') as f:
                shutil.copyfileobj(src.extractfile(m), f, 1024**2)
        else:
            sys.exit(f"Unsupported archive member {p!s}")
PY
