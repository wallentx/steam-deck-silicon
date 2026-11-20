# LCD Steam Deck capability matrix

The observations apply to Valve Jupiter on BIOS F7A0133 unless a row names another platform.

| Capability | Classification | Evidence and limit |
|---|---|---|
| SATA instance 0 appears in the runtime harvest table | CONFIRMED | AMD maps hardware ID 168 to SATA. The checked runtime record contains that ID and instance. The boot policy, fuse state and physical routing remain unknown. [Record](../evidence/deck-live/runtime-comparison.md) |
| ISP 3.0.0 appears in discovery | CONFIRMED | The BIOS and live driver inventories match. The driver did not register an ISP block. [Inventory](../evidence/deck-live/ip-discovery.tsv) |
| Usable ISP pipeline | UNKNOWN | No video/media endpoint or successful workload was observed. [Boot evidence](deck-disabled-hardware.md) |
| ML2-compatible PCI endpoint on this Deck boot | DISPROVEN | None of 30 readable PCI functions matches 1022:149d. [PCI capture](../evidence/deck-live/pci.md) |
| Physical Mero-equivalent CVIP on the LCD die | HYPOTHESIS | Die analysis and common firmware vocabulary provide leads. The stock Deck AML omits GP18.CVIP. [Physical evidence](../analysis/steam-deck-applicability.md) · [ACPI](../evidence/deck-live/acpi.md) |
| CVIP acceleration for ML on this Deck | UNKNOWN | The ML2 runtime contains vision jobs. No compatible Deck endpoint or running task was demonstrated. [Compute evidence](../analysis/architecture.md) |
| Eight exposed GPU compute units and eight online CPU threads | CONFIRMED | The GPU topology reports 16 SIMDs and two SIMDs per CU. CPU online and present masks both cover 0-7. [Kernel data](../evidence/deck-live/subsystems.txt) |
| Optional UART, I2C, eMMC and audio descriptions report inactive | CONFIRMED | ACPI status and selected methods establish what firmware exposes. Populated chips and external connections remain unknown. [Controller analysis](deck-disabled-hardware.md) |
