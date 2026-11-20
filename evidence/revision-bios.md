# ML2 BIOS revisions and the LCD Deck

## Firmware scope

The comparison covers the regular and SSC 16 MiB BIOS variants from each of four stock flash packages. Every row below records a SHA-256 of the entire BIOS file. The distinct hashes prevent a package label from being mistaken for identical firmware. Magic Leap assigns the T2 minimum to OS 1.2.1 on MedTech and 1.3.1 on Enterprise devices. The published matrix does not identify a specific chip stepping. [Vendor and SKU evidence](revision-sources.md)

| ML2 OS | demophon_bios.FD | demophon_bios_ssc.FD |
|---|---|---|
| 1.2.0 | `34bed2044655e82c97b6965abd7ad94ce97c14318dd05402f4d6d8d935a93051` | `47b3718d189c27c735279a86b79f2e6aee832bba553f1ad636e8a72a7988acd2` |
| 1.2.1 | `245269b8f98b3e888b70e5fc38e94516612ea00a4a295eec0e522129f2a61b4e` | `5c2a3cac3c1a228b1288e579aff3f8ca8b13154b7a3ea1a9f00e5a3ae924b9fc` |
| 1.3.1 | `17a22fb1e63f21bfd26c64a28bcb373a859b95957ae7efd2ab8d867251bb7351` | `90cb4e2b8f3fc0c95a42eaaab379018eebc8f571b4ff41ec6e7acfdcf7baf7bc` |
| 1.12.1 | `f4b050e9b7f518b084b4184b7818a7e03cdabc975f20357d99a11f66469c5b62` | `5152a164858b02ce65032cd6f06c4c36f5b28b46f01eefc0bfee801a616391c4` |

Each ROM contains level-two PSP directories at 0x100000 and 0x880000. Each directory holds 30 entries. In all 16 directory instances, type 0x30 uses table-relative offset 0xd5200 and length 0xe7850. This maps to ROM offsets 0x1d5200 and 0x955200. The two copies within each release match across both BIOS variants. The static header supplies no evidence of which redundant copy a specific boot selected.

| Artifact (SHA-256) | OS 1.2.0, 1.2.1, 1.3.1 | OS 1.12.1 |
|---|---|---|
| Raw DSDT | `af1f696ad3c822e9a47e5181c5597541029075626981f0baa336444d401305f5` | `82becb75d20daa981e9e4a672288b705c6c35651e4a336229759cf6f04c977ec` |
| PSP directory type 0x30 | `541d20bc4764c410fa1659ee22853ac9cef8a2fa0d4f8f47d07c3671b2219dae` | `208fcb7181fa932ddc39a452f1b13ebbffd0b9d949c88a9d1ae00cffa0881145` |
| SmuV13Dxe.efi | `25b125f21391c69d4a7303094961405235b366c79b3c8ec00e6c6354c8bdc0b9` | `7f7b5ddaf71385055fa9523400b964036b652d0072b7bd3fb53f099e1f151cfe` |

## Device discovery and resources

**CONFIRMED.** ACPICA 20251212 decoded the DSDT from every variant. All eight DSDTs describe the same `\_SB.PCI0.GP18` at PCI device 8, function 2. Its SATA child has downstream address zero. Its CVIP child has downstream address one, a wake descriptor with values 8 and 4, and no local `_HID`, `_CRS` or IRQ descriptor. The AML NameSeg `CVIP` starts at DSDT offset 0x12d0 in all eight copies. The PCI endpoint supplies BAR resources if it enumerates. This static ACPI node does not itself confirm runtime enumeration, BAR addresses or an interrupt assignment. [ML2 driver and enumeration evidence](device-identifiers.md)

**CONFIRMED.** The older and newer DSDT differ at exactly two of 15,897 bytes. The change at 0x3ac3 raises `I2CC.TMP0`'s `loc_shutdown-limit` value from 0x50 to 0x53. Its checksum at 0x9 changes from 0xb7 to 0xb4. Their complete GP18 subtrees are identical even across the later release. The 7-Zip UEFI output path in each regular/SSC extraction is `20BC8AC9/EE4E5898/VOLUME/ACPI/5.raw`. Each raw table passes its length and ACPI checksum.

## CVIP-specific bootloader path

**CONFIRMED.** Each type 0x30 container has a 21-entry index of little-endian 32-bit subtype/offset pairs at +0x100. Two indexed bodies contain the NVMe partition, destination memory and firmware-copy diagnostics. Their complete payloads match byte-for-byte across both directories, both variants and all four releases. The payload begins at subtype-header offset +0x100 and its little-endian length is at header +0x14. The outer container differs in OS 1.12.1, so hashing the entire ABL alone would obscure this reuse. [Existing initialization analysis](../analysis/initialization.md)

| ABL subtype | Entry offset relative to type 0x30 | Payload length | SHA-256 of payload |
|---|---|---:|---|
| 0x05 | 0x1e810 | 73,996 | `c694885400ad8cd3c6c276fc9540302bf774c2aba704c46edc2522d34c658941` |
| 0x14 | 0xde430 | 37,404 | `c0e55b290ea71d1ce1179989c51b2b7db58a364b8cec2765f605478693d776da` |

| First-ROM-copy diagnostic | Absolute ROM offset in subtype 0x05 | Absolute ROM offset in subtype 0x14 |
|---|---:|---:|
| ABL CVIP partition-table lookup | 0x1fcac5 | 0x2b9155 |
| Found CVIP firmware partition | 0x1fee4a | 0x2ba7b2 |
| Partition label and FMR destination address | 0x1fee68 | 0x2ba7d0 |
| CVIP image copy completion | 0x1feeb2 | 0x2ba81a |
| Missing CVIP image partition in NVMe | 0x200864 | 0x2bb9d4 |

**UNKNOWN.** These messages describe an implementation capable of loading CVIP firmware from NVMe partitions into memory. The BIOS files alone do not show which path executed, which CVIP silicon revision booted or the value of a per-unit hardware revision.

## What changed at the compatibility floors

**CONFIRMED.** Between OS 1.2.0 and 1.2.1, two of the 188 matched 7-Zip output files in the regular UEFI volume changed bytes: AndroidBootloader.efi and PlatformSmbiosDxe.efi. Between OS 1.2.1 and 1.3.1, five changed: the AMD PBS setup module, AmdVersionDxe, AndroidBootloader, PlatformSmbiosDxe and SystemFirmwareReportDxe. These counts cover 7-Zip's decoded volume at BIOS file offset 0x580000. Other regions also changed. In the first PSP directory, the table-relative payloads which differ between the first pair have types 0x25 and 0x83, and the second pair additionally differs at types 0x08 and 0x12. Type 0x30 remains identical within this early series. These deltas support no unique attribution of the SKU floor.

**CONFIRMED.** AndroidBootloader.efi in 1.2.1 adds the ASCII Android boot parameter `androidboot.lwear.hardware.revision`, alongside a named `lwear_hwrev` configuration record described as the wearable's hardware revision. The 1.2.0 executable lacks these three strings. OS 1.3.1 retains them. For 1.2.1, the key at RVA 0x39838 is referenced by the parameter table at 0x248f8 alongside its code callback at 0x1737c. The callback requests configuration record 0x10, calls the getter at 0x203dc and formats a nonempty value with `%a=%a` from RVA 0x39738. The configuration table at 0x3de70 contains pointers to the record name at 0x3dc18 and description at 0x3dc28. This is a specific host boot-interface change at the MedTech floor. Its link to a specific T2 serial number or a CVIP stepping is **UNKNOWN**. A compatible headset's Android boot properties would test actual propagation. [Vendor's documented headset compatibility changes](revision-sources.md)

| OS | SHA-256 of extracted AndroidBootloader.efi |
|---|---|
| 1.2.0 | `6dcf8e38e4286adb5740ac0203099586f31db62c78e35c78c791b21a2ff89f7b` |
| 1.2.1 | `fc6b0f6d0aac88ac49b922691184357d9d570336931d84cf318bea8eca030cb6` |
| 1.3.1 | `aeda08f3997b40fda51ef7b6c2a522830f31de7fb166f8f6e76093388715d749` |
| 1.12.1 | `276ead30a9a12791c4b69e1575fb90121adf22d3564388dc2bce2e80e00826bb` |

## Deck comparison

**CONFIRMED.** The owner's Valve Jupiter F7A0133 capture contains 30 readable PCI functions and zero `1022:149d` endpoints. Its GP18 subtree exposes `SATA` and `SATA.PRT0`; its only enumerated downstream function is `05:00.0` (`1022:145a`). The DSDT and twelve SSDTs in the separate raw ACPI capture exclude a named CVIP endpoint. The same stock Deck topology therefore differs from all eight inspected ML2 BIOS variants. [Owner's raw ACPI comparison](../evidence/deck-live/acpi.md) · [Owner's PCI capture](../evidence/deck-live/pci.md)

**CONFIRMED.** The first and second copies of type 0x30 in each of the official F7A0131 and F7A0133 LCD BIOS images contain 21 zlib-compressed subsections. Expanding them and searching for the specific ML2 partition-label, lookup, NVMe, FMRAddress and copy-completion signatures yielded zero matches. The sole case-insensitive CVIP match in those expanded payloads remains the known memory-category string in subtype 0x11. Both LCD BIOS releases and all eight ML2 BIOS images lack a type 0x57 entry in their two inspected level-two directories. An absent 0x57 entry therefore **does not distinguish** these functioning ML2 configurations from the LCD Deck. The stock PCI endpoint and the richer ML2 bootloader code remain stronger discriminators. The evidence identifies no additional accessible Deck hardware interface. [LCD BIOS hashes, module disassembly and public captures](../analysis/steam-deck-applicability.md)

## Offline reproduction

7-Zip 26.06 `7z x -o<private-output> <bios-file>` exposes the DSDT. ACPICA `iasl -d -p <output-stem> <raw-table>` decodes AML without evaluating methods. Compare the decoded GP18 scopes and use `cmp -l` on the raw DSDT files to check their two changed byte positions. The offsets above refer to zero-based byte positions; cmp numbers them starting at one.

For the ABL, read each directory's entry count as a little-endian uint32 at +8. Parse its entries as two little-endian uint32 values (type, length) and a uint64 encoded address, starting at +16. Both type 0x30 entries in the ML2 images use address-mode bits 63:62 equal to 2, with the lower 62 bits relative to the directory. Hash the declared byte length only. Parse the nested index and payload lengths as described above; search the payloads statically for their diagnostic text. The local `bios/{regular,ssc}/parsed.json` files under each historical version retain the directory offsets, subtype-specific diagnostic positions, SHA-256 values and AML names. The analysis preserves the source ROMs unchanged.
