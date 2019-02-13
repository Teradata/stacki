#!/opt/stack/bin/python3

# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import sys
import os
import subprocess

# Check if we are running in efi mode
if not os.path.isdir('/sys/firmware/efi'):
	sys.exit()

# Parse the UEFI bootorder and put the installation network as
# the first boot device. We store this in /opt/stack/etc/uefi_netboot
netbootfile = '/opt/stack/etc/uefi_netboot'
if not os.path.isfile(netbootfile):
	sys.exit()

f = open(netbootfile, 'r')
netboot = f.read().strip()

# get the current EFI boot order
efi_proc = subprocess.Popen(['/usr/sbin/efibootmgr'],
	stdout=subprocess.PIPE)
out, err = efi_proc.communicate()

for line in out.splitlines():
	line = line.decode()
	if line.startswith('BootOrder: '):
		boot_order = line.strip().replace('BootOrder: ', '')
		boot_order = boot_order.split(',')
		break

b = boot_order.index(netboot)
if b >= 0:
	boot_order.pop(b)
boot_order.insert(0, netboot)
subprocess.call(['/usr/sbin/efibootmgr', '--bootorder', ','.join(boot_order)])
subprocess.call(['/usr/sbin/efibootmgr', '--bootnext', netboot])
