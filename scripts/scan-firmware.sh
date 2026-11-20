#!/usr/bin/env bash
# Emit a tab-separated SHA-256 and keyword index for extracted regular files.
# Usage: scan-firmware.sh WORK [tree ...] > evidence/host-index.tsv
set -euo pipefail
export LC_ALL=C
cd -- "${1:?usage: scan-firmware.sh WORK [tree ...]}"
shift
if (( $# == 0 )); then set -- package boot vendor system userdata cache bios host-ramdisk; fi
for tree do [[ -d $tree ]] || { printf 'Missing tree %s\n' "$tree" >&2; exit 1; }; done
tmp=$(mktemp -d)
trap 'rm -r -- "$tmp"' EXIT
specific='cvip|cvpe|cvcore|mero[_-](ipc|xpc|notifier)|shregion|pl320|mlnet|xtensa|vision[_ -]?[qc][56]|kraken|demophon'
general='mero|vangogh|vision|image processing|(^|[^a-z])(isp|ml|npu|vpu|dsp|smu|psp|ipc)([^a-z]|$)|firmware|coprocessor|remoteproc|rpmsg|mailbox|amdgpu'
scan() {
    local status=0
    rg --no-ignore --hidden -ail0 -e "$1" -- "${@:2}" || status=$?
    (( status <= 1 ))
}
scan "$specific" "$@" > "$tmp/specific"
scan "$general" "$@" > "$tmp/general"
python3 - "$tmp" "$specific" "$general" "$@" <<'PY'
import hashlib, os, pathlib, re, struct, sys
tmp = pathlib.Path(sys.argv[1])
roots = [pathlib.Path(p) for p in sys.argv[4:]]
hits = {k: set((tmp/k).read_bytes().split(b'\0')) for k in ("specific","general")}
patterns = [re.compile(p,re.I) for p in sys.argv[2:4]]
print("path\tbytes\tsha256\tformat\tmachine\tkeyword_tier")
for root in roots:
    for p in sorted(root.rglob("*")):
        if p.is_symlink() or not p.is_file():
            continue
        with p.open("rb") as f:
            h = f.read(64)
            f.seek(0)
            digest = hashlib.file_digest(f,"sha256").hexdigest()
        kind,arch = "other","-"
        if h.startswith(b'\x7fELF'):
            mach = struct.unpack_from("<H" if h[5]==1 else ">H",h,18)[0]
            kind = "ELF64" if h[4]==2 else "ELF32"
            arch = {3:"i386",62:"x86-64",40:"ARM",183:"AArch64",94:"Xtensa"}.get(mach,str(mach))
        else:
            for magic,fmt in ((b'MZ','DOS/PE'),(b'PK\x03\x04','ZIP'),(b'ANDROID!','Android boot'),(b'AVB0','AVB'),(b'\x3a\xff\x26\xed','Android sparse'),(b'\x1f\x8b','gzip')):
                if h.startswith(magic):
                    kind=fmt
                    break
        tier=next((k for k,pat in zip(hits,patterns) if os.fsencode(p) in hits[k] or pat.search(str(p))),"none")
        print(p,p.stat().st_size,digest,kind,arch,tier,sep="\t")
PY
