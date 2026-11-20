# Device discovery

| Confidence | Platform and interface | Identifier | Evidence |
|---|---|---|---|
| CONFIRMED | ML2 Android x86 PCI driver | AMD 1022:149d | The registered driver points to a single nonzero PCI ID entry, followed by the zero terminator. Both subsystem IDs are wildcards. The class and mask are zero. |
| CONFIRMED | ML2 platform BIOS DSDT | `\\_SB.PCI0.GP18.CVIP` | The GP18 bridge has address 0x00080002 (device 8, function 2). Its CVIP child has address 1 (downstream device 0, function 1). Its SATA sibling has address zero. The CVIP node supplies a wake package. The kernel assigns secondary bus numbers at enumeration. |
| CONFIRMED | ML2 temperature monitoring | AMDI0068 | The module's ACPI alias resolves to mero_cvip_thermal. Its dependency is mero_thermal_zone. The functional endpoint uses the PCI matcher above. |
| CONFIRMED | Older ML2 downstream CVIP-side platform source | amd,cvip-plt | The platform driver's OF match table binds to this compatible. Its PCI filters describe the topology that CVIP sees on its side. The current build's protected DTB prevents a direct node comparison. [Public source](source-references.md) |
| CONFIRMED | Original Deck captures | GP18, downstream function inventory | Two LCD AML captures retain GP18 and SATA. The available reads omit the CVIP child and the matching PCI endpoint. [Deck evidence and sampling limits](../analysis/steam-deck-applicability.md) |

## Binary attribution

The host kernel has two functions named `cvip_probe`. The PCI registration fixes which one binds this device. In the uncompressed x86 ELF, the init function at VA `ffffffff82faefe4` calls `ipc_dev_pre_init`. At `ffffffff82faeff6` it passes the driver at `ffffffff82a95340` to `__pci_register_driver`. At ordinary file offset `0x1c95340`, the pointers at +0x10, +0x18 and +0x20 resolve to the name “cvip”, its ID table, and the probe at `ffffffff816d71d0`. The other function at `ffffffff81b5d770` falls outside this registration.

The ID table starts at file offset `0x16b23a0` in the original decompressed ELF. Its first four little-endian words are 0x1022, 0x149d, 0xffffffff and 0xffffffff. The original ELF program headers independently supply the VA-to-file mapping. The recovered kallsyms base agrees with the executable PT_LOAD at `ffffffff81000000`. [Offline verifier](../scripts/check-host-identifiers.py)

The DSDT is section `20BC8AC9/EE4E5898/VOLUME/ACPI/5.raw` of the UEFI volume beginning at file offset 0x580000 in demophon_bios.FD. Its AML Device opcode starts at 0x12cd, the CVIP NameSeg starts at 0x12d0, and the byte after the _ADR name is AML One. ACPICA 20251212 resolved the enclosing scopes and wake package. [File hashes](host-index.tsv)
