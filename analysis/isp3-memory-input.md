# What SEND_FRAME_INFO consumes

**CONFIRMED.** Both ISP images in ML2 build 9601 dispatch command `0x02050002` to a real firmware handler. It accepts an external **frame-information package** with a build-specific size and checksum. **UNKNOWN** whether a stock host supplies a corresponding input image on a valid stream and whether the ISP reads its pixels. The last identifiable consumer is a post-frame-information queue. A queue entry alone does not establish pixel DMA, an image transform or a completed output. [Host protocol](isp3-command-protocol.md) · [Artifact hashes and load paths](isp3-firmware-and-smu.md)

## Two receivers with different layouts

The following offsets are byte offsets in the original files. Firmware VAs use a body origin of `0x60000000`, supported by command-table pointers, code and independent string references. The wrapped file's body begins at `+0x200`. The RAM file begins at the body itself. Generic Xtensa disassembly is strongest where baseline instructions, literal values, strings and the second build agree. Exact configuration-specific instruction semantics remain a limit.

| Build 9601 evidence | Wrapped `amdgpu/mero_isp.bin` | `isp_firmware_nawb_isp3.ram` |
|---|---:|---:|
| ID/pointer row between frame control and send-buffer | `+0x17038` | `+0xb7d8` |
| Linked handler / file offset | `0x6008d718 / +0x8d918` | `0x60092e9c / +0x92e9c` |
| Load of expected size / literal file offset | `0x6008d721 / +0x86120` | `0x60092ea5 / +0x83438` |
| Size of indirect package / equality branch VA | **4,728** (`0x1278`) / `0x6008d736` | **4,656** (`0x1230`) / `0x60092ebd` |
| Size-error diagnostic / handler-name string | `+0x13e50 / +0x15bc0` | Handler references its size diagnostic at VA `0x60092ec8`; name string at file `+0x9b50`. |

In the signed body, `DispatchStrCmd` at VA `0x60093c60` splits the command ID into a group and a low selector, indexes the directory at `0x600163b0`, bounds the selector, and fetches the handler pointer at `0x60093cdd–0x60093ce3`. The selected handler reads the size at command offset `+0x10`. On its matching-size branch, it uses the reference words at `+8/+12` and compares the computed package checksum to the byte at `+20` (`0x6008d782–0x6008d7af`). This distinguishes an address of *descriptive data* from the address of a plane inside that data. The two handlers' size requirements differ by 72 bytes. A package satisfying one size check fails the other. [Hash-gated receiver-size check](../scripts/inspect-isp3-build.py)

**STRONG EVIDENCE.** After validating the package, the firmware copies frame information into an internal representation. The wrapped handler copies a scalar from external `+0x790` to internal `+0x3d4` at `0x6008d88f–0x6008d897`; the sibling uses external `+0x788` and internal `+0x394`. The wrapped image contains the pipeline manager's host-frame-info failure and full-queue diagnostics (file `+0x17a28`, `+0x1809c`). The accepted queue branch constructs internal message type 7 (wrapped VA `0x60096098`, RAM VA `0x6009b324`). Its relationship to a particular raw read-DMA operation or frame-done response is **UNKNOWN**. Names of read-DMA buffer, size, format and start routines in the same image (`+0xa990–0xaa30`) do not supply that missing edge.

**CONFIRMED queue consumer code.** The wrapped image's `PopPostFrameInfo` routine at VA `0x600982c8` references its name at `0x600982d3` and the queue-pop diagnostic at `0x600982f6` (string at file `+0x18d44`). The RAM variant references the same queue-pop diagnostic at VA `0x6009d410` (file string `+0x2ec60`). Thus the firmware contains both enqueue and dequeue sides of this frame-information queue. Neither reference identifies the input pixel address consumed by an RDMA engine for one completed frame.

## Host producer search

1. **A recognizer.** Mero x86 `isp_send_fw_cmd_ex` recognizes this ID. At `K:a888cf–a8894d` its diagnostic uses two words at external `+0x77c/+0x780` as an address and three length operands at `+0x784/+0x790/+0x79c`. This supplies a minimum accessed extent of `0x7a0`. The arrangement resembles three planes. It establishes neither direction nor usable stride, packing, width or height. `K:` here is relative to `0xffffffff81000000`. [Packet and diagnostic fields](isp3-command-protocol.md)
2. **A missing issuer.** In the pinned x86 kernel's executable text, all five literal occurrences of `0x02050002` are comparisons, diagnostics or name lookup. The positive control, ordinary `SEND_FRAME_CTRL`, has a direct issuing site. The generic tuning route could receive a dynamically supplied ID. Its existence establishes no caller, input ownership or actual frame transaction. The observed `SEND_BUFFER` callers set up output/working storage. The Android input-buffer branch reaches host scaling or JPEG. [Exact call sites, XML and alternatives](isp3-frame-evidence.md)
3. **A broader negative control.** Searching allocated sections of 2,623 hash-checked ELF artifacts from the 9601 system, vendor, userdata and CVIP RO inventories found 2,612 with allocated SHT_PROGBITS sections of at least four bytes. Thirty files contained the little-endian command value somewhere. The only `.text` hits were two instruction-boundary coincidences in 32-bit `vendor/lib/libLLVM10.so` (ELF file offsets `0x2665fd8` and `0x26689b4`). The stock `vcam_isp_client` imports Android capture-session operations and `AImageReader_acquireNextImage`, consistent with an output consumer. No literal issue site was identified in these camera or CVIP client binaries. Constructed IDs, scripts, protected partitions and out-of-tree clients remain outside that negative. [Member index](../evidence/host-index.tsv) · [CVIP filesystem index](../evidence/cvip-side.tsv)
4. **A valid stream remains necessary.** The host rejects requested ring 4 *before* it redirects frame-info to physical command ring 0. A request originally for ring 0 produces tag `0xffff`; the signed firmware's stream-control dispatcher at `0x600943fb–0x60094404` accepts tags 0–2. Changing the physical slot cannot satisfy both conditions. Physical cameras with their own rings could qualify if sensor type were 4. The three shipped sensor callbacks report 0 and the override defaults to −1. The observed reset path deliberately leaves logical 3 without a stream assignment. Whether that reflects a private initializer, unshipped configuration or product policy is **UNKNOWN**. [Assignment census and firmware tag check](isp3-command-protocol.md) · [Sensor override](isp3-frame-evidence.md#can-a-registered-camera-keep-its-ring-and-acquire-memory-type-4)

**DISPROVEN for these specific paths.** The Android output minima (640 × 480 YUV), host-side scaling and YUV422 post-loopback do not individually demonstrate a sensorless ISP transform. The two XMLs advertise zero input streams, and the loopback diagnostic explicitly skips the core. Neither an input format contract nor a measured external input/output frame pair has been recovered.

## Offline reproduction

The [corpus scanner](../scripts/scan_isp3_frame_info.py) verifies the two committed member indexes and searches all eligible sections. Run `python3 scripts/scan_isp3_frame_info.py DIRECTORY` with the four read-only expanded images named `system.raw`, `vendor.raw`, `userdata.raw` and `cvip.raw`. It prints .text offsets from the beginning of the ELF file, including the section file offset.

Use the original files named above and the member digests in the [extraction guide](../reports/reproduction.md). The build verifier resolves the linked handler and its size literal from each file. GNU Binutils 2.44 with target `xtensa-unknown-elf` can disassemble the two receivers as data using these different VMA adjustments:

```sh
python3 scripts/inspect-isp3-build.py WORK
xtensa-unknown-elf-objdump -D -b binary -m xtensa -EL --adjust-vma=0x5ffffe00 --start-address=0x6008d718 --stop-address=0x6008d8ac mero_isp.bin
xtensa-unknown-elf-objdump -D -b binary -m xtensa -EL --adjust-vma=0x60000000 --start-address=0x60092e9c --stop-address=0x60092f3c isp_firmware_nawb_isp3.ram
```
