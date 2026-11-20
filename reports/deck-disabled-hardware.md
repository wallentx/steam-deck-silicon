# Hardware visibility on the owner's LCD Steam Deck

On Valve Jupiter BIOS F7A0133, AMDGPU reports a versioned image signal processor (ISP 3.0.0, instance 0, hardware ID 44). All 36 hardware-ID/instance/version tuples in its live discovery tree match the stock F7A0133 firmware's discovery table. The boot log identifies ten AMDGPU driver blocks, including graphics, video and JPEG. It lists no ISP driver block. The running kernel enables CONFIG_DRM_AMD_ISP, but the installed AMDGPU module exposes ISP driver descriptors for 4.1.0 and 4.1.1. No video or media device node was observed. On Jupiter, an ISP3 driver binding, board camera connection, usable image input and actual execution remain unverified. [Live GPU discovery](../evidence/deck-live/ip-discovery.tsv) · [Running kernel and boot messages](../evidence/deck-live/subsystems.txt)

The follow-up identified a version-matched driver in the shipped Mero software. It selects ISP3 and requests matching firmware. Jupiter's matching kernel skips ISP3 registration. Whether that Mero implementation can process a frame on Jupiter remains open. [ISP3 registration, firmware and memory input](../analysis/followup-isp.md)

## ASIC discovery tables

The two official Valve F7A0131 and F7A0133 capsule files both contain a 1,068-byte, checksum-valid discovery binary at offsets 0x234770 and 0xa34770, SHA-256 28451c4acb6e035dc4eb610f674ee2834c36c3108b97d75a002fcd7555b34895. Its version-2 IPDS lists 36 instances. All per-instance harvest nibbles are zero. The separate HARV table at relative offset 0x3a4 has 32 empty records. The live sysfs harvest column also reads zero for every instance. These records describe firmware and driver reporting. They cannot establish electrical enablement or manufacturing fuse values. The upstream sysfs formatter's per-block logic covers only selected block types, so an ISP zero by itself has limited meaning. The raw runtime capture subsequently revealed a SATA harvest record outside the 36-instance IPDS inventory. [Runtime comparison](../evidence/deck-live/runtime-comparison.md) [Decoded BIOS entries](../evidence/deck-live/deck-bios-ip.tsv) · [AMD structure definitions](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/include/discovery.h) · [Upstream harvest reporting](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c#L984-L1012)

The existing ML2 image provides an offline control. Its BIOS block at offset 0x14c800 lists the same ISP version and base-address descriptors. It includes one additional hardware ID, decimal 254, instance 0, version 1.0.0. Its identity remains unknown. Other shared entries also have revision or address differences. The comparison supports distinguishing the named ISP from the independently established CVIP PCI endpoint 1022:149d. The Deck does not enumerate that endpoint. [Decoded Mero BIOS entries](../evidence/deck-live/ml2-bios-ip.tsv) · [Live PCI result](../evidence/deck-live/pci.md)

The follow-up found an exact-output SATA harvest producer in the Valve PSP bootloader. It also recovered the two Mero ID 254 bases and confirmed that the shipping Mero driver's own name table leaves that slot empty. [SATA production and Mero ID 254](../analysis/followup-discovery.md)

## ACPI functions and processor resources

| Function | Observations on this Deck |
|---|---|
| I2C controllers | I2CA through I2CD report status 15. I2CE and I2CF report zero. The DSDT conditions these optional controllers on the platform and controller-enable fields. No external wiring was verified. |
| UART controllers | FUR0 reports 15. FUR1 through FUR4 and the four legacy UAR descriptions report zero. Alternate descriptions can refer to the same resources, so these counts cannot be added to estimate spare physical ports. |
| Storage | EMM0 reports zero. The DSDT gates its availability on the OS branch and EMME. The active mmcblk0 reports SD and attaches through PCI 02:00.0. A populated eMMC chip was not established. |
| Audio | SPK1 and SPK2 report 15. SSDT4 declares an alternative SPK3 device, ID VLV1777, whose status method always returns zero. It describes SPI resources; it does not establish a third physical speaker. |
| CPU/GPU compute | All eight logical CPUs are present and online with SMT active. KFD reports 16 SIMDs and two SIMDs per CU, exposing eight GPU compute units. No spare CPU or GPU compute capacity was identified by this inventory. |

The numeric device status zero clears the present and enabled bits. The AML for individual controllers can return zero for more than one reason. These results describe platform exposure on this boot. Testing external pins, programming an accelerator, changing power, and reading raw registers were outside the investigation. [Live ACPI statuses](../evidence/deck-live/acpi-status.tsv) · [ACPI device status specification](https://uefi.org/specs/ACPI/6.6/06_Device_Configuration.html#sta-device-status)
