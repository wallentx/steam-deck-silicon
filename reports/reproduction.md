# Reproducing the investigation

## Original LCD Steam Deck

From the repository root, create a private output directory. The first collector reads kernel-maintained inventories. The second collector requests sudo for the DSDT/SSDT reads. The following debugfs read copies the driver’s cached discovery blob. This path applies to the tested Deck, where AMDGPU owns card0.

```bash
umask 077
mkdir -p raw
bash scripts/steam-deck-readonly.sh raw
bash scripts/collect-acpi.sh raw
sudo cat /sys/kernel/debug/dri/0/amdgpu_discovery > raw/runtime-discovery.bin
python3 scripts/inspect-discovery.py raw/runtime-discovery.bin
```

To reproduce the byte comparison, supply the F7A0133 signed capsule from the [Valve package identified here](../analysis/steam-deck-applicability.md). The parser verifies the declared record and table checksums before reporting harvest entries and changed offsets. The [published comparison](../evidence/deck-live/runtime-comparison.md) records the expected hashes.

```bash
python3 scripts/inspect-discovery.py raw/runtime-discovery.bin --bios raw/F7A0133_sign.fd
```

## Magic Leap 2 firmware on Arch Linux

Run these examples from the repository root for a fresh reproduction. Store the verified input archive under `work/`. These examples use a new directory so the original outputs can be compared. Allow at least 30 GiB of free space on a filesystem that supports sparse files. The initial archive extraction alone checks for 7 GiB. The analysis used Bash, Python 3.11+, GNU binutils, libarchive, ripgrep, e2fsprogs, Android sparse tools, unpack_bootimg, AVB tooling, 7-Zip and ACPICA. The symbol reconstruction used vmlinux-to-elf 1.4.0. The CVIP filesystem verification additionally used veritysetup.

1. Verify the catalog digest and extract the archive. The tool rejects links and special files and requires a new destination.

   ```bash
   mkdir -p work
   repro=$(mktemp -d work/repro-XXXXXXXX)
   image=work/flash_demophon_aosp-user_10_B3E.251015.01_9601_release-keys.tar.gz
   scripts/inventory.sh "$image" "$repro/package"
   ```

2. Decode the host partitions and boot image. The ext4 reader uses read-only debugfs and extracts regular files by inode. These commands require no mounts or root privileges.

   ```bash
   for part in system vendor userdata cache; do
       simg2img "$repro/package/$part.img" "$repro/$part.raw"
       python scripts/extract-ext4.py "$repro/$part.raw" "$repro/$part"
   done
   unpack_bootimg --boot_img "$repro/package/boot.img" --out "$repro/boot"
   /usr/src/linux/scripts/extract-vmlinux "$repro/boot/kernel" > "$repro/boot/vmlinux"
   python scripts/extract-host-ramdisk.py "$repro/boot/ramdisk" "$repro/host-ramdisk"
   uvx --from vmlinux-to-elf==1.4.0 vmlinux-to-elf "$repro/boot/vmlinux" "$repro/boot/vmlinux.symbols"
   nm -n "$repro/boot/vmlinux.symbols" > "$repro/boot/kallsyms.txt"
   ```

3. Inspect the platform firmware and reproduce the identifier checks. The 7-Zip warning about bytes after its selected UEFI volume is expected. Other BIOS structures occupy the rest of the image.

   ```bash
   7z x "$repro/package/demophon_bios.FD" "-o$repro/bios"
   iasl -p "$repro/demophon" -d "$repro/bios/20BC8AC9/EE4E5898/VOLUME/ACPI/5.raw"
   python scripts/check-host-identifiers.py "$repro"
   avbtool info_image --image "$repro/package/vbmeta.img"
   ```

4. Rebuild the host and CVIP inventories. The scan includes regular files, ELF headers, bytes and filenames. The specific-keyword tier is a lead for attribution, and the candidate table retains unresolved matches. The CVIP script verifies this build's sparse images and inventories the ARM/DSP filesystem. [DSP-specific verification](../evidence/firmware.md)

   ```bash
   scripts/scan-firmware.sh "$repro" > "$repro/host-index.tsv"
   python scripts/classify-host.py "$repro" "$repro/host-index.tsv" > "$repro/host-candidates.tsv"
   python scripts/cvip-side.py "$repro/package" "$repro/cvip-side" > "$repro/cvip-side.tsv"
   cmp evidence/cvip-side.tsv "$repro/cvip-side.tsv"
   ```

5. On an original LCD Deck, run the read-only collector as the current user. It creates a private output directory under the specified parent. Firmware tables that require additional read permissions can be absent from an unprivileged collection. Its numeric PCI inventory remains useful on its own.

   ```bash
   bash scripts/steam-deck-readonly.sh "$HOME"
   ```

The public specification, consolidated kernel notices, AMD headers, release notes, Hub metadata archive, two LCD BIOS images, seven PCI captures and two ACPI captures used here were archived locally during analysis under `work/sources/`. The [reference digests](../evidence/reference-hashes.txt) identify those copies. Public source URLs and revision information are in the [source evidence](../evidence/source-references.md) and [Deck report](../analysis/steam-deck-applicability.md).

The [four-build hardware comparison](hardware-revisions.md) follows both documented T2 compatibility boundaries, compares BIOS, kernel and vision firmware, and tests the recovered identifiers against a live LCD Deck.
