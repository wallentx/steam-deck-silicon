# CVIP discovery on the LCD Steam Deck

The read-only collector ran on Valve Jupiter with BIOS F7A0133 and kernel 7.2.7-valve2-2-neptune-72-g31504582a073 at 2026-11-20 04:32:43 UTC. All 30 PCI functions had readable vendor and device IDs. None matched AMD 1022:149d, the Magic Leap 2 CVIP driver's PCI ID. [Host metadata](host.txt) · [PCI inventory](pci.tsv)

| Observation | This Deck |
|---|---|
| Host bridge | 0000:00:08.2 enumerated as AMD 1022:1648. |
| Downstream endpoint | Only 0000:05:00.0 enumerated below this bridge. It reported 1022:145a and had no bound driver. |
| ACPI namespace visible through sysfs | GP18, GP18.SATA and GP18.SATA.PRT0 appeared. No GP18.CVIP child appeared. |
| Raw ACPI tables | The deck account lacked permission to read the DSDT and 12 SSDTs. |

The normal PCI driver match is unavailable on this boot. The capture leaves the physical presence of the accelerator and the reason for non-enumeration unresolved. The SHA-256 manifest covers the raw collector outputs. [ACPI inventory](acpi.tsv) · [Subsequent raw-table analysis](acpi.md) · [Capture hashes](collector-hashes.txt)
