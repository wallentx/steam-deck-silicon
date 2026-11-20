# Runtime harvest record on Jupiter F7A0133

The 10,240-byte AMDGPU debugfs capture has SHA-256 31b54009c2177f38b5fea6b19df54a4b3ec0265a71c0d7a0687c6bc93258eb5c on both the Deck and the workstation. The header gives a logical size of 1,068 bytes. That region has SHA-256 85eff526aab15ddcc74261aa8a6520517d588107a058a83f07afda77b4a94880. Both stock F7A0133 copies at capsule offsets 0x234770 and 0xa34770 match each other. The runtime header and all three populated table checksums pass.

| Offset | Stock BIOS | Runtime | Field |
|---|---|---|---|
| 0x008 | 0x4d37 | 0x4e87 | Whole-binary checksum |
| 0x01e | 0x0131 | 0x01d9 | Harvest table checksum |
| 0x3ac | 00 00 00 00 | a8 00 00 00 | First harvest record, little-endian ID 168, instance 0, reserved 0 |

Only four individual bytes differ within the logical binary. The remaining 31 harvest records are empty. The IP discovery and graphics capability tables match the BIOS byte for byte. The 9,172 bytes past the declared end include 7,772 bytes of 0xff and other values. The header assigns no table to that region. Its origin is undetermined.

AMD defines 168 as SATA_HWID. The runtime harvest entry reports SATA instance 0 as harvested. Neither the source of that setting nor its reversibility follows from the record. SATA does not appear among the 36 named live discovery instances, explaining why their individual harvest attributes missed it. The prior PCI inventory also contains no SATA-class controller. The image signal processor (ID 44) remains in the ordinary IP inventory and has no harvest entry. This capture provides no new evidence of CVIP accessibility. [AMD hardware IDs](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/include/soc15_hw_ip.h#L97) · [Harvest record format](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/include/discovery.h#L355-L369) · [Live IP inventory](ip-discovery.tsv) · [PCI capture](pci.tsv)
