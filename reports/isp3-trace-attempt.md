# Attempt to recover one recorded Mero memory-input frame

**No pixel frame could be replayed or verified.** The build 9601 factory release contains the ISP software and playback configurations. Across the files inspected, no saved frame-info command had even the external package length required by either shipped firmware. The closest acknowledgement candidate was in Android's framework code and failed the actual [ring decoder](../scripts/decode_isp3_ring.py).

The practical question was whether one recording could show the same input picture reaching the ISP and generating an output. A useful recording would have to preserve the command, the separate frame-information package, evidence identifying the input pixels, and the associated completion. The earlier study established the packet layout and Jupiter's separate power-control limitation. [Starting report](isp3-driver-feasibility.md)

## What the search covered

The reference was Magic Leap OS 1.12.1, build 9601, release archive SHA-256 `9747b3652e20746596b64b0b244bd23a047ba47d4eb3d392271cac08a615f28c`. Counts below describe **overlapping views** of those bytes. A hit at one layer can recur at another. [Release provenance](../evidence/artifacts.md)

| View | Files or entries checked | Outcome |
|---|---:|---|
| Decompressed outer archive | All 60 regular members, 5,460,694,114 bytes, verified against their recorded hashes | 2,118 frame-info ID positions and 2,408 ordinary frame-control ID positions inside complete 64-byte windows. Zero candidates had the matching command-package length. One putative frame-info acknowledgement failed its checksum. |
| Logical files inside the system, vendor, userdata and CVIP read-only filesystems | 6,377 hash-verified regular files, 4,969,835,369 bytes | Zero size-matching commands. Reading logical files separately also avoids missed matches at fragmented ext4 boundaries. None was the size of a standalone ring or slot. The two files with exactly 4,656 or 4,728 bytes were Bionic test libraries. |
| ZIP-family members, including packaged apps and five CVIP models | 225 distinct containers, 39,849 decompressed entries totaling 3,683,737,206 bytes | 511 frame-info ID positions, zero frame-info commands of the required size. The 4,656-byte asset repeated in three apps was a PNG icon. |
| Additional recognized wrappers | 105 UnityFS bundles (139 logical files), eight gzip members, seven APEX filesystems (265 regular files) and seven ZIPs within those APEX filesystems | Zero size-matching commands. No encrypted partition or unrecognized proprietary trace format was decoded. |

The byte scan accepts candidates at any alignment and retains 63 bytes between chunks. It checks ID `0x02050002` at slot offset 4, external length **4,728 or 4,656** at offset 16, then the byte sum at offset 63. The ordinary capture control uses ID `0x02050001` and length 2,640. Acknowledgements are searched independently by response ID, original command ID and checksum. Stream tag and pointer plausibility are not used to discard candidates at this stage. A passing checksum would still require provenance and a separately associated package. [Search tool](../scripts/find_isp3_trace.py) · [Boundary fixtures](../tests/test_find_isp3_trace.py)

**The closest match was tested.** In expanded `system.raw` a 64-byte window at `0x8f6c7596` had the putative acknowledgement ID and original frame-info ID at the expected offsets. Its stored checksum was `0x8c`; the calculated sum was `0xf5`. Running the published decoder returned `slot checksum mismatch`. ext4 block 587463 resolves to inode 4115, `/system/framework/framework.jar`. The same window occurs at offset `0x76a6ca` in its uncompressed ZIP member `classes3.dex`, in the DEX map's class-data region. SHA-256 of the 64-byte window is `40c17e1c02f52d4e43426c074c15b5f7dc237e02fa78279ebe06377f0a9dbb6d`. **DISPROVEN** as an intact R64 acknowledgement. [Android DEX map definitions](https://source.android.com/docs/core/runtime/dex-format)

The eight CVIP playback YAMLs configure the vision engine and refer to external trace or log directories. The factory CVIP writable filesystem contains only a mount marker. The Android sensor-recorder service similarly names a recording directory without supplying an existing frame session. A separate public-source check covered the vendor's C API sample ZIP directory (1,344 entries), all 488 regular files in its OpenXR sample ZIP, and one publicly attached headset log. None supplied a matching run. ML Hub's Capture feature records the visible display. [ML2 C API samples](https://thelab.magicleap.cloud/packages_mlhub/artifacts/com.magicleap.capisamples/1.12.0/sdk_native_samples_src.zip) · [OpenXR samples](https://thelab.magicleap.cloud/packages_mlhub/artifacts/com.magicleap.openxrsamples/1.12.0/openxr_samples_source.zip) · [Headset log source](https://forum.magicleap.cloud/t/issue-with-marker-tracking-app-on-magic-leap-2/4293/1) · [Magic Leap Capture documentation](https://developer-docs.magicleap.cloud/docs/guides/developer-tools/ml-hub-3/ml-hub3-capture/)

## One more link inside the firmware

**STRONG EVIDENCE for a queue-to-scheduler handoff.** In the signed `mero_isp.bin` (SHA-256 `2a8c6ae8b24d2613cf5f862ded9240100b2c3ffedcb4d5b2193fc0eb8e656fb0`), the type-7 event branch at VA `0x60094d9d` takes the item from event offset 4. It computes the same queue location as the one-frame selection routine at `0x600972f8`. At `0x60097360–0x60097365` the latter checks a returned item and inspects its drop field. The queue association is inferred from matching data flow; some bundled Xtensa instructions are configuration-specific. [Image mapping and earlier handoff](../analysis/isp3-memory-input.md)

**CONFIRMED static correlation clue.** At `0x600973aa/0x600973b0`, the scheduler loads a pointer from item offset `0x54` and reads its first dword. The drop diagnostic at `0x600973c5–0x600973ca` identifies that value as the picture-order count (POC). The continuing path checks per-stream state 2 at `0x600973f9`; its alternate diagnostic identifies a stream core that is not running. Rejection paths at `0x6009738b/0x60097416` call the cleanup routine at `0x60096490`, whose `baseFrameInfoPool` release diagnostic appears at `0x60096572–0x60096577`. A future trace can correlate the stream and POC and distinguish a dropped information object from pixel processing. The original source pixel address, a read by the DMA engine, and an output from that frame remain **UNKNOWN**.

## Reproduce

```sh
python3 -B scripts/find_isp3_trace.py --release flash_demophon_aosp-user_10_B3E.251015.01_9601_release-keys.tar.gz
python3 -B -m unittest discover -s tests -q
```

For a saved candidate file, omit `--release`. The search prints counts and up to 20 checksum-passing byte offsets. For a separate memory package, use the existing decoder's `--payload` option. None of these tools follows addresses or submits work. At 08:23 UTC on November 20, 2026, a second read-only check of the owner's Jupiter still showed zero video/media nodes and ten AMDGPU blocks with no ISP. No picture was submitted to the Deck.
