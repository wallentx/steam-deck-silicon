# Jupiter SATA status, CVIP firmware policy and Mero ID 254

**STRONG EVIDENCE.** A second AMD platform names the PSP word that Jupiter uses for SATA harvesting. Jupiter’s CVIP policy also has a path from a CPUID-gated UEFI driver to an SMU service request. Both results come from offline firmware inspection. The eight Mero BIOS images examined contain one identical discovery table for ID 254.

## SATA — the upstream word now has a cross-platform name

**CONFIRMED on Cezanne.** AMD’s published `TypeId0x73_PspBootLoader_AB_CZN.sbin` is 67,712 bytes, SHA-256 `c3c927fdd6023eedcd86840104ff2db2a291e030a05972f1a4b4b1753fab8660`. Offsets here are relative to the payload after its 256-byte header. At `0x9d88` a Thumb literal load obtains PSP-space address `0x03200010` from `0x9e08`. The routine reads the word at `0x9d8e`, selects the format string `GPU MP0_FUSE_HARVESTING: %x` at `0x9e0c`, and passes that very word to the formatter at `0x9d92–0x9d94`. A second function reads the same address at `0xe3aa–0xe3b2` when rebuilding a HARV table. The diagnostic provides a name for the actual operand. [AMD Cezanne bootloader](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/TypeId0x73_PspBootLoader_AB_CZN.sbin) · [AMD’s accompanying release notes](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/PSP_ReleaseNotes.txt)

**STRONG EVIDENCE on Jupiter.** The AER-tagged F7A0131 and F7A0133 bootloaders sample the same address in the same HARV-producing role. In F7A0133 the SATA selector is `0x2c`, tests bit 1, and chooses ID 168, instance zero. The logical output matches the owner’s earlier captured digest exactly. In Cezanne’s reader at `0xe3c2`, the helper `0xaf1c` instead selects index `0x16` for bit 1 (`0xaf34–0xaf52`). The initial ID at that index in Cezanne’s table at `0xeaca` is 42 (SDMA0). Its SATA entry at index `0x32` takes the helper’s zero/default branch. This gives the status word a credible cross-product identity while demonstrating that its field-to-IP mapping varies by product. [Jupiter trace and structured reconstruction](followup-discovery.md) · [AMD hardware IDs](https://github.com/torvalds/linux/blob/8d3ae59288f1e7d58d76558a6ee96d533bc5019f/drivers/gpu/drm/amd/include/soc15_hw_ip.h)

**UNKNOWN upstream of the status register.** The aligned literal occurs five times in the F7A0133 type-0x73 payload. Four sites read or branch on the sampled word and one compares the address in a generic access routine. The same five literals occur in F7A0131, each 24 bytes earlier. The additional direct reads start at `0x5f52`, `0x5fe8` and `0xc9cc` in F7A0133. These are other consumers of the word. The trace located no boot-time assignment to bit 1 attributable to AGESA, the SMU, a board setting, or a physical fuse bank. Both Mero variants’ type-0x73 headers declare encryption in each inspected release. The Cezanne binary provided the plaintext comparator. An independently implemented PSP emulator identifies a different word in the same page as a key-size fuse on some platforms. Its map gives no Jupiter definition for `+0x10`. A direct eFuse sense, hardware shadow register, or firmware-influenced status remain distinguishable hypotheses. An AER register specification giving reset source and write semantics would resolve more than another cached HARV read. [PSP emulator’s modeled fuse registers](https://github.com/PSPReverse/PSPEmu/blob/b00465d276400a8d0aca090e62e7844ad25ed254/psp-dev-fuse.c#L89-L110) · [Magic Leap and Valve BIOS provenance](../evidence/revision-bios.md)

## CVIP — a reachable SMU policy path

**CONFIRMED in the firmware files.** F7A0133’s expanded DXE section has SHA-256 `dad11d4a8ba6c1b20ba696b33942b69a3bb149fa6496c7317127c5fd022b0eab`. Its `SmuV13Dxe` FFS header starts at expanded offset `0x10d5558`. Its DXE dependency expression at `0x10d5574` pushes nine protocols and ANDs all nine, SHA-256 `8bf60602c2f611d3b3d9cff6c981bb3545af903659320ad85b9259b25db914a5`. Mero 1.12.1 uses the same FFS GUID (`8fd29f8b-8e6a-4ba1-b68c-0e3da4a3ba9f`) in a different expanded section, SHA-256 `6f4b78ce7b784ff8f7658f930284668edc4f6cda0107454fad77c3a1b42e437f`. Its six-protocol AND expression at `0x338a44` hashes to `2172fcf202a7f27d65cf19740083d0e283042de4f5085b7003f04fc711e23d88`. A dispatcher needs all required interfaces installed before it can start the driver. [UEFI PI dispatcher rules](https://uefi.org/specs/PI/1.8A/V2_DXE_Dispatcher.html) · [SmuV13Dxe executable hashes and prior bit trace](followup-cvip-boot.md)

| Dependency group | Identifying evidence in Jupiter |
|---|---|
| Required on both | Marker `52f59e3c-8e4e-4d30-acda-bde4b927316f` from the SoC DXE below. In-image installers for GUIDs beginning `756db75c`, `2adcd53f` and `0ecad4a0` are `AmdNbioPcieDxe` at RVA `0x9ac`, `AmdFabricFf3Dxe` at `0x94e`, and `CbsBaseDxeFF3` at `0x5a4`. The other two are standard PI PCD (`13a3f0f6`) and SMBus Host Controller (`e49d33ed`). |
| Three added by Jupiter | `7189e04e` is installed by `AmdApcbDxeV3` at RVA `0x90d`. `0de50221` is installed by `ApobFf3Dxe` at `0x3f1`. `0379be4e` is the standard Device Path Utilities protocol. |

1. **Platform gate.** Jupiter’s `AmdSocFf3VnDxe` PE (SHA-256 `63133246a78965440c1426ec3b25b24caedad3953d8072cce9689ca056e62f77`) checks leaf `80000001h` at RVAs `0x7ef–0x82c`. It requires `(EAX & 0x0fff0f00) == 0x00890f00` and `EBX[31:28] == 3`. Its install loop at `0x8e8–0x919` includes marker pointer 12, at `0x15f0`. An independently published AMD Custom APU 0405 capture and the owner’s subsequent live Deck reading both give EAX `00890f02` and EBX `30000000`. The owner’s CPU passes both checks and the SMU module’s VN predicate. Execution of the marker-install loop on that boot remains unknown. Mero’s `AmdSocFf3MrDxe` (SHA-256 `99e6c3249086e317c33273f078a1b0016beddd9cc0989f260ab058069a68fb68`) publishes this same marker subject to a tighter EAX mask `0x0fff0ff0` and value `0x00890f80` at `0x55c–0x57c`. [Owner’s live CPUID](../evidence/deck-live/isp3-boot-check.md) · [Raw 0405 CPUID](https://github.com/InstLatx64/InstLatx64/blob/17be9a9793c306cf96f8c286e34e705b780a0226/AuthenticAMD/AuthenticAMD0890F02_K17_VanGogh_01_CPUID.txt#L27-L31)
2. **Entry and diagnostic.** Jupiter’s PE entry at `0x440` calls the main routine at `0xdf4` directly. On the normal path its table allocation at `0xf40` succeeds, and `0x100b` calls the platform policy fixup. The diagnostic at `0x129e` takes the PCD-derived word and reaches the CVIP DSP label in ordinary control flow. Printing is conditional on a separate logging interface (`669ed5b1-49a3-4c59-9d2d-0432ad6cdb61`), which the formatter looks up at `0x4cab`. It is absent from the nine required GUIDs. A missing diagnostic line cannot show this policy was skipped. The exit-boot-services callback registered by the constructor at `0x51a` is a return stub at `0x4e90`. [Existing feature/PCD trace](followup-cvip-boot.md) · [EDK II Boot Services ABI](https://github.com/tianocore/edk2/blob/0f3867fa6ef0553e26c42f7d71ff6bdb98429742/MdePkg/Include/Uefi/UefiSpec.h#L1930-L2007)
3. **Actual consumer of the policy.** The entry routine registers callback `0x1740` against GUID `addf9be3-1eb8-4472-95d1-f8cdde58e5bb` at `0x16b3–0x16c6`. The helper creates a notification event, registers the protocol, and signals the event once. `AmdCcxVhFf3Dxe` installs the GUID at Jupiter RVA `0xd34` (PE SHA-256 `c7e48ef4a28f52e12a32f7f65266dc1efec3cf2a9e884205b2c82d73f5f4d27b`) and Mero RVA `0xb31` (SHA-256 `ccba177a17515329526c3f2905cb635e2e154487abbc38d9c51c46c248a97af0`). Jupiter’s callback checks the interface at `0x179e` and returns early on failure. The successful path identifies itself as `CallbackAfterCcxDxeDone`. On a branch permitted by further platform checks at `0x1850–0x187e`, it reads both feature words and passes them to `SmuServiceRequest` at `0x18f7` or `0x192c`. The latter branch clears bit 26 of the extended argument, preserving bit 21, the CVIP DSP DPM field. This is a static path from configuration to a service request. The masks accepted by the SMU on this unit remain **UNKNOWN**.

**UNKNOWN on the owner’s boot.** The saved PCI inventory excludes `1022:149d` and the Deck AML describes only a function-zero child under GP18. Neither the saved logs nor the public CPUID capture record the nine interface installations, the callback’s branch, a returned SMU response, a CVIP carveout, reset release, a routed rail or a firmware handoff. The Mero ABL and PCI contrast still supplies the stronger evidence for the distinction in boot policy. DPM feature 53 is a clock/power-policy field. Its value alone cannot identify a missing endpoint’s cause. [Deck boot capture](../evidence/deck-live/subsystems.txt) · [Deck AML and PCI](../evidence/deck-live/acpi.md) · [Four Mero BIOS releases](../evidence/revision-bios.md)

## Mero ID 254 — stable across four releases

**CONFIRMED.** I extracted both regular and SSC BIOS files from OS 1.2.0, 1.2.1, 1.3.1 and 1.12.1. I verified all eight BIOS member hashes against the earlier release inventory. For the three older releases I read the archive prefixes through the two BIOS members. At offsets `0x14c800` and `0x8cc800` every image contains the same checksum-valid **entire** 1,084-byte discovery record, SHA-256 `3a91175c612062d10875974d8c909b7957b7c927e2c3ac8f2fe756d2fe77a188`. All sixteen copies therefore represent a single table design. Every instance at `0x14c934` or `0x8cc934` has version 1.0.0 and the same two dword descriptors, `0x02445000` and `0x06540000`. This excludes a one-release addition and any visible inventory change across the July 2023 compatibility boundary. [Member hash manifest](../evidence/revision-bios.md) · [Earlier official archive URLs](../evidence/revision-sources.md) · [1.12.1 archive](../evidence/artifacts.md)

**UNKNOWN function.** AMD’s independently published Cezanne type-0x20 record has 41 IP entries, and none has ID 254 or either segment base. The original Mero name-table and UMR controls yielded no binding. A new scan of the shipped ML2 x86 `vmlinux` (SHA-256 `f8891033b1f3b9cf9f25ef76d914173f1d43ff9a75df6764982207f0bd84f642`) returned zero first-base literals. Its sole apparent second-base literal at file `0x1cb345a` crosses fields in a sequence containing the aligned words `0x01f80650`, `0x01f80654` and `0x01f80658`. The arithmetic byte-offset control for the first base (`0x09114000`) is absent. The only `.text` match for the second scaled value (`0x19500000`) spans a displacement and an immediate in `ftrace_int3_handler` (`0xffffffff8105875a`). Neither scaled value is a demonstrated CPU physical address. A Mero register map naming the full pair, or software explicitly binding number 254, is still needed. [AMD Cezanne IP configuration](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/TypeId0x20_HwIpCfg_CZN_A0.sbin) · [Prior controls and exact vendor header names](followup-discovery.md)

## Reproduce the distinguishing bytes offline

The following Python command reads three original inputs without running them. The two manufacturer capsules have different absolute offsets for the GUID-defined LZMA stream. The inner FFS section type `0x13` is DXE DEPEX. Its `PUSH` operands are little-endian EFI GUIDs. [Valve input and hashes](steam-deck-applicability.md) · [Magic Leap input and hashes](../evidence/artifacts.md) · [UEFI dependency expression](https://uefi.org/specs/PI/1.8A/V2_DXE_Dispatcher.html)

```sh
python3 - F7A0133_sign.fd demophon_bios.FD TypeId0x73_PspBootLoader_AB_CZN.sbin <<'PY'
import hashlib
import lzma
import struct
import sys
import uuid
from pathlib import Path

driver = uuid.UUID("8fd29f8b-8e6a-4ba1-b68c-0e3da4a3ba9f").bytes_le
for name, base in zip(sys.argv[1:3], (0x3fcc70, 0x580000)):
    image = Path(name).read_bytes()
    length = int.from_bytes(image[base+0x90:base+0x93], "little")
    expanded = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(
        image[base+0xa8:base+0x90+length])
    pos = expanded.index(driver) + 24
    size = int.from_bytes(expanded[pos:pos+3], "little")
    assert expanded[pos+3] == 0x13
    dep = expanded[pos+4:pos+size]
    guids = []
    i = 0
    while dep[i] == 2:
        guids.append(str(uuid.UUID(bytes_le=dep[i+1:i+17])))
        i += 17
    assert dep[i:] == bytes([3]) * (len(guids)-1) + bytes([8])
    print(name, hashlib.sha256(dep).hexdigest(), guids)

czn = Path(sys.argv[3]).read_bytes()[0x100:]
print(hex(struct.unpack_from("<I", czn, 0x9e08)[0]),
      czn[0x9e0c:czn.index(0, 0x9e0c)].decode().strip())
PY
```
