#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob
umask 077
export TZ=UTC

usage() {
    printf 'Usage: %s [EXISTING_OUTPUT_PARENT]\n' "${0##*/}"
    printf 'The collector creates a private directory. With read permission it copies DSDT/SSDT AML for offline analysis.\n'
}

case ${1-} in
    -h|--help) usage; exit 0 ;;
esac
(( $# <= 1 )) || { usage >&2; exit 2; }
pci_devices=(/sys/bus/pci/devices/*)
(( ${#pci_devices[@]} )) || { printf 'No kernel PCI inventory is visible.\n' >&2; exit 1; }
out=$(mktemp -d -- "${1:-.}/deck-cvip-XXXXXXXX")
printf 'Collection directory: %s\n' "$out"

# Fixed sysfs attributes expose kernel inventory. No PCI configuration, BAR
# data, ACPI methods, controller or physical-memory interfaces are opened.
field() {
    local value
    if [[ -r $1 ]] && IFS= read -r value < "$1"; then
        printf '%s' "$value"
    else
        printf '%s' '-'
    fi
}

{
    printf 'collected_utc=%(%FT%TZ)T\n' -1
    printf 'kernel=%s\n' "$(uname -srmo)"
    for key in sys_vendor product_name board_name bios_version bios_date; do
        printf '%s=%s\n' "$key" "$(field "/sys/class/dmi/id/$key")"
    done
} > "$out/host.txt"
model=$(field /sys/class/dmi/id/product_name)
if [[ $model != Jupiter ]]; then
    printf 'This host reports %s. The capture is not identified as a Jupiter LCD Deck.\n' "$model" >&2
fi

mkdir -- "$out"/{pci-resources,aml}
matches=0
unreadable_ids=0
{
    printf 'bdf\tvendor\tdevice\tclass\trevision\tsubvendor\tsubdevice\tdriver\tsysfs_path\n'
    for dev in "${pci_devices[@]}"; do
        bdf=${dev##*/}
        vendor=$(field "$dev/vendor")
        device=$(field "$dev/device")
        [[ $vendor != 0x1022 || $device != 0x149d ]] || (( ++matches ))
        if [[ $vendor == - || $device == - ]]; then
            (( ++unreadable_ids ))
        fi
        path=$(readlink -f -- "$dev") || path=-
        driver=$(readlink -- "$dev/driver") || driver=-
        printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$bdf" "$vendor" "$device" \
            "$(field "$dev/class")" "$(field "$dev/revision")" "$(field "$dev/subsystem_vendor")" \
            "$(field "$dev/subsystem_device")" "${driver##*/}" "$path"
        # resource is the kernel's address/flags listing; resourceN maps BAR memory.
        if [[ -r $dev/resource ]]; then
            cat -- "$dev/resource" > "$out/pci-resources/$bdf.txt"
        fi
    done
} > "$out/pci.tsv"
printf 'enumerated_1022_149d=%s\nunreadable_pci_ids=%s\n' "$matches" "$unreadable_ids" >> "$out/host.txt"
{
    printf 'device\thid\tnamespace_path\tphysical_node\n'
    for dev in /sys/bus/acpi/devices/*; do
        node=$(readlink -- "$dev/physical_node") || node=-
        printf '%s\t%s\t%s\t%s\n' "${dev##*/}" "$(field "$dev/hid")" "$(field "$dev/path")" "$node"
    done
} > "$out/acpi.tsv"

tables=/sys/firmware/acpi/tables
{
    printf 'source\tresult\n'
    for dir in "$tables" "$tables/dynamic"; do
        if [[ ! -r $dir || ! -x $dir ]]; then
            printf '%s\tunavailable\n' "$dir"
            continue
        fi
        tables_found=("$dir"/DSDT "$dir"/SSDT*)
        for table in "${tables_found[@]}"; do
            [[ -f $table ]] || continue
            dest="$out/aml/${dir##*/}-${table##*/}.aml"
            if [[ -r $table ]] && cat -- "$table" > "$dest"; then
                printf '%s\tcopied\n' "$table"
            else
                printf '%s\tunreadable\n' "$table"
            fi
        done
    done
} > "$out/aml-status.tsv"
(
    cd -- "$out"
    files=(host.txt pci.tsv acpi.tsv aml-status.tsv pci-resources/*.txt aml/*.aml)
    sha256sum -- "${files[@]}" > SHA256SUMS
)
printf 'The kernel enumerated %s matching 1022:149d function(s). See %s/aml-status.tsv for table coverage.\n' "$matches" "$out"
