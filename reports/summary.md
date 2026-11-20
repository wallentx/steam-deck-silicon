# Findings on one LCD Steam Deck

Valve's F7A0133 BIOS contains an empty hardware harvest table. The copy exported by the running AMDGPU driver lists one harvested component, SATA instance 0. This is the clearest direct evidence of a disabled block on this Jupiter unit. The exact mechanism remains unknown. [Byte comparison](../evidence/deck-live/runtime-comparison.md)

The GPU discovery inventory includes ISP 3.0.0. The boot log includes no corresponding driver block. The comparison with Magic Leap firmware distinguishes this image processor from the proposed CVIP accelerator. [Deck hardware inventory](deck-disabled-hardware.md)

Four ML2 kernels identify CVIP as AMD PCI 1022:149d. The live Deck exposes neither this ID nor the corresponding ACPI child, despite CVIP references in its BIOS. The evidence establishes that the standard ML2 driver has no matching endpoint on this boot. Physical presence and firmware compatibility remain unresolved. [Local PCI data](../evidence/deck-live/pci.md) · [Firmware revisions](hardware-revisions.md) · [ML2 architecture summary](ml2-summary.md)

The follow-up found the shipped Mero ISP3 driver and identified a PSP bootloader routine that reproduces the saved SATA harvest record. It also traced the CVIP power label to a firmware configuration word and a shipped hand-tracking result from ARM code to the Android interface. [Follow-up results and next experiments](followup-summary.md)
