# Archive provenance and coverage

The local input is `flash_demophon_aosp-user_10_B3E.251015.01_9601_release-keys.tar.gz`. It contains 2,603,628,990 bytes. The SHA-256 computed before extraction matches the release catalog. The original was opened read-only. [Hub catalog](https://thelab.magicleap.cloud/packages_mlhub/packages.json) · [Firmware metadata archive](https://thelab.magicleap.cloud/packages_mlhub/com.magicleap.ml2_firmware.zip) · [Original image](https://thelab.magicleap.cloud/packages_mlhub/artifacts/com.magicleap.ml2_firmware/B3E.251015.01_user_secure/flash_demophon_aosp-user_10_B3E.251015.01_9601_release-keys.tar.gz)

| Algorithm | Whole-archive digest |
|---|---|
| SHA-256 | `9747b3652e20746596b64b0b244bd23a047ba47d4eb3d392271cac08a615f28c` |
| BLAKE2b-512 | `428db50f4fbff85db247ca2b29ccd02d70de7030f8bd0af3ee9e257ff12f4452666da056d00bf83c45ccc7fb7129883a543f30c2e281594c94393632c1730622` |

The gzip-compressed tar contains 60 regular files below one demophon build directory. The build metadata reports Android 10 (API 29), Magic Leap OS 1.12.1, build B3E.251015.01 incremental 9601, AMD BSP R64, user/release-keys, and A/B updates. The product is demophon. The archive is a fastboot provisioning bundle with per-partition images and host utilities. Its member list contains no payload.bin, super.img or vendor_boot.img. The partition template includes NVMe A/B labels for Android and CVIP. The archive is not a whole-disk byte image. [Full file index](host-index.tsv) · [Partition roles](firmware.md)

| Component | Inspected format and scope |
|---|---|
| Android boot | boot.img uses Android header v0, a 2,048-byte page, an 11,988,000-byte x86 bzImage and a 7,561,941-byte compressed ramdisk. The kernel identifies as 5.4.19-android-x86_64. Its uncompressed ELF has SHA-256 f8891033b1f3b9cf9f25ef76d914173f1d43ff9a75df6764982207f0bd84f642. Kallsyms recovery located 55,397 symbols. The ramdisk contains 208 regular entries, including a byte-identical copy of the remote RW image. [Member names](host-ramdisk-paths.txt) |
| Android partitions | Android sparse v1 decodes to ext4. The logical sizes for system, vendor, userdata and cache are 8 GiB, 2 GiB, 20 GiB and 64 MiB respectively. Regular-file extraction returned 4,624, 1,245, 282 and zero files respectively. The vendor inventory includes 485 loadable kernel modules. |
| Boot verification | avbtool identifies SHA256_RSA4096 in vbmeta, a SHA-256 boot hash descriptor and SHA-1 system/vendor hashtree descriptors. These describe Android AVB. The CVIP boot-wrapper headers and remote RO verity data require separate analysis. [CVIP firmware](firmware.md) |
| Early firmware | The archive includes two 16 MiB BIOS variants, a FAT32 capsule with OtaCapsule.cap, and a FAT embedded-controller image. The regular BIOS yielded a UEFI volume at 0x580000, a DSDT, and independently parsed AMD bootloader data outside that volume. The MCU metadata identifies STM32L4A6 build EC2-1865_REL. The SSC BIOS was indexed but its nested volumes were not independently decompiled. |
| CVIP | Five boot blobs have AMD headers. Three other .hbin files are readable Android sparse images. The RO image yielded 226 files, including four DSP programs and four profiling tables, AArch64 ELFs, weights and typed job maps. The RW image contains one regular file. [243 artifact records](cvip-side.tsv) |

## Search and attribution

The [host index](host-index.tsv) contains 6,612 rows from the package, decoded host partitions, ramdisk, BIOS volume and kernel work files. Each row records a SHA-256, size, format indicator, ELF machine where applicable, and a keyword-search tier. Search covered both names and binary contents. Of these entries, 355 matched the more specific terms, 2,839 matched only broad terms, and 3,418 matched neither tier. These counts include nested and derived representations of the same data. Reviewing the central directories of 220 APK/JAR/APEX/ZIP containers found no additional member names matching the selected CVIP/XPC/shared-region terms. That pass did not reverse-engineer all DEX methods or scan every compressed member's contents.

The [host candidate table](host-candidates.tsv) records exact paths, file types, hashes, interpretation and a next inspection for 390 files. It includes additional controls such as Android models and AMDGPU firmware. Generic ML, ISP, VCN, DSP or Mero strings are insufficient for device attribution. The [CVIP-side inventory](cvip-side.tsv) records the separate embedded filesystem. Documentation uses the work-tree paths for extracted files. For example, `system/system/lib64` represents `/system/lib64` on the Android device.

| Host artifact | Evidence | Classification and next check |
|---|---|---|
| boot/vmlinux and vendor modules.builtin | The PCI registration points to cvip, its ID table and probe. The manifest lists the linked-in mailbox, XPC, GSM, MLNET and shregion implementations. | CONFIRMED host drivers. Decode the transport structures against matching vendor sources. |
| system/system/lib64/cvcorelib.so, shregion.so, gsmshared.so, meronotifier.so | Dynamic dependencies, mapping and notification symbols connect these x86 libraries. The binaries expose separate DSP VA, IOVA and DMA accessors. | CONFIRMED cross-core runtime. Follow buffer handoff in one known job. |
| system/system/etc/cvip/sysfs_property_config, etc/init and etc/nbd-config | Android maps state labels to properties, starts the monitoring services and exports the CVIP filesystem. | CONFIRMED integration. Compare with a legitimate ML2 boot log if one becomes available. |
| vendor thermal module and camera/sensor HAL | The thermal module matches AMDI0068. The sensor service requests shregion, notifier and GSM groups. The ISP path contains CVIP camera messages. | CONFIRMED telemetry/consumer evidence. These clients have different roles from the primary PCI driver. |
| vendor/lib/firmware/amdgpu/mero_*.bin and Android .tflite files | AMDGPU labels identify separate graphics, multimedia and ISP firmware. The Android models lack a demonstrated path to the DSP loader. | CVIP attribution is UNKNOWN for the Android models. The demonstrated inference example comes from the CVIP RO filesystem. |

The working filesystem had 268 GiB free before extraction. Static analysis used host tools to decode files and omitted executable permissions on extracted package members. No bundled tool, DSP code or firmware image was executed. The evidence describes shipped software and published observations. It does not measure the live electrical state of either target.
