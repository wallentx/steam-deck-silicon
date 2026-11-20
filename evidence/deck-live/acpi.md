# Raw ACPI follow-up on Valve Jupiter

The capture contains one DSDT and twelve SSDTs. All 13 files matched the SHA-256 manifest from the Deck. Each also passed its ACPI header length and byte checksum. ACPICA iASL 20251212 disassembled every table individually. Joint disassembly reported duplicate namespace objects, so the scope observations below use the individual disassemblies and the earlier live sysfs inventory.

The DSDT defines GP18 at device 8, function 2 and gives it a single device child, SATA, at downstream device 0, function 0. SSDT3 extends the SATA scope with PRT0. No other SSDT refers to GP18 by name. None of the 13 disassemblies contains CVIP, CVPE, AMDI0068 or the literal 0x149D. The baseline PCI capture independently found zero AMD 1022:149d endpoints among 30 readable functions. These observations establish that this Jupiter boot lacks the Mero-style GP18.CVIP namespace entry and enumerated PCI function. Physical silicon presence remains unknown.

The disassembly locates GP18 at DSDT line 3584, SATA at line 3708 and the SATA scope at SSDT3 line 25. [Table hashes](aml-hashes.txt) · [Live PCI capture](pci.md)
