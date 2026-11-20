# CVIP boot assets and DSP program startup

The evidence separates three events. The fastboot helper assigns files to partitions. The platform must bring up the ARM environment before its services can run. The ARM vision runtime then starts DSP services and workers. Only the first and third stages can be traced directly in the inspected helper and AArch64 code. [Partition and firmware evidence](../evidence/firmware.md)

```text
ML2 release archive
  |
  +-- cbl / kernel / dtb / ramfs / oem  (distinct boot partitions)
  |       |
  |       +-- boot-ROM caller, reset sequencing, load addresses: unknown
  |
  +-- cvip_remote_ro  (ext4 + SHA-256 verity tree)
          |
          +-- systemd all_svc unit -> AArch64 all_svc -> CV engine Init
          |                                                |
          |                                                +-> DSP service start
          |
          +-- C5/Q6 program images and typed job maps -> DSP worker tasks
```

## Boot evidence on Magic Leap 2

**CONFIRMED.** The release carries an A55-named CBL, a kernel, a board DTB and a ramfs as separately targeted, signed/encrypted-header firmware. The package also carries an AArch64 Linux executable and a systemd unit whose ExecStart names that executable. The RO and RW filesystems both have the 33-byte mount marker expected for boot synchronization. The GPT labels and the vendor helper identify what each partition receives. The ordering in the helper is a provisioning order. It does not measure boot time. [Image and partition table](../evidence/firmware.md)

**STRONG EVIDENCE.** The ARM cluster has a distinct boot/software environment from Android x86, with its own kernel/ramfs payloads and GNU/Linux userspace. The release diagnostics expect separate CVIP-side log streams and component status reporting. In particular, `package/Linux/bootdr.py` checks for x86 shregion, MLNET link-up and Mero notifier at lines 1501-1528, and parses CVIP component status at lines 1530-1628. These strings are the vendor's expected diagnostics. No live ML2 trace was collected. The A55's ability to start without host or PSP cooperation, authentication enforcement, power-domain transitions, and inner firmware entry points remain UNKNOWN. [Firmware evidence and hashes](../evidence/firmware.md)

## ARM-to-DSP runtime calls

The [CVIP RO inventory](../evidence/cvip-side.tsv) identifies the precise AArch64 ELF and its companion program images. llvm-objdump and addr2line identify the following call sites in `kraken/lib/libcv_engine-cvip-arm-hw.so`. The addresses are ELF virtual addresses for this build. The instruction bytes are little-endian AArch64 BL calls through the library's PLT. These observations confirm function use even though imported implementations need a separate provider.

| Caller | Call-site VA | Destination or observed access |
| --- | ---: | --- |
| kraken::cv_engine::Init | 0xa41c8 | The function calls dsp_service_start through PLT entry 0x3f180. |
| runtime::GatherFunctionPointers | 0xc69f8 and 0xc6a80 | Both sites call LoadDSPSymbols. The ELF contains a /cvip_ro/kraken/bin/%s/%s_%s.jobs filename template at file offset 0xf3370. |
| runtime::LaunchWorkerThread | 0xbf158 | The worker path calls TaskControl::FindAndAttachToTask. |
| runtime::LaunchWorkerThread | 0xbf29c and 0xbf33c | The worker path contains calls to TaskControl::CreateTask and TaskControl::StartTask(void*, unsigned long). Branches and errors can select different paths. |
| runtime::EndWorkerThread | 0xc0400 | The shutdown path calls TaskControl::GetTaskRunState. |

**CONFIRMED.** The library also exposes `runtime::ExecuteJob` at 0x4a720, `EnqueueThreadJob` at 0x4d3c0, `DequeueThreadJob` at 0x4d5a0, `JobExecutionContext::GetDspAddress` at 0x46640 and `GetZPadPageIommuAddress` at 0x46c50. DT_NEEDED includes CVIP Mero XPC, shregion and message-queue libraries. Some small shared libraries are linkage shims. For example, `libdsp_control-cvip-arm-hw.so` declares `libdsp_control.so` as a dependency. An implementation inside a different image remains possible. [ELF provenance](../evidence/cvip-side.tsv)

**STRONG EVIDENCE.** The Q6 DSP executive contains task-manager discovery fields beginning at file offset 0x1b4d, XOS task diagnostics at 0x1841, iDMA descriptor and local-memory FIFO diagnostics at 0x231b, and task-to-stream-ID binding at 0x9074. The same file names `mero_xpc_common.c` at 0x3c72, IRQ status reporting at 0x3c96, `xpc_reply` at 0x3cd8 and three mailbox categories at 0x3db9-0x3ec2. These support a DSP-side task manager, interrupt-backed messaging and DMA. They do not identify which remote peer owns each mailbox, the x86 PCI function, a host BAR layout, or the mechanism used to release a core from reset. [DSP service image evidence](../evidence/firmware.md)

**UNKNOWN.** The exact serializer and buffer lifetime rules for submitting arbitrary DSP work, low-level image copy path, DSP boot vector, signed image verification chain and third-party toolchain availability remain unresolved. The AArch64 worker call sites demonstrate vendor task dispatch. They do not demonstrate that a new binary can run on an LCD Deck.

## Rechecking the calls

The commands below operate on the decoded files produced by the [CVIP-side inventory script](../scripts/cvip-side.py).

```bash
lib=work/cvip-side/cvip_ro/kraken/lib/libcv_engine-cvip-arm-hw.so
addr2line -C -f -e "$lib" 0xa41c8 0xc69f8 0xc6a80 0xbf158 0xbf29c 0xbf33c 0xc0400
llvm-objdump -d "$lib" | rg '^[ ]*(a41c8|c69f8|c6a80|bf158|bf29c|bf33c|c0400):'
c++filt < work/cvip-side/cvip_ro/kraken/bin/c5/all_svc_c5.jobs
veritysetup dump --hash-offset 256000000 work/cvip-side/cvip_ro.img
```
