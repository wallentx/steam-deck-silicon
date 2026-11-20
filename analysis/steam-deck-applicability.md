# Original Steam Deck LCD

## What the Deck exposes

**CONFIRMED.** Seven public PCI captures under Valve Jupiter each enumerate 30 PCI functions, including the LCD GPU `1002:163f`. None lists the ML2 kernel driver's `1022:149d` function. The captures span SteamOS 3.1 through 3.7 and have six distinct file hashes. One file from each exact minor version was selected in lexicographic repository-path order. A device can appear in these inventories without any driver bound. The PCI ID database separately assigns the name VanGogh CVIP to `1022:149d`. [ML2 ID evidence](../evidence/device-identifiers.md) · [PCI ID database](https://github.com/pciutils/pciids/blob/f56421679d662b6a6178adcf297f1a69b27db455/pci.ids#L5456)

| SteamOS | Primary capture | SHA-256 |
|---|---|---|
| 3.1 | [43F315AA0C](https://github.com/linuxhw/LsPCI/blob/716d5be960ffcac591ebb3309361bdce17cf6079/Notebook/Valve/Jupiter/Jupiter/008A08C1D8C0/STEAMOS-3.1/5.13.0-VALVE10.3-1-NEPTUNE-02176-G5FE416C4ACD8/X86_64/43F315AA0C) | `5e444e3ff635045345ea9f0eead25c185160e43fb37010bdd8ffce16b66fbbea` |
| 3.2 | [F7D66C8D35](https://github.com/linuxhw/LsPCI/blob/716d5be960ffcac591ebb3309361bdce17cf6079/Notebook/Valve/Jupiter/Jupiter/07D3FB6109DD/STEAMOS-3.2/5.13.0-VALVE15-1-NEPTUNE-02197-GF6EC7AD3762A/X86_64/F7D66C8D35) | `656d0d97af3b8899b969059e4af17068c8875cb00e0fad1d6062f9b2ea2b15cd` |
| 3.3 | [2ADCFCE1C0](https://github.com/linuxhw/LsPCI/blob/716d5be960ffcac591ebb3309361bdce17cf6079/Notebook/Valve/Jupiter/Jupiter/0080737A43A3/STEAMOS-3.3/5.13.0-VALVE21-1-NEPTUNE-02209-G2A5BDC1102A0/X86_64/2ADCFCE1C0) | `5e444e3ff635045345ea9f0eead25c185160e43fb37010bdd8ffce16b66fbbea` |
| 3.4 | [01E0010535](https://github.com/linuxhw/LsPCI/blob/716d5be960ffcac591ebb3309361bdce17cf6079/Notebook/Valve/Jupiter/Jupiter/079AE3D0AB50/STEAMOS-3.4/5.13.0-VALVE31-1-NEPTUNE/X86_64/01E0010535) | `74a96327ea6c09059e1a945be67f3d3e1c09b736221c440dd4ce38bba3505cb3` |
| 3.5 | [4A37142AF9](https://github.com/linuxhw/LsPCI/blob/716d5be960ffcac591ebb3309361bdce17cf6079/Notebook/Valve/Jupiter/Jupiter/01909D84022D/STEAMOS-3.5/5.13.0-VALVE35-1-NEPTUNE/X86_64/4A37142AF9) | `8a8f68f006994471675c7fa8570d8e36e9023533dc0348eb67f79cca2deefca4` |
| 3.6 | [348B004789](https://github.com/linuxhw/LsPCI/blob/716d5be960ffcac591ebb3309361bdce17cf6079/Notebook/Valve/Jupiter/Jupiter/063685FB56C5/STEAMOS-3.6/6.1.52-VALVE10-1-NEPTUNE-61/X86_64/348B004789) | `7ec4569182bd8002e289a8b1d22256ef15cfe6184e479c3ffe9de1f1fa031c4d` |
| 3.7 | [8DA5EA058B](https://github.com/linuxhw/LsPCI/blob/716d5be960ffcac591ebb3309361bdce17cf6079/Notebook/Valve/Jupiter/Jupiter/17411FAF6322/STEAMOS-3.7/6.8.12-VALVE2-1-NEPTUNE-68-G8D066AEACD49/X86_64/8DA5EA058B) | `c57c17192087a945b1ed0ee7a1991a04ee7ee076ff0f760596cdea8fe19729f4` |

**CONFIRMED.** The SteamOS 3.3 capture shows PCI bridge `00:08.2` (`1022:1648`) forwarding to bus 05, with I/O, memory and prefetchable memory windows disabled. Bus 05 contains only a dummy function at `05:00.0` (`1022:145a`). The display controller, encryption controller and audio coprocessor appear on another branch as `04:00.0` (`1002:163f`), `04:00.2` (`1022:1649`) and `04:00.5` (`1022:15e2`, bound to `snd_pci_acp5x`). None matches the Mero driver's ID. Firmware can allocate bus numbers differently across boots. The bridge path and function number provide the portable comparison. [PCI bridge and windows](https://github.com/linuxhw/LsPCI/blob/716d5be960ffcac591ebb3309361bdce17cf6079/Notebook/Valve/Jupiter/Jupiter/0080737A43A3/STEAMOS-3.3/5.13.0-VALVE21-1-NEPTUNE-02209-G2A5BDC1102A0/X86_64/2ADCFCE1C0#L74-L87) · [Downstream functions](https://github.com/linuxhw/LsPCI/blob/716d5be960ffcac591ebb3309361bdce17cf6079/Notebook/Valve/Jupiter/Jupiter/0080737A43A3/STEAMOS-3.3/5.13.0-VALVE21-1-NEPTUNE-02209-G2A5BDC1102A0/X86_64/2ADCFCE1C0#L182-L257)

**CONFIRMED.** Two independent ACPI *files* published under Jupiter describe `PCI0.GP18` with `_ADR=0x00080002` and a single child device, `SATA`, with `_ADR=Zero`. They lack the Mero sibling `GP18.CVIP` with `_ADR=One`. A case-insensitive whole-file scan also returns zero literal matches for CVIP, CVPE, Mero, RPMSG and AMDI0068. Both decoded namespaces contain PSP and ACP under GP17. A missing ACPI name only describes those tables. The numeric PCI comparison independently covers enumerated endpoints. [First ACPI capture](https://github.com/linuxhw/ACPI/blob/d6d30c6ef6f45506567f25a302c64f009d8f5f4e/Notebook/Valve/Jupiter/Jupiter/D98C04F8D964#L4159-L4289) · [Second ACPI capture](https://github.com/linuxhw/ACPI/blob/d6d30c6ef6f45506567f25a302c64f009d8f5f4e/Notebook/Valve/Jupiter/Jupiter/F3B9E861E0CA#L4158-L4288) · [ML2 device evidence](../evidence/device-identifiers.md)

| Public ACPI text file | SHA-256 |
|---|---|
| D98C04F8D964 | `93ec6a73a9e51f971b64adbaa93c844bccdc9d20956a2385b730bd36f74c120c` |
| F3B9E861E0CA | `9a24cf7e86e32f0baebd9638ec00637013b759f9a640c47b8cf1ed22189d2eeb` |

## What Valve's BIOS includes

**CONFIRMED.** Two LCD BIOS files distributed in Valve's package repository contain identical CVIP-related UEFI modules. Static extraction used libarchive for the outer package and uefi-firmware-parser 1.16 in firmware-volume scan mode for the PE32+ EFI x86-64 capsule. The inspection never invoked Valve's updater. The hashes below record the downloaded content. [Valve's 3.6 package](https://steamdeck-packages.steamos.cloud/archlinux-mirror/jupiter-3.6/os/x86_64/jupiter-hw-support-3.6.20240905.1-1-any.pkg.tar.zst) · [Valve's main package](https://steamdeck-packages.steamos.cloud/archlinux-mirror/jupiter-main/os/x86_64/jupiter-hw-support-20261028.1-2-any.pkg.tar.zst)

| Capsule path in package | Package SHA-256 | Capsule SHA-256 |
|---|---|---|
| usr/share/jupiter_bios/F7A0131_sign.fd | `861629c1c0dedaeb5ebb4f3e993bba486b7570f97f90ed16c06ca55fc1f307ff` | `c1d47a42cb7480bf581b2dedfdb3152772fe119e4568f1ab0113f334de57f8b8` |
| usr/share/jupiter_bios/F7A0133_sign.fd | `27d80a9931381ea3f7c3c6a2fa6aef5c80b4c7aaeffc052788e7d704a7362ae1` | `c8b1e749ad709bf20899eed59bd9012a8482b55003d2785134f0b17876a240d9` |

Each firmware volume at capsule offset 4181104 or 12569712 (decimal) has the following module path under the parser's output. The file's UI section supplies its name. Each executable is a PE32+ EFI x86-64 boot-service driver.

```text
volume-<decimal offset>/file-20bc8ac9-94d1-4208-ab28-5d673fd73486/
  section0/section1/volume-ee4e5898-3914-4259-9d6e-dc7bd79403cf/
    file-<GUID>/section1.pe
```

| Module and file GUID | SHA-256 of PE section | Evidence inside that section |
|---|---|---|
| SmuV13Dxe, 8fd29f8b-8e6a-4ba1-b68c-0e3da4a3ba9f | `371b04c3cc217922828d32889512a342eb4c85a516dcd5b590ca72039685ad61` | At RVA 0x35c9 the routine takes the address of the feature label at 0x9100. At 0x35d0 it masks bit 21 of a software value, and at 0x35e1 it calls a shared diagnostic routine. Other references pair software fields with CVIP rail labels. The current-limit diagnostic at 0x37cb reads a 32-bit field from a structure. |
| CbsSetupDxeFF3, 3114f98c-5a36-44b4-8eb9-0ab945ce52d9 | `4e0f057947287da4cc385b3f51c88faaa389ebafbbb3f16eb1276f9f8077dd38` | UTF-16LE setup strings include a CVIP reserved-memory test setting at 0x94e0 and VDDCR_CVIP TDC/EDC current-limit fields at 0x11a7d/0x11d27. |

The feature label is `FEATURE_CVIP_DSP_DPM`. The ASCII fields at 0x93c8, 0x9460, 0x98b8 and 0x9e90 describe rail current limits, forced voltage and a power-saving setting. The code proves that these BIOS builds know the field definitions. A stored limit or feature name cannot establish the measured voltage, the runtime mask, the user-visible setup options or an electrically connected rail. Scans for Mero also matched fragments of Spanish strings in a network driver and the unrelated UI name TimeRoller. Those matches provide no platform evidence.

### AMD bootloader directory

**CONFIRMED.** Both LCD capsules contain two 26-entry PSP level-two directories (`$PL2` at 0x168c70 and 0x968c70). The 16-byte entries start after the directory's 16-byte header. Both copies of entry type 0x30 use a table-relative offset of 0xf0c00, yielding capsule offsets 0x259870 and 0xa59870. Both copies within each release have identical content. Neither directory includes type 0x57. This exclusion is scoped to those directories. PSPTool 3.7 failed with a bounds assertion on these inputs, so the following results use direct structure parsing.

| BIOS | Type 0x30 size | SHA-256 | Only CVIP ASCII match in expanded subsections |
|---|---|---|---|
| F7A0131 | 0x6bb80 | `0cc779361fe3fac848ef5c1c8da974082e2a4efe881ac2238d8b192e89cbe8a2` | Subsection 0x11 contains a memory category at 0x53d4. |
| F7A0133 | 0x6bbe0 | `7d0ec95c21af61653cfd0f243ea0074fec29898a58f13c867d04337a19bbfc46` | Subsection 0x11 contains the same label at 0x5430. |

The entry contains an index of 21 little-endian type/offset pairs at 0x100 for subsections 0x10 through 0x24. Each subsection has a `$PS1` signature at offset 0x10 and a standard zlib stream at 0x100. All 21 streams decompressed in both versions. The label occurs among UMA, MMIO and PrivilegedDRAM labels. Neither Deck release contains the explicit CVIP partition-table or image-copy messages identified in the ML2 ABL. Differences in logging or build configuration could produce that result. [ML2 firmware-loading analysis](firmware-loading.md)

AMD's published PSP release notes describe an AER-specific exclusion of CVIP from an RSMU table, and separate entries describe a graphics-to-PSP loading API, a carved-out memory region, a power-on message handler and reset release. The notes span several products. They establish that platform-specific differences existed in AMD's development tree, but do not establish the state of a retail Deck's fuses or power routing. The AGESA notes explicitly associate a CVIP PCIe bridge hotplug change with Mero. [AER entry](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/PSP_ReleaseNotes.txt#517) · [Power-on and polling entries](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/PSP_ReleaseNotes.txt#1289) · [Mero PCIe hotplug entry](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/AgesaBLReleaseNotes.txt#1779)

## Physical silicon and accessibility

**HYPOTHESIS.** High Yield's analysis of Fritzchens Fritz's photographs attributes a region of the LCD die to Mero-style CVIP. The estimated area, firmware references and shared PCI naming make this interpretation plausible. The photographs do not identify an executable endpoint, prove a matching six-A55/eight-accelerator configuration or demonstrate compute performance. Valve lists different APU fabrication nodes for LCD and OLED models. This report's BIOS and captures cover the LCD model only. **UNKNOWN.** Actual block presence, clocks, fuses, rail connectivity, board policy and support for an ML2 firmware image on either Deck revision remain unresolved. [Original die analysis at the CVIP chapter](https://www.youtube.com/watch?v=ERm1StY-4uY&t=743s) · [Valve hardware specifications](https://www.steamdeck.com/en/tech)

**STRONG EVIDENCE.** The inspected Jupiter boots do not provide the ML2 driver's ordinary PCI binding path even though the Deck firmware includes CVIP-specific code. An experimental Linux driver would first need an already enumerated endpoint, OS-assigned resources, an appropriate firmware/boot contract and an independently verified host protocol. A useful userspace runtime would additionally need known capabilities, buffer ownership, workload representation, completion and error semantics. The observations support no estimate for Deck inference throughput and do not establish that a Linux driver alone could make the block usable.

## Read-only test on another LCD Deck

From the investigation directory, run the [collection script](../scripts/steam-deck-readonly.sh) on a Jupiter LCD Deck. It accepts an existing output parent, creates a new private directory, reads kernel-maintained PCI and ACPI inventory, copies accessible DSDT/SSDT files and hashes its outputs. It only reads the textual PCI resource inventory. Raw PCI configuration/BAR access and ACPI method evaluation fall outside this test. The owner subsequently ran the collector on an LCD Deck and retrieved all 13 ACPI tables. [Live capture](../evidence/deck-live/acpi.md)

```bash
bash scripts/steam-deck-readonly.sh "$HOME"
```

A positive count for `1022:149d` would identify an enumerated candidate. Check its PCI bridge ancestry, resource metadata and corresponding ACPI path offline. A zero count extends the sample of boots without that PCI ID. A missing table in `aml-status.tsv` leaves its contents unknown. If table reads require administrator privileges, an administrator may run the same collector with an existing private output parent. The collector never invokes sudo. A positive identification still leaves firmware compatibility, operational readiness and compute performance to be established.
