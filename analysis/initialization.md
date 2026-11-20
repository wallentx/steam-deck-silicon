# Initialization and readiness

ML2 provisions several boot partitions before Android starts. The vendor flashing script describes their destinations. Its command order describes provisioning only. The host BIOS and downstream kernel code provide separate evidence for the boot sequence. [Partition map](../evidence/firmware.md)

```text
NVMe CVIP partitions
  -> BIOS ABL partition lookup and image copy        [static firmware evidence]
  -> CBL / A55 kernel / DTB / initial RAM filesystem [partition roles known]
  -> CVIP-side platform ready notification           [vendor kernel source]
                    |
Android x86 PCI probe, MSI-X and mailbox controller
  -> CVIP alive handling, transport buffer mapping and registration
  -> XPC/MLNET state and Android service readiness
  -> RO/RW storage exports and vision runtime        [configuration and binaries]
```

The two sides can progress concurrently. The diagram shows dependencies. It cannot establish a boot-time ordering between the host PCI probe and each A55 startup step.

1. **CONFIRMED.** The Mero BIOS holds a second-level PSP directory at 0x100000. Its type 0x30 entry points to file offset 0x1d5200, length 0xe7850. Within this entry, the diagnostic at 0x1fcac5 identifies an ABL CVIP partition lookup. Other diagnostics describe an NVMe lookup, a destination FMR address, and completion of an image copy. The byte-identical evidence can be checked with the [offline verifier](../scripts/check-host-identifiers.py).
2. **STRONG EVIDENCE.** These bootloader diagnostics, separate signed/encrypted-format boot files and the A55 userspace together implicate board firmware and a distinct CVIP boot environment. Coreboot documents that AMD ABLs execute on the PSP. Public AMD release notes also describe a CVIP firmware-load interface, SRAM initialization, power-on handling and release from reset. The exact decision path, key selection, reset owner and handoff address for build 9601 remain UNKNOWN. [Coreboot PSP integration](https://doc.coreboot.org/soc/amd/psp_integration.html) · [AMD PSP release history](https://chromium.googlesource.com/chromiumos/third_party/coreboot/amd_blobs/+/8d9190d5a70c46dda257fa71210a77f0559ee56a/cezanne/PSP/PSP_ReleaseNotes.txt)
3. **CONFIRMED.** The ML2 x86 PCI probe sets up MMIO, MSI-X, mailboxes, IOMMU information and misc devices. Its alive-handling function calls ipc_init, ipc_sendmsg and cvip_reg_buf. The public CVIP-side platform probe registers notifiers and conditionally calls send_cvip_alive. This vendor source predates the image. Cross-side pairing is STRONG EVIDENCE rather than a recorded boot trace. [Host interface](host-interface.md) · [Vendor source](../evidence/source-references.md)
4. **CONFIRMED.** Android starts cvip-monitor, cvipsysfsmonitor and nbd_server on early-fs. Its property map considers XPC connected at MODULES_LOADED and enables init.cvip.start only at OPERATIONAL. Other named states include OFFLINE, INITIALIZING, NETWORK_READY and BOOT_VERIFIED. Android exports the slot-aware, read-only CVIP partition, a writable partition, DSP properties, and read-only calibration. The state labels establish the software contract. They do not independently verify a successful cryptographic check. [Build files and hashes](../evidence/host-index.tsv)
5. **CONFIRMED.** The RO image holds an AArch64 service stack plus DSP applications and job descriptors for C5 and Q6. The service implementation contains load, task creation and start paths. The exact first instruction of the A55 boot components, the live state of each core and a user-supplied standalone boot remain UNKNOWN. [Firmware loading](firmware-loading.md) · [Workload evidence](architecture.md)
