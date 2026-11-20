# LCD Deck follow-up

**ISP 3.0 is the best software lead.** The Deck and Magic Leap 2 have byte-identical ISP entries. Mero shipped a matching driver and firmware. The Deck’s SteamOS kernel skips ISP3 registration. No Deck frame processing has been demonstrated. The Deck was off, so this follow-up used its saved evidence. [Driver comparison](../analysis/followup-isp.md)

**SATA has the clearest reporting mechanism.** Two Valve bootloaders contain code that turns one input bit into a SATA harvest entry. Its SATA-only output reproduces all four changed bytes and the SHA-256 of the saved 1,068-byte record. The source of the bit remains **UNKNOWN**. [Firmware and byte comparison](../analysis/followup-discovery.md)

## What the two Valve systems establish

| Subject | Strongest observation | Remaining physical or functional question |
|---|---|---|
| Deck and Mero ISP | Mero has an internal memory-input path. Both Android camera configurations advertise zero input streams. [ISP evidence](../analysis/followup-isp.md) | Can Jupiter process a sensorless frame? |
| Deck SATA | Saved harvest entry 168, instance 0. No SATA-class PCI function. [Discovery evidence](../analysis/followup-discovery.md) | Fuse, policy or earlier initialization? Are lanes routed? |
| Mero ID 254 and CVIP | 254 is a versioned record with two bases and no name in the shipping driver. Four ML2 releases describe a separate CVIP PCI function, `1022:149d`. The Deck capture has 0 of 30 matches. Both Valve BIOS feature defaults clear CVIP DSP DPM. [ID 254](../analysis/followup-discovery.md) · [CVIP policy](../analysis/followup-cvip-boot.md) | Identity of 254 and physical CVIP presence on Jupiter are separately **UNKNOWN**. |
| Fremont IPU, iGPU and ACP | Fremont and an XDNA-equipped Framework have identical IPU declarations. Fremont has empty IPU/ACP functions and a graphics placeholder. [Companion investigation](https://github.com/wallentx/steam-machine-silicon) | Exact die, iGPU fuse and ACP implementation. |
| Fremont Navi 33 | Each engine reports CU masks `ff/3f`. Two WGPs are inactive. AMD sells 28-CU mobile parts. [Companion investigation](https://github.com/wallentx/steam-machine-silicon) · [AMD specifications](https://www.amd.com/content/dam/amd/en/documents/partner-hub/radeon/amd-radeon-rx-7000-series-laptops-quick-reference.pdf) | Whether those positions recur or contain working silicon. |

The ML2 C5 detector consumes world-camera frames. ARM publishes timestamped hand records, and Android x86 reads that result type. The buffer and completion for a single frame remain untraced. [Seven-stage workload trace](../analysis/followup-hand-detection.md)

## Ranked next experiments

| Rank and action | Expected information gain | Feasibility and prerequisites | Risk / read-only |
|---|---|---|---|
| 1. Compare the ML2 ISP3 source against Jupiter's graphics and memory interfaces | High. Identify which parts of memory input depend on CVIP, firmware and board resources. | Offline once the matching build-9601 source is available through Magic Leap's GPL offer. | None to hardware / yes |
| 2. Match the PSP harvest input and ID 254's two bases to revision-specific AMD definitions | High. Distinguish fuse shadow from other policy, or give the Mero record a defensible name. | Offline. Needs a matching register description, firmware symbol, or labeled IP map. | None to hardware / yes |
| 3. Read the two cached ISP base descriptors on the next normal LCD boot | Modest. Tests that sysfs exports both expected bases on the physical Deck. | High when the Deck is on. Ordinary user, two sysfs text files. [Command](../analysis/followup-isp.md#validation-and-driver-requirements) | Inventory only / yes |
| 4. Correlate an existing ML2 trace by frame ID and timestamp | High for buffer ownership and completion. | Requires an authorized recording with host, ARM and DSP events from the same headset. | Offline analysis of existing trace / yes |
| 5. Inspect a board-matched Jupiter firmware boot trace | High if it records an actual carveout or reset handoff. | Requires an existing trace with the relevant boot stage. | Offline / yes |

An active ISP frame test is a separate proposal in the driver report. It requires a supported test system, bounded DMA, documented firmware and power compatibility, a recovery boot, and explicit approval. [Prerequisites and limits](../analysis/followup-isp.md#separate-proposal-requiring-approval)
