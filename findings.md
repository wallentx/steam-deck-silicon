# Evidence and outstanding questions

## Hardware the Deck reports as disabled

The firmware's runtime harvest list identifies SATA instance 0 by AMD hardware ID 168. The static BIOS record omits that entry. No SATA-class controller enumerated on this boot. The combined evidence establishes a reported disabled function. It leaves the mechanism and reversibility unknown. [Runtime comparison](evidence/deck-live/runtime-comparison.md) · [PCI functions](evidence/deck-live/pci.tsv)

The platform firmware also marks optional I2C, UART, embedded storage and audio descriptions absent on this unit. These descriptions document alternate configurations. They cannot establish whether unused pins reach a connector or which optional components were populated. [Controller findings](reports/deck-disabled-hardware.md) · [ACPI status inventory](evidence/deck-live/acpi-status.tsv)

## The ISP and the proposed vision accelerator

The Deck exposes an ISP 3.0.0 entry in AMDGPU’s discovery hierarchy. Its driver registered graphics, video and JPEG blocks and omitted the ISP. Magic Leap’s Mero firmware also describes ISP 3.0.0, while a separate PCI function handles CVIP. The Mero BIOS discovery inventory includes one additional ID, 254, whose identity remains unknown. [Inventory comparison](reports/deck-disabled-hardware.md)

The Mero kernel identifies the CVIP endpoint by a PCI match table. Its probe establishes memory mappings, MSI-X interrupts and mailboxes. On the original Deck the corresponding PCI bridge exists, but the enumerated downstream function has a different ID. Thirteen checked ACPI tables omit the Mero CVIP child. Valve's BIOS includes CVIP diagnostics, and a die-photo analysis proposes a candidate region. Neither observation demonstrates an electrically accessible accelerator. [Kernel attribution](evidence/device-identifiers.md) · [Local ACPI evidence](evidence/deck-live/acpi.md) · [BIOS, public captures and die references](analysis/steam-deck-applicability.md)

## Reference implementation in Magic Leap 2

| Question | Evidence |
|---|---|
| How does the subsystem boot? | Separate AMD-format boot artifacts, an x86 PCI driver and a distinct AArch64 service environment provide evidence for the firmware and host startup sequence. [Initialization](analysis/initialization.md) · [Firmware loading](analysis/firmware-loading.md) |
| How do data and commands travel? | The host uses PL320 mailboxes for short messages, shared memory for buffers and MLNET/NBD for remote storage. [Host interface](analysis/host-interface.md) |
| Which workloads can be identified? | The shipped software contains C5 hand-detection jobs, Q6 vision work, model weights, task creation and start routines. Arbitrary model loading and measured throughput remain unknown. [Compute analysis](analysis/architecture.md) |
| Did the interface change across hardware revisions? | All four inspected OS builds use the same PCI ID and ACPI location. The 1.2.1 update accommodates headset hardware changes and includes calibration changes. The T2 serial group has no established mapping to a CVIP silicon stepping. [Revision comparison](reports/hardware-revisions.md) |

## Evidence boundaries

A confirming result for Deck CVIP would require a hardware-specific observation beyond shared firmware names, such as a verified silicon identification or an enumerated endpoint. Establishing ISP usability would require evidence of an appropriate driver, image input, and successful processing. A working SATA interface would require independent evidence of electrical routing and controller availability. This investigation used offline firmware parsing and read-only inventories. No enablement or throughput test was performed.

[ML2 artifact inventory](evidence/artifacts.md) · [Firmware hashes](evidence/cvip-side.tsv) · [Public source register](evidence/source-references.md)
