# Public source evidence

## Magic Leap's kernel source embedded in the notices

**CONFIRMED.** The November 2024 consolidated hardware notices include four GPL-2.0 kernel files as C source. The source identifies an actual device-tree match, a PCI topology filter and an application binary interface. This document predates OS 1.12.1. Its contents describe a vendor implementation and provide symbols to match against the downloaded build. The 129,539,557-byte original has SHA-256 `1d6b3d45baac6f8744d761d58b5fbfa4ca6a83ccb3185ac8f9f343e2d3208f7f`. [Vendor index](https://www.magicleap.com/legal/open-source-software-notices-ml2) · [Exact text examined](https://site-assets.magicleap.com/live/dotCOM/ML2HW_Consolidated_notices_11_26_2024.txt)

The following offsets are zero-based, in bytes, with an exclusive end. Each hash covers the verbatim bytes between the BEGIN and END marker lines, including CRLFs and blank lines. The vendor text contains a few broken lines within C identifiers.

| File in the notice | Start | End | SHA-256 of source block |
|---|---:|---:|---|
| cvip_plat_ioc.h | 118199126 | 118200746 | b5c50a0a8b8a4cc852d25b8bb919ebfea1d33e7349756c9ae77a15210375bc66 |
| cvip_plt.c | 118200825 | 118228786 | 436549051336ee2bbe024c4ec2bf368a7e22d8fe9ce55438cfd966646c41f122 |
| cvip_plt.h | 118228858 | 118230554 | 59c2329c1156d39ffeff4bd2756827294ac2dc2be4bfda5980b62e97f9c408ef |
| cvip_plt_pci.c | 118230630 | 118245538 | e06484ba491869ae22a7f2025fdff9843eae2115289e46d6746da386dc934d02 |

| Vendor notice lines | What the source establishes |
|---|---|
| 1688180-1688245, 1689953-1689958, 1690199-1690209, 1690239, 1690265-1690269 | The kernel 5.4.19 file list names an ARM64 Mortable board DTS, its DSP include, Mauna reference boards, Mero mailbox drivers, a PCI controller, a DSP driver and BIO-MMU support. These paths record changes by 2022. |
| 2979300-2979362, 2980245-2980351 | `cvip_plt_probe` initializes x86 and transport readiness, obtains persistent-property and crumb metadata, registers kernel notifiers, and calls `send_cvip_alive` when CVIP IPC is configured. The match table names `amd,cvip-plt`. The send routine is external to this source excerpt. |
| 2979797-2979838, 2980080-2980100 | The CVIP-side platform exposes separate device operations for shared transport, configuration properties, diagnostics and PCI. The transport mapping uses write-combining attributes. |
| 2980467-2980476, 2980763-2980840 | The PCI scan filter recognizes AMD root bridge `1022:1647`, NWL switch devices `19aa:5000/5001/5002` and Magic Leap MLH endpoints `1e65:b0ba/b0bc/b0bb` (default, bootloader, main firmware respectively). These identities describe hardware visible to the CVIP-side scan. An x86-facing CVIP driver match requires separate evidence. |
| 2981094-2981111, 1529855 | The notice identifies vendor GPL modules for networking, cross-processor communications and shared resources, including `mlnet`, `mero_xpc`, `gsm` and `shregion / shregions`. It separately describes an NFS client on CVIP and a server on LuminOS. |

**CONFIRMED.** Magic Leap offers corresponding source for the kernel at line 1688182 and for the listed modules at line 2981109. An exact-build request should identify OS 1.12.1, build B3E.251015.01, the x86 and CVIP kernels, the Mortable DTS files, the module list and their configuration/build files. A public exact-build repository was not located. The two public Magic Leap GitHub organizations expose earlier Lumin kernel repositories. [Source offer](https://site-assets.magicleap.com/live/dotCOM/ML2HW_Consolidated_notices_11_26_2024.txt) · [ML1 repository](https://github.com/magicleap/ml1-kernel-lumin) · [Earlier developer repository](https://github.com/MagicLeapDevs/kernel-lumin)

## Linux, AMD and firmware history

| Inspected source | Result |
|---|---|
| [AMD's 2020 Van Gogh PM commit](https://github.com/torvalds/linux/commit/f57d62a00a348530375f0dfca889d0848dadc782) | The patch introduces generic SMU message/feature names for CVIP power, A55 DPM and CVIP DSP DPM. This predates the consumer Deck. |
| [Van Gogh SMU driver at Linux v6.12](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c#L105-L114) and [feature mappings](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c#L179-L187) | The actual Van Gogh mapping table includes CVIP up/down messages, A55 DPM, CVIP DSP DPM and a separate ISP DPM feature. |
| [SMU message header](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_ppsmc.h#L72-L79), [feature header](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_pmfw.h#L83-L89), [throttle status](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_vangogh.h#L159-L170) | SMU v11.5 names CVIP messages 0x2a and 0x2b, ISP/A55/CVIP DSP feature bits 51/52/53, and a CVIP throttle status. These are interface definitions. No live status value was read or command sent. |
| [linux-firmware WHENCE](https://gitlab.com/kernel-firmware/linux-firmware/-/blob/73e8acec66b0a91513e0699567b7854f4161d8b5/WHENCE#L2692-2702) | The inspected manifest lists 11 Van Gogh AMDGPU files, including VCN, SDMA and DMCUB. A case-insensitive CVIP search returned no match in WHENCE. Firmware embedded under different names remains possible. |
| [coreboot/openSIL Phoenix memory map](https://github.com/coreboot/coreboot/blob/8329c70b1077e36702410503972d3925f7b57a2d/src/vendorcode/amd/opensil/phoenix_poc/memmap.c#L22-L30) | This generic map names a reserved-memory category for CVIP. Its Phoenix target and the nature of the lookup table prevent attribution to a Deck memory reservation. |

The inspected [Android common 5.4 drivers/soc tree](https://android.googlesource.com/kernel/common/+/250657e3e4fa0189d0ebf710093551ba4a1ea9c1/drivers/soc/) lacks a vendor AMD subtree at that path. GitHub default-branch text searches identified AMDGPU power-management references in Linux and its ROCm derivatives. A Mesa mirror returned zero CVIP hits. LLVM results included unrelated tracing-register names and Hexagon identifiers. These bounded searches did not identify an ML2 graph compiler or a Deck userspace execution runtime and cannot exclude software distributed under other names. [Mesa mirror](https://github.com/chaotic-cx/mesa-mirror) · [LLVM](https://github.com/llvm/llvm-project)

## Product and DSP references

Magic Leap's v5.7 specification, page 5, gives the core counts, SRAM, fixed-point rate, DRAM access and application-developer restriction. The inspected PDF has SHA-256 `42a737957a0a2d540f048b5397f4a5b5779f987841a5480e8b5008b58834ae99`. The public developer documentation describes the Android host. [Product specification](https://www.tdsynnex.com/na/us/magic-leap/wp-content/uploads/sites/85/2024/05/Magic-Leap-2_Detailed_Spec_Sheet_31012024_English_5.7.pdf#page=5) · [Developer hardware specifications](https://developer-docs.magicleap.cloud/docs/device/hardware/hardware-specs/)

The consolidated notice lists Cadence XI Library, XOS, XNNC, a VisionQ6 VFPU library and AMD's dspelfldr. Its introduction explains that development dependencies may be listed. These names support cross-checking firmware and ELF symbols. They alone cannot identify each core's configuration or enabled instruction extensions. Cadence describes configurable Vision-family DSPs and optional vector floating-point hardware. [Hardware notice, lines 248, 342-350, 824-826 and 3220075-3220101](https://site-assets.magicleap.com/live/dotCOM/ML2HW_Consolidated_notices_11_26_2024.txt) · [Cadence Vision family](https://www.cadence.com/content/dam/cadence-www/global/en_US/documents/tools/silicon-solutions/compute-ip/tip-vision-dsp-pb.pdf)
