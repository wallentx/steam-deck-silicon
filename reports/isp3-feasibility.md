# Jupiter ISP3 memory processing — offline verdict

**Mero can skip the two CVIP buffer callbacks. A complete sensorless ISP3 frame path on the LCD Deck remains unproved.** With CVIP disabled in the driver configuration, stream setup bypasses the CVIP metadata/statistics buffers. The stock Mero image assigns that setting twice. The later assignment is true. On normal initialization, logical memory camera 3 inherits camera 1's profile but keeps ring 4, which the command inserter rejects. The three shipped sensor drivers report ordinary sensor type 0. A separate settings override could select memory type 4 on a physical camera with a valid ring. No stock producer supplying an input plane on that route was identified. [Function-level assessment and dependency matrix](../analysis/isp3-memory-path.md)

**Live Deck check.** A subsequent Jupiter boot reported the predicted ISP bases `0x00018000` and `0x0240B000`. Its loaded AMDGPU build ID matches the analyzed Valve module. The boot journal lists ten blocks and omits ISP, and the Deck exposed no video or media node. [Live evidence and reproduction](../evidence/deck-live/isp3-boot-check.md)

The ordinary Mero capture path is traceable through interrupt, frame-done response and output dequeue. Its pixel buffers use a Mero graphics-memory operation absent from the matching Neptune UAPI. Mero and Jupiter agree on five ISP-related SMU message numbers. Mero's driver expects interface 2. Jupiter's boot journal reports interface 3 for both driver and firmware. Jupiter's firmware acceptance, memory-domain ownership and interrupt routing remain **UNKNOWN**. [Buffer audit](../analysis/isp3-buffer-dependencies.md) · [Firmware and SMU](../analysis/isp3-firmware-and-smu.md)

**The next experiment is to trace one host input plane** in Magic Leap's corresponding R64 ISP3 source through a valid ring assignment, submission and a matching frame completion. This test can proceed offline. [Offline acceptance criteria](../analysis/isp3-memory-path.md#offline-milestone)

## Other findings

| Lead | What changed |
|---|---|
| Jupiter SATA | AMD's Cezanne bootloader calls the same source address `MP0_FUSE_HARVESTING`. Jupiter uses bit 1 for SATA, while Cezanne decodes that bit differently. **STRONG EVIDENCE** for a harvest-status word. Its physical source and permanence on Jupiter remain unknown. [Binary comparison](../analysis/jupiter-policy-and-mero-id.md) |
| Jupiter CVIP power policy | The owner's live Deck CPUID passes the identified firmware predicate. The DXE registers a callback that can pass the feature words to the SMU service. The owner's boot provided no execution trace, rail measurement or CVIP endpoint. [Boot-policy trace](../analysis/jupiter-policy-and-mero-id.md) |
| Mero ID 254 | Sixteen instances across eight BIOS images contain one byte-identical discovery table. This establishes a stable record across four OS releases. Its hardware name remains **UNKNOWN**. [Cross-release comparison](../analysis/jupiter-policy-and-mero-id.md) |
| Fremont controls | An exact non-PRO 8540U boot has the same dummy-only bridge in its full PCI inventory. Its raw accelerator AML is unavailable. A real RX 7600S matches Fremont's 28-CU aggregate topology. Published comparator data still lack the four masks needed to match Fremont's exact WGP positions. [8540U boot](https://linux-hardware.org/?probe=3930a3484f&log=dmesg) · [RX 7600S owner capture](https://forum.garudalinux.org/t/can-no-longer-see-dedicated-gpu-works-on-live-garuda-usb-relevant-logs-attached/36886/1) |
