#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob
umask 077

tables=/sys/firmware/acpi/tables
sources=("$tables"/DSDT "$tables"/SSDT* "$tables"/dynamic/SSDT*)
parent=${1:-raw}
mkdir -p -- "$parent"
sudo -v
out=$(mktemp -d -- "$parent/acpi-XXXXXXXX")
for src in "${sources[@]}"; do
    name=${src##*/}
    [[ $src != */dynamic/* ]] || name=dynamic-$name
    # The deck account owns the output. Only the sysfs read needs root.
    # shellcheck disable=SC2024
    sudo cat -- "$src" > "$out/$name.aml"
    [[ -s $out/$name.aml ]]
done
(cd -- "$out" && sha256sum -- *.aml > SHA256SUMS)
printf 'Collected %d tables in %s\n' "${#sources[@]}" "$out"
