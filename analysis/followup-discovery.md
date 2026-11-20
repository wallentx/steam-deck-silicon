# Who writes the Deck SATA harvest record, and what Mero ID 254 describes

**STRONG EVIDENCE.** Valve’s F7A0133 PSP bootloader contains a routine that produces the exact SATA record seen on the owner’s Jupiter. It samples a 32-bit input, selects bit 1 for its SATA entry, writes hardware ID 168 with instance 0, and recomputes both checksums. The earlier capture matches the output this decision would produce. The physical source of the bit, the reason SATA fails to enumerate, and board wiring remain **UNKNOWN**. The Deck was offline during this comparison. [Original runtime evidence](../evidence/deck-live/runtime-comparison.md) · [Valve capsule provenance](steam-deck-applicability.md)

## SATA from the signed capsule to the driver cache

**CONFIRMED.** I re-extracted the F7A0131 and F7A0133 capsules from Valve’s packages and verified the full SHA-256 digests against the earlier investigation. On F7A0133 the first PSP level-two directory (`$PL2`) starts at capsule offset `0x168c70`. Slot 11 at `0x168d30` names entry type `0x20`, length `0x62c`, with a table-relative address of `0xcba00`. Its `$PS1` wrapper begins at `0x234670`. The logical discovery binary starts 256 bytes later at `0x234770`. The second directory at `0x968c70` supplies an identical wrapper at `0xa34670`. The four wrappers across both BIOS releases are byte-identical, SHA-256 `e2c49dd81a0a88a4b23dd57891e1059d40f87dab7e8b5b13bae3db57b65047c0`. Coreboot calls type 0x20 `AMD_FW_PSP_HW_IPCFG`. [Valve F7A0131 package](https://steamdeck-packages.steamos.cloud/archlinux-mirror/jupiter-3.6/os/x86_64/jupiter-hw-support-3.6.20240905.1-1-any.pkg.tar.zst) · [Valve F7A0133 package](https://steamdeck-packages.steamos.cloud/archlinux-mirror/jupiter-main/os/x86_64/jupiter-hw-support-20261028.1-2-any.pkg.tar.zst) · [Coreboot PSP directory types](https://github.com/coreboot/coreboot/blob/8329c70b1077e36702410503972d3925f7b57a2d/src/vendorcode/amd/psp/psp_directory.h#L78-L94)

**CONFIRMED in the distributed executable.** The same directory’s slot 2 contains type `0x73`, `AMD_FW_PSP_BOOTLOADER_AB`. Both F7A0133 copies at `0x16b970` and `0x96b970` hash to `e54ff1fafe76eeaded583c98ca7a661d2599a24b5aef5e440b09fb12c7280bd0` over `0x10d00` bytes. The header contains `AER ` at `+0x64`, load address `0x100`, and a `0x10a00`-byte payload starting at capsule offset `0x16ba70`. The following are **offsets in that payload**, which hashes to `0d60b2a1271aec023dd695625246802b4d91ac08a81ecaae37d530e9380f33a3`. A linked pointer to payload data is its file offset plus `0x100`. [Coreboot bootloader entry type](https://github.com/coreboot/coreboot/blob/8329c70b1077e36702410503972d3925f7b57a2d/src/vendorcode/amd/psp/psp_directory.h#L139-L143) · [PSP header layout](https://github.com/PSPReverse/PSPTool/blob/88daed8eb5f94d7cd61f1fb9c19091492e6cd05e/psptool/header_file.py#L76-L94)

| F7A0133 payload offset | Recovered operation |
|---|---|
| `0xb400–0xb408` | Caller supplies type `0x20` to the preceding helper, passes the same destination buffer to the routine at `0xdc88`. |
| `0xdc98–0xdcc6` | Checks signature `0x28211407` and the existing byte sum. Uses the header’s harvest-table offset at `+0x1c`, clears `0x88` bytes, writes `HARV`, and reads one word at the PSP-space address in literal `0xdd38` (`0x03200010`). This is an address observed in code. |
| `0xdccc–0xdcd8`, helper `0xab58–0xab8a` | Iterates selectors 0 through 56. For selector `0x2c` (44), the helper returns bit 1 from the sampled word. A zero result skips the slot. Other selectors test different bits or return zero. |
| `0xdce0–0xdd0e` | Loads a 16-bit ID from the table at linked address `0xe79c` (payload `0xe69c`). Entry 44 at `0xe6f4` is `a8 00`. Writes the ID and an initial instance of zero. The optional remap helper at `0xb9a4` leaves SATA unchanged. Up to 32 harvest slots can be emitted. |
| `0xdd10–0xdd2a` | Sums all 136 HARV bytes and stores the result at header `+0x1e`. Sums logical bytes from `+0x0a` through the declared end and stores the result at `+0x08`. The byte-accumulation helper is at `0xa0b8`. |

F7A0131 has the same selector helper bytes at `0xab40` and producer at `0xdc70`, with the same input literal and SATA lookup result. Its full type-0x73 entry has a different digest, `463b62fade12ab2ad08c7b080af816f2a79068c301e8718e76feaf50cd9c3c79`. AMD’s cross-product PSP notes independently describe discovery loading, an IP-harvesting fix and skipping discovery loading on some resume paths. Those notes do not identify the Jupiter input. [AMD loading entry](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/PSP_ReleaseNotes.txt#2553) · [AMD harvesting entry](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/PSP_ReleaseNotes.txt#2359) · [Resume entry](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/PSP_ReleaseNotes.txt#2305)

**CONFIRMED against the published runtime digest.** Starting with the 1,068-byte F7A0133 template (SHA-256 `28451c4acb6e035dc4eb610f674ee2834c36c3108b97d75a002fcd7555b34895`), emitting SATA alone and summing the result gives `85eff526aab15ddcc74261aa8a6520517d588107a058a83f07afda77b4a94880`, exactly the original live digest for the logical region. This was an in-memory reconstruction. The original 10,240-byte raw debugfs file was unavailable for a fresh read. Its 9,172 trailing bytes are outside the logical record. [Recorded capture, lengths and digests](../evidence/deck-live/runtime-comparison.md)

| Offset from discovery signature | Stock → reconstructed live | Meaning |
|---|---|---|
| `0x008`, `0x009` | `37 4d → 87 4e` | Whole sum `0x4d37 → 0x4e87`, an increase of `0x150` since both changed bytes below contribute `0xa8`. |
| `0x01e` | `31 → d9` | HARV descriptor sum `0x0131 → 0x01d9`. High byte stays `01`. |
| `0x3ac` | `00 → a8` | First of 32 little-endian `<HBB` slots in HARV at `0x3a4`. Its four bytes become `a8 00 00 00`. The remaining slots are zero. |

**CONFIRMED in the matching kernel.** Neptune commit `31504582a07316ae0e8a8fb3b8fdc39d94842816` matches the Deck kernel’s build suffix. By default on this ASIC, `amdgpu_discovery_init` gets the discovery area from the reserved firmware memory region, copies it into `adev->discovery.bin`, and verifies signatures and sums. A module-parameter override can select a file instead. The read-only debugfs file exposes that in-memory copy. Its existence does not identify the earlier producer by itself. [Boot identification](../evidence/deck-live/host.txt) · [Memory and file paths](https://github.com/Jovian-Experiments/linux/blob/31504582a07316ae0e8a8fb3b8fdc39d94842816/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c#L265-L409) · [Source selection and verification](https://github.com/Jovian-Experiments/linux/blob/31504582a07316ae0e8a8fb3b8fdc39d94842816/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c#L668-L729) · [Debugfs blob](https://github.com/Jovian-Experiments/linux/blob/31504582a07316ae0e8a8fb3b8fdc39d94842816/drivers/gpu/drm/amd/amdgpu/amdgpu_debugfs.c#L2228-L2230)

For GC 10.3.1 the driver uses the HARV slot loop. ID 168 takes its default branch without changing an AMDGPU block mask. The sysfs harvest formatter reports masks for selected IPDS block types, and SATA is absent from IPDS altogether. **DISPROVEN** for the proposition that this AMDGPU code disables an AHCI PCI function when it reads the SATA slot. Earlier platform configuration can both disable a function and report it. [Selection](https://github.com/Jovian-Experiments/linux/blob/31504582a07316ae0e8a8fb3b8fdc39d94842816/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c#L1700-L1736) · [HARV consumer](https://github.com/Jovian-Experiments/linux/blob/31504582a07316ae0e8a8fb3b8fdc39d94842816/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c#L833-L907) · [Sysfs formatter](https://github.com/Jovian-Experiments/linux/blob/31504582a07316ae0e8a8fb3b8fdc39d94842816/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c#L1152-L1183)

**UNKNOWN upstream of the bit.** The code demonstrates how early firmware can construct a matching report. Neither a boot trace nor a trustworthy Jupiter definition of the sampled word was available. A permanent fuse sampled directly or through a latch, board/firmware policy, and earlier initialization feeding a status field remain possible. The inspected Van Gogh SMU host interface supplies no SATA-to-bit mapping. AMD AGESA notes discuss temporarily changing a SATA-disable control during DXIO training on **Vermeer/Qogir**, a different product. [Van Gogh SMU messages](https://github.com/torvalds/linux/blob/8d3ae59288f1e7d58d76558a6ee96d533bc5019f/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_ppsmc.h) · [AGESA Vermeer entry](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/AgesaBLReleaseNotes.txt#2096)

**UNKNOWN at the connector.** The owner’s ACPI path `GP18.SATA` resolves to PCI `05:00.0`, a `1022:145a` class `0x130000` function. The captured storage controller is NVMe class `0x010802` on a different branch. A public Jupiter SSDT adds a `PRT0` child whose `_GTF` returns a zero-filled buffer through a constant branch. Valve documents PCIe eMMC/NVMe in the LCD model’s M.2 2230 socket. These sources do not supply SATA lane routing, a SATA clock/reset network or a connected SATA port. [Local ACPI mapping](../evidence/deck-live/acpi.tsv) · [Local PCI class data](../evidence/deck-live/pci.tsv) · [Public SSDT](https://github.com/linuxhw/ACPI/blob/d6d30c6ef6f45506567f25a302c64f009d8f5f4e/Notebook/Valve/Jupiter/Jupiter/D98C04F8D964#L19702-L19727) · [Valve LCD specifications](https://cdn.steamstatic.com/steamdeck/images/press/techspecs/steamdeck_techspecs.pdf)

## Mero ID 254 in firmware order

**CONFIRMED.** Magic Leap OS 1.12.1 (`B3E.251015.01`, build 9601) provides `demophon_bios.FD`, SHA-256 `f4b050e9b7f518b084b4184b7818a7e03cdabc975f20357d99a11f66469c5b62`. Its two matching 1,084-byte type-0x20 discovery records at `0x14c800` and `0x8cc800` hash to `3a91175c612062d10875974d8c909b7957b7c927e2c3ac8f2fe756d2fe77a188`. All three populated table checksums pass. The following are real neighbors in the binary stream. The earlier per-ID TSV is sorted numerically. [Archive and catalog provenance](../evidence/artifacts.md) · [Member hashes](../evidence/host-index.tsv) · [Earlier inventory](../evidence/deck-live/ml2-bios-ip.tsv) · [AMD packed structures](https://github.com/torvalds/linux/blob/8d3ae59288f1e7d58d76558a6ee96d533bc5019f/drivers/gpu/drm/amd/include/discovery.h#L83-L121)

| Zero-based index on die 0 | BIOS offset (record relative) | ID / instance / IP version | Two 32-bit segment bases in file order |
|---:|---|---|---|
| 9 | `0x14c924` (`0x124`) | 47 / 0 / 11.5.0, CLKB | `0x00017e00`, `0x0240bc00` |
| 10 | `0x14c934` (`0x134`) | **254 / 0 / 1.0.0** | **`0x02445000`, `0x06540000`** |
| 11 | `0x14c944` (`0x144`) | 46 / 0 / 3.0.1, DF | `0x00007000`, `0x0240b800` |

The complete 16-byte entry is `fe 00 00 02 01 00 00 00 00 50 44 02 00 00 54 06`. The last header byte has zero harvest and reserved nibbles. The IPDS v2 die header declares 37 entries, consumes ID 254 as an ordinary variable-length record, then reaches the table end at relative `0x350`. **DISPROVEN** for the proposed end-marker interpretation. There is no extent or register-function field in the entry.

Keying both inventories by (ID, instance) gives 36 shared keys and one Mero-only key, (254, 0). Comparing all original entry bytes makes 32 of the shared keys identical. MP0, MP1 and MP2 use 11.5.1 on Mero and 11.5.0 on the Deck. MP2 additionally changes its first base from `0x00016000` on Deck to `0x00016400` on Mero. UVD/VCN changes from 3.0.2 to 3.1.0 with the same three bases. Both stock GC tables and both stock HARV tables are byte-identical. [Deck inventory](../evidence/deck-live/deck-bios-ip.tsv) · [Mero inventory](../evidence/deck-live/ml2-bios-ip.tsv)

**CONFIRMED negative control from the shipping driver.** The Mero `vendor/lib/modules/5.4.19-android-x86_64/kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.ko` SHA-256 is `ca31bf6b6751b6bcf8073daf7244a3dfb437e938c40905a5d5f04b94bc86cb9f`. Its ELF symbol `hw_id_names` covers 300 64-bit slots at `.data+0x3900`. Slot 254 at `.data+0x40f0` (file `0x5747a0`) is eight zero bytes without a relocation. Control relocations resolve to ISP (44), DF (46), CLKB (47), SATA (168) and MP0 (255). The module’s 28-element `hw_id_map` at `.rodata+0x5d20` also omits 254. Linux v5.4, current-generation v7.2 and the inspected ROCm vendor `soc15_hw_ip.h` each define 255 as MP0 and supply no definition with value 254. [Shipping module inventory](../evidence/host-index.tsv) · [Linux v5.4](https://github.com/torvalds/linux/blob/219d54332a09e8d8741c1e1982f5eae56099de85/drivers/gpu/drm/amd/include/soc15_hw_ip.h) · [Linux v7.2](https://github.com/torvalds/linux/blob/8d3ae59288f1e7d58d76558a6ee96d533bc5019f/drivers/gpu/drm/amd/include/soc15_hw_ip.h) · [ROCm driver](https://github.com/ROCm/ROCK-Kernel-Driver/blob/f818e1c3fa05eb652ece8680f63a5eae22daadba/drivers/gpu/drm/amd/include/soc15_hw_ip.h)

**UNKNOWN identity.** The public Van Gogh offset header matches the named blocks around this record but contains neither of its bases. On a different ASIC, Sienna Cichlid, `0x02445000` *does* occur as VCN instance 1, segment 2, following two different addresses. On Mero, VCN already has its own ID 12 record, instance 0, and different bases. A single segment value reused across ASICs cannot assign a name. The 1.12.1 Mero name table, the discovery record, and the known CVIP PCI endpoint provide no mapping between ID 254 and CVIP. A matching Mero register/IP map, a labeled firmware table containing the full pair, or vendor source directly binding 254 would resolve it. [Van Gogh offset map](https://github.com/torvalds/linux/blob/8d3ae59288f1e7d58d76558a6ee96d533bc5019f/drivers/gpu/drm/amd/include/vangogh_ip_offset.h) · [Sienna Cichlid VCN tuples](https://github.com/torvalds/linux/blob/8d3ae59288f1e7d58d76558a6ee96d533bc5019f/drivers/gpu/drm/amd/include/sienna_cichlid_ip_offset.h#L191-L193) · [ML2 endpoint](../evidence/device-identifiers.md)

Static inspection of AMD’s UMR register tool provides another control. The program at `vendor/bin/umr` (SHA-256 `88d010b06c9a205469dd6108bb8244d2fdff775dc6f9721114320337fe754bbe`) has a `mero` ASIC builder at ELF VA `0x227cd80`. Its 13 called block helpers name blocks including CLK, DCN and UVD. None names ID 254. A literal scan found no packed little-endian pair of the two Mero bases. Magic Leap’s published kernel file list names the two headers to request for the exact build, `drivers/gpu/drm/amd/include/asic_reg/mero_ip_offset.h` and `drivers/gpu/drm/amd/include/mero_ip_offset.h`, at notice lines 1689183 and 1689227. Those lines provide filenames only. [Full member inventory](../evidence/host-index.tsv) · [Magic Leap hardware notices](https://site-assets.magicleap.com/live/dotCOM/ML2HW_Consolidated_notices_11_26_2024.txt) · [Corresponding-source offer and scope](../evidence/source-references.md)

## Recheck offline

Use extracted, hash-matched personal copies named as below. All firmware reads are ordinary file reads. The comparison is performed in Python memory.

```sh
python3 - <<'PY'
import hashlib
import struct
from pathlib import Path

capsule = Path("F7A0133_sign.fd").read_bytes()
record = bytearray(capsule[0x234770:0x234770 + 1068])
assert record == capsule[0xa34770:0xa34770 + len(record)]
print("stock", hashlib.sha256(record).hexdigest())
record[0x3ac] = 168
struct.pack_into("<H", record, 0x1e, sum(record[0x3a4:]) & 0xffff)
struct.pack_into("<H", record, 0x08, sum(record[0x0a:]) & 0xffff)
print("reconstructed", hashlib.sha256(record).hexdigest())

mero = Path("demophon_bios.FD").read_bytes()
print("ID 254", mero[0x14c934:0x14c944].hex(" "))
PY
```

For the Thumb offsets, make an analysis copy in a private scratch directory. The ELF wrapper is input to a disassembler. For the name-table check, inspect only the `.rela.data` section since relocations in other sections use their own offsets. The existing decoder can also compare a genuinely captured debugfs file and the stock capsule. [Existing decoder and commands](../reports/reproduction.md)

```sh
dd if=F7A0133_sign.fd of=deck-bl2.bin bs=1 skip=$((0x16ba70)) count=$((0x10a00)) status=none
llvm-objcopy -I binary -O elf32-littlearm -B arm --rename-section .data=.text,alloc,load,readonly,code,contents deck-bl2.bin deck-bl2.o
llvm-objdump -D --triple=thumbv7a --start-address=0xdc88 --stop-address=0xdd30 deck-bl2.o
llvm-objdump -D --triple=thumbv7a --start-address=0xab58 --stop-address=0xab8c deck-bl2.o
readelf -Ws amdgpu.ko | grep -E ' hw_id_(names|map)$'
readelf -rW amdgpu.ko | sed -n "/Relocation section '.rela.data'/,/^$/p" | grep -E '^0*(40f0|40f8) '
```
