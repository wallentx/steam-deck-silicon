# Inside the original Steam Deck: which hardware is switched off?

The original LCD Steam Deck reports a disabled **SATA storage controller**. Its graphics driver also lists an **image signal processor** that SteamOS leaves unused. The more intriguing possibility is a computer-vision accelerator like the one in the Magic Leap 2 headset. Valve’s BIOS contains code that knows about that accelerator, but Linux finds no device for its driver to claim. Whether the circuitry exists on the Deck die remains an open question.

[ISP3 driver feasibility](reports/isp3-driver-feasibility.md) · [Follow-up discoveries](reports/followup-summary.md) · [Original short report](reports/summary.md) · [Detailed findings](findings.md) · [Capability matrix](reports/capability-matrix.md)

## What did this Deck report?

| Part | Evidence on the LCD Deck |
|---|---|
| SATA controller | The live AMD discovery table lists SATA instance 0 as *harvested*, AMD’s term for a hardware block reported as disabled. The stock BIOS copy has an empty harvest table. Linux sees an NVMe controller and no SATA-class controller. The reason for the disabled state remains unknown. [Runtime byte comparison](evidence/deck-live/runtime-comparison.md) |
| Image signal processor (ISP) | The stock and live inventories both list ISP 3.0.0. The running graphics driver registered ten functional blocks and omitted the ISP. The installed module contains drivers for ISP 4.1.0 and 4.1.1. Whether the Deck’s ISP can process an image remains untested. [Driver and hardware evidence](reports/deck-disabled-hardware.md) |
| Computer vision and image processing (CVIP) | Four Magic Leap 2 OS builds use AMD PCI ID `1022:149d`. On the Deck, all 30 PCI functions were readable. None matched. The Deck’s ACPI tables describe the corresponding bridge and omit the CVIP child present on Magic Leap. [PCI capture](evidence/deck-live/pci.md) · [ACPI capture](evidence/deck-live/acpi.md) |
| CPU and Radeon compute | Linux reports all eight logical CPUs online. The GPU exposes eight compute units. This investigation found no evidence of additional CPU cores or GPU compute units waiting to be enabled. [Kernel inventory](evidence/deck-live/subsystems.txt) |

### Why the runtime table matters

The running driver exports a cached discovery record. Its first 1,068 bytes contain the structured data. All 36 hardware instances match the stock BIOS inventory. A separate list in the same record identifies harvested components. In that list, the running Deck adds one SATA entry. Only four bytes in the structured record change, including the updated checksums. Looking at the 36 enumerated blocks alone misses that result. [Exact offsets and hashes](evidence/deck-live/runtime-comparison.md)

### Why Magic Leap is a useful comparison

Magic Leap’s AMD Mero system gives us a positive example of the accelerator people have proposed for the Deck. Its firmware contains ARM services, DSP programs, model weights and a driver that uses PCI, shared memory, interrupts and hardware mailboxes. One hand-detection job can be traced from an ARM library to a C5 DSP job map. The Deck’s firmware retains CVIP power-management references, but its live inventories lack the endpoint used in every ML2 release examined. No CVIP workload has been demonstrated on this Deck. [Runtime architecture](analysis/architecture.md) · [Four-release comparison](reports/hardware-revisions.md) · [Deck BIOS and die analysis](analysis/steam-deck-applicability.md)

## Scope and reproduction

The live subject was one Valve Jupiter LCD Deck running BIOS F7A0133. The comparison also covers another official LCD BIOS, seven public LCD PCI captures, and Magic Leap 2 builds 1.2.0, 1.2.1, 1.3.1 and 1.12.1. These results do not establish the physical layout of the OLED Deck or the cause of any fuse, power or board-level difference.

On an LCD Deck, collect kernel-maintained PCI and ACPI information as the login user:

```bash
mkdir -p raw
bash scripts/steam-deck-readonly.sh raw
```

The [reproduction guide](reports/reproduction.md) covers the discovery blob, privileged ACPI reads and offline firmware analysis. The repository contains observations, hashes, source references and analysis scripts. Large vendor images, full AML tables, disassemblies and working files stay local.

The related [Steam Machine silicon investigation](https://github.com/wallentx/steam-machine-silicon) applies the same questions to Valve Fremont.
