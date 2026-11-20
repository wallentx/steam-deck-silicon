# Jupiter ISP3 check on the November 20 boot

**CONFIRMED.** The owner's LCD Deck exports both predicted ISP 3.0.0 register bases. The AMDGPU module loaded on the Deck has the build ID of the exact Valve module previously disassembled. Its boot journal lists ten AMDGPU blocks and omits ISP. SteamOS exposed no camera or media device. A working sensorless ISP path remains **UNKNOWN**. [Version selector and Mero comparison](../../analysis/followup-isp.md) · [Memory-frame feasibility](../../analysis/isp3-memory-path.md)

The kernel booted at **2026-11-20 06:54:37 UTC**. The SSH inventory began at **06:59:07 UTC** on Valve Jupiter, BIOS F7A0133, kernel `7.2.7-valve2-2-neptune-72-g31504582a073`. This was a separate boot from the earlier 04:32 UTC capture. The observations below come from kernel-maintained text, the boot journal, CPU identification and disk files. [Earlier capture](host.txt)

| Question | Observation |
|---|---|
| Which ISP resource is visible? | GPU `0000:04:00.0`, PCI `1002:163f`, bound to `amdgpu`. In `ip_discovery/die/0`, `ISP/0` and `44/0` resolve to the same object. Its single instance is 0, version `3.0.0`, harvest `0x0`, base count 2. The complete `base_addr` output is `0x00018000` followed by `0x0240B000`. These match the binary records from both Jupiter and Mero. [Record bytes and units](../../analysis/followup-isp.md#what-the-two-inventories-describe) |
| Do these bases fit in the GPU's register aperture? | The PCI resource table gives BAR5 a length of 524,288 bytes (`0x80000`). The driver independently logged `register mmio size: 524288`. Converting the two dword bases to byte offsets gives `0x60000`, inside that length, and `0x0902c000`, outside it. This checks address arithmetic only. The segment extent, route to the second segment and whether the ISP would respond to a transaction remain unknown. Both observations came from resource metadata and the journal. [Matching Neptune BAR selection](https://github.com/Jovian-Experiments/linux/blob/31504582a07316ae0e8a8fb3b8fdc39d94842816/drivers/gpu/drm/amd/amdgpu/amdgpu_device.c#L3927-L3947) |
| Which driver actually ran? | SHA-256 of the installed, decompressed `amdgpu.ko.zst` is `990f7525b2325a617ecdf8e3cde2669d011c35b4e8735a6732a1902664855a02`. The running module's GNU build ID from sysfs is `65662cc623f2f9609bd466ba54f497a5aba4a5b1`. Both match the Valve package analyzed offline. Module parameters were `discovery=-1` and `ip_block_mask=4294967295` (all 32 bits set). [Disassembled version gate](../../analysis/followup-isp.md#where-jupiter-stops) |
| Did it register a camera? | The ten `detected ip block` records name common, GMC, IH, PSP, SMU, display, GFX, SDMA, VCN and JPEG. There were zero entries in the V4L2 and media class inventories and zero `/dev/video[0-9]*` or `/dev/media[0-9]*` nodes. The GPU did expose `card0` and `renderD128`. Neither Mero ISP firmware filename was found directly under the standard firmware roots in its expected subdirectory, including the `.zst` and `.xz` variants. |

## SMU, PSP and the CVIP policy predicate

**CONFIRMED on this Deck.** The GPU's boot journal reports SMU **driver interface 3 and firmware interface 3**, program 6, firmware `0x063f0f00` (63.15.0), followed by successful SMU initialization. Mero's compiled driver expects interface 2. This closes the runtime-version question on Jupiter. Acceptance of Mero's ISP image, tile-power commands and clocks on this board was not tested. The journal also records a **10 MiB** PSP trusted-memory reservation. It does not attribute that region to ISP or CVIP. [Firmware and SMU comparison](../../analysis/isp3-firmware-and-smu.md#smu-comparison)

**CONFIRMED on this CPU.** The AMD Custom APU 0405 reports family 23, model 144, stepping 2. On logical processor 0, CPUID leaf `0x80000001` gives EAX `0x00890f02` and EBX `0x30000000`. The masked EAX is `0x00890f00` and the high EBX nibble is 3, satisfying both Jupiter DXE checks. The installed F7A0133 capsule also hashes to `c8b1e749ad709bf20899eed59bd9012a8482b55003d2785134f0b17876a240d9`, exactly matching the file used for that analysis. Whether the firmware dispatcher ran the callback or powered CVIP remains **UNKNOWN**. [DXE predicate and callback](../../analysis/jupiter-policy-and-mero-id.md)

All 30 PCI functions had readable identifiers. There were zero `1022:149d` CVIP endpoints and zero SATA-class functions (`0106`). The only child of bridge `00:08.2` was `05:00.0 1022:145a`, class `130000`. The fresh discovery blob and TPM firmware event log required elevated access. Noninteractive sudo required a password for the discovery read. The SATA harvest bytes reported elsewhere still refer to the earlier capture. [Earlier harvest bytes and hashes](runtime-comparison.md)

## Reproduce the central observations

Run these commands as the ordinary login user on the same kernel. The first command prints the count followed by both bases. The other commands select this GPU's boot records, hash the installed module and print only the two CPU fields used by the firmware predicate.

```sh
isp=/sys/bus/pci/devices/0000:04:00.0/ip_discovery/die/0/44/0
cat "$isp/num_base_addresses" "$isp/base_addr"
journalctl -k -b -q -o cat --no-pager | grep -F 'amdgpu 0000:04:00.0:' | grep -E 'detected ip block|register mmio size|smu driver if version'
zstd -dc -- "$(modinfo -n amdgpu)" | sha256sum
env -i LC_ALL=C /lib64/ld-linux-x86-64.so.2 --list-diagnostics | grep -E '^x86\.processor\[0x0\]\.cpuid\.eax\[0x80000001\]\.(eax|ebx)='
```
