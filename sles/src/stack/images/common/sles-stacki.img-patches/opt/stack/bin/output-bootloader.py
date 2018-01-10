#!/opt/stack/bin/python3 -E
#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import xml.etree.ElementTree as ET
import subprocess
import sys

sys.path.append('/tmp')
from stack_site import attributes

efi = False

efivarsdir = "/sys/firmware/efi"
if os.path.exists(efivarsdir) and os.path.isdir(efivarsdir):
	efi = True

root = ET.Element("bootloader")
root.set('xmlns',"http://www.suse.com/1.0/yast2ns")
root.set("xmlns:config", "http://www.suse.com/1.0/configns")
g  = ET.SubElement(root, "global")

def sles11():
	if efi:
		ET.SubElement(g, 'boot_efilabel').text ="SUSE Linux Enterprise Server 11 SP3" 
		ET.SubElement(g, 'default').text = "linux"
		ET.SubElement(g, 'prompt').text = "true"
		timeout = ET.SubElement(g,"timeout")
		timeout.set("config:type","integer")
		timeout.text = "80"
		
		ET.SubElement(root,'loader_type').text="elilo"

		sections = ET.SubElement(root, 'sections')
		sections.set("config:type","list")
		section = ET.SubElement(sections, "section")
		ET.SubElement(section, "root").text="LABEL=rootfs"
		ET.SubElement(section, "image").text="/boot/vmlinuz"
		ET.SubElement(section, "initrd").text = "/boot/initrd"
		ET.SubElement(section, "initial").text = "1"
		ET.SubElement(section, "name").text = "linux"
		ET.SubElement(section, "type").text = "image"

	else:
		boot = ET.SubElement(g, "boot_mbr")
		boot.set("config:type","boolean")
		boot.text="true"

		ET.SubElement(root, "loader_type").text = "grub"

def sles12():
	if efi:
		ET.SubElement(root, "loader_type").text = "grub2-efi"
	else:
		boot = ET.SubElement(g, "boot_mbr")
		boot.set("config:type","boolean")
		boot.text="true"
		ET.SubElement(root, "loader_type").text = "grub2"

if attributes['os.version'] == "11.x":
	ostype = "sles11"
elif attributes['os.version'] == "12.x":
	ostype = "sles12"
if ostype:
	this = sys.modules[__name__]
	if hasattr(this, ostype):
		f = getattr(this, ostype)
		f()
		print (ET.tostring(root).decode())
