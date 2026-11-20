"""Annotate host search leads. The reasons are scoped to this build."""
import csv
import pathlib
import re
import subprocess
import sys

work, index = map(pathlib.Path, sys.argv[1:])
rules = [
    (r'^boot/(kernel|vmlinux)$', 'CONFIRMED', 'Compiled CVIP PCI, XPC, MLNET and shared region drivers', 'Check CVIP PCI registration and PL320 call sites'),
    (r'/modules\.builtin(\.modinfo)?$', 'CONFIRMED', 'Compiled-in module manifest lists CVIP subsystems', 'Compare with executable kernel'),
    (r'mero_cvip_thermal\.ko$', 'CONFIRMED', 'ACPI thermal driver AMDI0068', 'Separate temperature monitoring from PCI discovery'),
    (r'lib64/(cvcorelib|shregion|meronotifier|cvip_component|gsmshared|cvcoreinit)\.so$', 'CONFIRMED', 'Vendor cross-core runtime and synchronization family', 'Inspect exported symbols and caller dependencies'),
    (r'/(nbd_server|nbd-config|cvipsysfsmonitor|cvip-monitor|sysfs_property_config)$|/init/(cvipsysfsmonitor|cvip-monitor|nbd_server).*\.rc$', 'CONFIRMED', 'Host startup, state reporting or remote storage', 'Correlate state transitions with A55 boot services'),
    (r'ueventd\.(mero|demophon)\.rc$', 'CONFIRMED', 'Device rules name the shared-region and notifier nodes', 'Trace the device owners'),
    (r'/ACPI/5.raw$|/demophon_bios\.FD$', 'CONFIRMED', 'CVIP device node in platform firmware', 'Compare GP18 child AML and PCI inventory'),
    (r'flashall_amd\.(sh|bat)$|demophon_gpt.bin$', 'CONFIRMED', 'Release partition mapping', 'Compare labels with bootloader diagnostics'),
    (r'/Linux/cvip/dsp/|/Linux/bootdr.py$', 'CONFIRMED', 'Vendor diagnostic source describes target DSPs or boot events', 'Read the diagnostic source as text'),
    (r'/(cvip_.*hbin|Imagea55.*|rootfs.cpio.lzo.hbin|cbl_a55.bin.hbin|ml-mero-cvip.*|oem.bin.hbin)$', 'CONFIRMED', 'CVIP-side artifact in flash group', 'See firmware.md for wrapper and payload attribution'),
    (r'firmware/amdgpu/mero_(isp|vcn|sdma|dmcub|mec|ce|me|gpu_info|asd|ta|rlc|pfp|toc)', 'CONFIRMED', 'AMDGPU-family asset, distinct from C5/Q6 service binaries', 'Use named block for functional attribution'),
    (r'\.tflite$', 'UNKNOWN', 'Android model asset, CVIP execution unverified', 'Trace actual runtime backend before attributing inference'),
    (r'cviploginproxy|cvippowermanager|cvipbridge|libmlnet|/usemlnet$|/bugreport_cvip|/cvip_milestones', 'STRONG EVIDENCE', 'Named host integration, networking, or diagnostic client', 'Inspect service dependencies and provider'),
]
rules = [(re.compile(p,re.I),a,b,c) for p,a,b,c in rules]
out=csv.writer(sys.stdout,delimiter='\t',lineterminator='\n')
out.writerow(['path','file_type','sha256','classification','evidence','next_inspection'])
with index.open() as f:
    for row in csv.DictReader(f,delimiter='\t'):
        p=row['path']
        tag=next(((a,b,c) for pat,a,b,c in rules if pat.search(p)),None)
        if tag is None and row['keyword_tier']!='specific':
            continue
        if tag is None:
            tag=('UNKNOWN','Search term in path or file; direct CVIP role unestablished','Compare owner, imports and xrefs before attribution')
        desc=subprocess.check_output(['file','-b','--',work/p],text=True).strip()
        out.writerow([p,desc,row['sha256'],*tag])
