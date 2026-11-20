# CVIP hardware and compute workloads

## Processor and memory organization

**CONFIRMED.** Magic Leap describes 14 CVIP cores in the compute pack. Six are ARM Cortex-A55 cores, six are vector vision/ML cores and two are dedicated ML cores. The specification gives 1.28 MB of ARM subsystem SRAM, 4 MB of vector subsystem SRAM, a global 2 MB cache and LPDDR5 access. It also identifies hardware decompression and corner detection. The host has a separate Zen 2 CPU and RDNA 2 GPU. The manufacturer places CVIP outside the public application-developer interface. [Specification, page 5](https://www.tdsynnex.com/na/us/magic-leap/wp-content/uploads/sites/85/2024/05/Magic-Leap-2_Detailed_Spec_Sheet_31012024_English_5.7.pdf#page=5)

**CONFIRMED.** The OS 1.12.1 read-only CVIP filesystem packages AArch64 hand-tracking libraries, separate C5 and Q6 DSP service binaries, per-target Kraken programs, job maps and weights. Magic Leap's published CVIP kernel source includes the x86-alive and transport-ready interface. In this architecture, a CPU-side workload library, a DSP-specific job and the parameter file are distinct artifacts. [Local artifact hashes and architectures](../evidence/cvip-side.tsv) · [Vendor kernel source and identifiers](../evidence/source-references.md)

## A hand-detection workload in OS 1.12.1

Paths in this table start at the extracted `cvip_ro` root. ELF addresses are virtual addresses, DSP addresses are values printed in the job map, and string offsets are byte offsets in the indicated file. The evidence consists of static inspection only. [Per-file inventory](../evidence/cvip-side.tsv)

| Stage | File and location | What the bytes establish |
|---|---|---|
| Workload configuration | `kraken/etc/cv_engine_mero_live_hp_ht.yaml`, lines 6-36; SHA-256 `9e91520eb0c52266e4b3ae1d8daefbb91d20097405341c59f4b220b82576e6c1` | This configuration enables hand tracking, head pose and camera preprocessing. Comments document detection-weight overrides and a C5 coefficient path for development. They do not establish which config ran on a particular headset. |
| Parameter loading | `kraken/lib/libhand_tracking_blocks-cvip-arm-hw.so`, AArch64 .text, `DetectionNetWeights::LoadWeights` at 0x426c0 | The routine passes 0x4c6200 bytes to `LoadNetworkWeights`. That helper opens a file, seeks to its end, compares the length at 0x424ec and calls the stream read at 0x425bc. The packaged `kraken/resources/model_params/ht_detection_net_weights.bin` is exactly 5,005,824 bytes. |
| Network variants | Same ELF, functions starting at 0x426e0, 0x42700 and 0x42720 | The NMS, keypoint and DRN loaders pass 0x860e, 0xf34e00 and 0x9af080 bytes. Their sizes match `ht_detection_nms_weights.bin`, `ht_keypoint_net2_weights.bin` and `ht_drn_weights.bin` respectively. A second keypoint file has a different size. |
| DSP dispatch metadata | `kraken/bin/c5/all_svc_c5.jobs`, lines 2-4 of 5; `kraken/bin/q6/all_svc_q6.jobs`, 37 lines | C5 entry 0xc6082cd8 names detection weights, detection control, a world-camera frame, runtime parameters, scratch storage and output in its C++ type signature. Two other C5 entries specify keypoints. Q6 entries name descriptor extraction, corner tracking, depth preprocessing and a keypoint network. These type records identify packaged jobs. They do not define a portable user submission protocol. |
| DSP program | `kraken/bin/c5/all_svc_c5.bin` at 0x1ca2; `kraken/bin/q6/all_svc_q6.bin` at 0x1e4fd and 0x20244 | Both binaries have XNNC runtime-initialization diagnostics. The associated C5 and Q6 service images also contain `dsp_xnnc.c` and TCM bank diagnostics at byte offsets 0x274c/0x2780 and 0x2af9/0x2b2d respectively. |

**CONFIRMED.** The mangled type symbol at C5 job-map entry 0xc6082cd8 matches the exported ARM symbol at 0x18500 byte for byte in `kraken/lib/libhand_tracking_pkg-cvip-arm-hw.so`. Its package builder calls `GetC5SystemThread` at 0x2e390 and 0x2e3a4, `GetQ6SystemThread` at 0x2e3b8 and 0x2e3cc, and the detection-specific `Workload::CreateJob` at 0x2e9e0. In the separate AArch64 library `kraken/lib/libcv_engine-cvip-arm-hw.so`, `LoadDSPSymbols` at 0x91f00 opens a file, reads lines and parses a hexadecimal field with `strtoull` at 0x92544. The runtime calls that loader at 0xc69f8 and 0xc6a80, and calls `TaskControl::StartTask` at 0xbf33c. These findings link CPU-side jobs to DSP-side typed records. They do not establish which buffer reached which core at runtime. [Hashes for both libraries and job maps](../evidence/cvip-side.tsv)

**STRONG EVIDENCE.** Matching loader sizes, actual parameter files and C5 job signatures support a specialized hand-detection and keypoint-inference pipeline. The 5,005,824-byte detector parameters already exceed the published 4 MB vector SRAM size. The 15,945,216-byte keypoint variant is larger still. Installed model sizes therefore cannot be bounded by the on-chip SRAM figure alone. The inspected files do not establish where an implementation tiles, caches or streams each layer. [Firmware and parameter inventory](../evidence/cvip-side.tsv) · [Hardware memory specification](https://www.tdsynnex.com/na/us/magic-leap/wp-content/uploads/sites/85/2024/05/Magic-Leap-2_Detailed_Spec_Sheet_31012024_English_5.7.pdf#page=5)

## Assessment by workload

| Workload | Class | Evidence and remaining question |
|---|---|---|
| Vision inference, object detection and tracking | STRONG EVIDENCE | The packaged hand-detection and keypoint jobs provide an example for a specific object class. No accuracy, latency or on-device execution was measured. |
| Image preprocessing and feature extraction | STRONG EVIDENCE | The Q6 map includes camera/depth preprocessing, corner-tracking and feature-descriptor jobs. The hardware sheet separately identifies a corner detector. The map alone does not specify which steps use that fixed-function block. |
| Small neural networks | STRONG EVIDENCE | A specialized runtime, executable jobs and fixed-size weights ship together. A user-defined model would need a compiler or compatible code generator, an operator mapping and the runtime's buffer contract. |
| Arbitrary tensors and precision | UNKNOWN | The sheet specifies fixed-point throughput. A Q6 depth-processing symbol string at file offset 0x20388 names a Float16 context. Neither observation identifies a general tensor datatype contract, all enabled instructions or the operand widths behind the advertised rate. |
| LLM inference | UNKNOWN | This investigation identified no LLM backend, verified attention implementation, full operator coverage, sustained memory bandwidth or measured host-transfer latency for CVIP. The vendor's peak of 1,700 GOP/s cannot predict tokens per second. |

The next static test is to follow the detection job's resource-list construction through buffer serialization to the task-start call. An end-to-end reconstruction needs the buffer ownership, field widths, transfer direction and completion order. [Host-interface analysis](host-interface.md)
