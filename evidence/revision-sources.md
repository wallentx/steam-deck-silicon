# Hardware compatibility and the 2023 releases

## Device serial and supported OS

**CONFIRMED.** Magic Leap bases its compatibility matrix on characters six and seven of the **device serial number**. Its support article locates that number on the headset under the forehead pad. Android Settings and the ADB device list also report the device serial. These sources identify where to read the compatibility code. Neither identifies a CVIP stepping, compute-pack board revision, or individual part encoded by T2. [Compatibility matrix](https://developer-docs.magicleap.cloud/docs/releases/releases-overview/#hardware-and-software-compatibility-matrix) · [Locating the device serial](https://www.magicleap.care/hc/en-us/articles/6021151517709-Finding-Your-Serial-Number)

| Device serial positions 6-7 | Enterprise minimum | MedTech minimum |
|---|---|---|
| T0, T1 | 1.0.0 | 1.0.0 |
| T2 | 1.3.1 | 1.2.1 |

## Release chronology and identity

| OS | Public release | ML API | Signed public build and incremental | AMD BSP in archive |
|---|---|---:|---|---|
| 1.2.0 | 26 April 2023 | 26 | B3E.230330.11-R.044 / 45 | R50 |
| 1.2.1 | 31 July 2023 | 26 | B3E.230330.11-R.051 / 52 | R50 |
| 1.3.1 | 31 July 2023 | 29 | B3E.230616.02-R.121 / 123 | R53 |

**CONFIRMED.** The July releases were concurrent. The catalog metadata associates both 1.2 releases with the R6 release path and 1.3.1 with R7. Each version has one public firmware artifact in the inspected catalog. Each extracted Android build record identifies the same product (`demophon`), flavor (`demophon_aosp-user`) and release signing tag (`release-keys`). None of the three build records or catalog entries labels its artifact MedTech-only or Enterprise-only. Exclusive edition targeting remains **UNKNOWN**. The support matrix gives minimum compatible versions for the hardware classes. [Release dates and API levels](https://developer-docs.magicleap.cloud/docs/releases/releases-overview/) · [Public firmware metadata ZIP](https://thelab.magicleap.cloud/packages_mlhub/com.magicleap.ml2_firmware.zip) · [Magic Leap's secure-build update table](https://www.magicleap.care/hc/en-us/articles/10731234815757-Magic-Leap-OS-Update-Path)

## Changes Magic Leap attributed to hardware

**CONFIRMED.** The 1.2.1 changelog describes three changes with direct hardware implications. Later headsets could omit the unused **Bend Camera** because the startup code stopped requiring its presence. The display startup sequence also received timing fixes and support for additional factory calibration data. Magic Leap separately reports a Bluetooth manufacturing-yield improvement. The April 1.2.0 notes cover earlier OS features. The July 1.3.1 notes describe a release based on 1.3.0-dev2 and identify the R.121 build. [1.2.1 changes](https://developer-docs.magicleap.cloud/docs/releases/release-2023-july/1.2.1-os-release-notes/) · [1.2.0 notes](https://developer-docs.magicleap.cloud/docs/releases/release-2023-april/os-release-notes/) · [1.3.1 notes](https://developer-docs.magicleap.cloud/docs/releases/release-2023-july/os-release-notes/)

**HYPOTHESIS.** A headset lacking the Bend Camera would explain why previously working boot code needed updating. The release notes do not explicitly map that omission to T2, identify the first serial affected, or attribute the compatibility floor solely to the camera. The published changes provide a concrete alternative to a CVIP silicon revision. Evidence attributing T2 to an AMD silicon change remains **UNKNOWN**. A parts-change order or board-revision document naming T2 and the affected assembly would distinguish those possibilities. [1.2.1 changes](https://developer-docs.magicleap.cloud/docs/releases/release-2023-july/1.2.1-os-release-notes/) · [Compatibility matrix](https://developer-docs.magicleap.cloud/docs/releases/releases-overview/#hardware-and-software-compatibility-matrix)

## Metadata provenance and a release-note discrepancy

The inspected public catalog ZIP has SHA-256 `496d92ef858aa328da44be297048ccac1fff6afcbdcdeb5fc3c5e45c6c524dd7`. Its `ml2_firmware/package.xmi` member has SHA-256 `6997c0af866e7939095a64ee391919652157ba225a305ff838e1bde68d1e20d9`. Each build ID above comes from both that catalog and the archive's build record. [Public catalog](https://thelab.magicleap.cloud/packages_mlhub/com.magicleap.ml2_firmware.zip)

| OS | Local build record | SHA-256 |
|---|---|---|
| 1.2.0 | [build_info.json](https://thelab.magicleap.cloud/packages_mlhub/artifacts/com.magicleap.ml2_firmware/B3E.230330.11-R.044_user_secure/flash_demophon_aosp-user_10_B3E.230330.11-R.044_45_release-keys.tar.gz) | 19214a25610cb780e966fbca927f2c345874f6495fecc30313bc9c68035fddf9 |
| 1.2.1 | [build_info.json](https://thelab.magicleap.cloud/packages_mlhub/artifacts/com.magicleap.ml2_firmware/B3E.230330.11-R.051_user_secure/flash_demophon_aosp-user_10_B3E.230330.11-R.051_52_release-keys.tar.gz) | c0516b0a85b20f6b231b9b30397c2852fcc48494c60a25696826c43e4e33dd19 |
| 1.3.1 | [build_info.json](https://thelab.magicleap.cloud/packages_mlhub/artifacts/com.magicleap.ml2_firmware/B3E.230616.02-R.121_user_secure/flash_demophon_aosp-user_10_B3E.230616.02-R.121_123_release-keys.tar.gz) | 4013218a9d9a29ab8e78d8e8b3c9c9b3de7e06308f33348183474c06c565b8d8 |

**CONFIRMED.** A line-by-line comparison of the 1.2.0 and 1.2.1 HTML notes in the catalog found only one changed line. It updates the first heading from R.044 to R.051 while retaining the April R.044 body. The 1.3.1 catalog notes similarly pair an R.121 heading with an earlier June R.026 heading. The version-specific developer portal changelogs therefore provide the change descriptions above. [Catalog containing the HTML notes](https://thelab.magicleap.cloud/packages_mlhub/com.magicleap.ml2_firmware.zip) · [July release index](https://developer-docs.magicleap.cloud/docs/releases/release-2023-july/july-release-notes/)
