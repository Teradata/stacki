# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
import os
import sys
import string
from stack.bool import *
from subprocess import *

def megacli(args):
	cmd = [ '/opt/stack/sbin/MegaCli' ]
	cmd.extend(args)
	cmd.extend(['-AppLogFile','/tmp/MegaCli.log'])

	result = []
	p = Popen(cmd, stdout=PIPE)
	for line in p.stdout.readlines():
		tokens = line[:-1].split(':', 1)
		if len(tokens) != 2:
			continue
		(k, v) = tokens
		k = k.strip()
		v = v.strip()
		if len(v) and v[-1] == '.':
			v = v[:-1]
		result.append((k,v))
	return result


def numAdapters():
	"""
	Return the number of MegaRAID adapters found on
	the system.
	"""

	for (k, v) in megacli(['-adpCount']):
		if k == 'Controller Count':
			return int(v)
	return 0


def diskInfo(adapter):
	"""
	Returns a list of physical drives
	id - bus number
	size - raw size
	vendor - raw vendor info
	"""
	
	list = []
	disk = None
	for (k, v) in megacli(['-PDList', '-a%s' % adapter]):
		if k == 'Enclosure Device ID':
			if disk:
				list.append(disk)
			disk = {}
			disk['enclosure'] = int(v)
		if k == 'Slot Number':
			disk['id'] = int(v)
		elif k == 'Raw Size':
			disk['size'] = v
		elif k == 'Inquiry Data':
			disk['vendor'] = v
	if disk:
		list.append(disk)

	return list


def volumeInfo(adapter):
	list = []
	volume = None
	for (k, v) in megacli(['-LdPdInfo', 'a%s' % adapter]):

		if k == 'Virtual Drive':
			if volume:
				list.append(volume)
			volume = {}
			volume['id'] = int(v.split()[0])
			volume['disks'] = []
			disk = None
		elif k == 'RAID Level':
			volume['type'] = v
		elif k == 'Size':
			volume['size'] = v
		elif k == 'Slot Number':
			disk = {}
			disk['id'] = int(v)
		elif k == 'Raw Size':
			disk['size'] = v
		elif k == 'Inquiry Data':
			disk['vendor'] = v
			volume['disks'].append(disk)

	if volume:
		list.append(volume)
		
	return list


def isMegaRAID():
	if os.system('lspci | fgrep LSI | fgrep MegaRAID > /dev/null') == 0:
		return 1
	return 0


def doNuke():
	for i in range(0, numAdapters()):
		megacli(['-CfgClr', '-a%d' % i])
		megacli(['-CfgForeign', '-Clear', '-a%d' % i])
		megacli(['-AdpSetProp', 'BootWithPinnedCache', '1', '-a%d' % i])


def getDisks():
	disk = {}
	for i in range(0, numAdapters()):
		if not volumeInfo(i):
			for d in diskInfo(i):
				disk['%d:%d' % (d['enclosure'], d['id'])] = (d['size'], d['vendor'])

	return disk


def doBootDisk(disk, bootdisk0, bootdisk1, mcliflags):
	if not bootdisk0:
		return

	for i in range(0, numAdapters()):
		if bootdisk0 in disk.keys() and bootdisk1 in disk.keys():
			print 'create boot volume (%s,%s)' % (bootdisk0,
				bootdisk1)
			cmd = ['-CfgLdAdd', '-r1', 
				'[%s, %s]' % (bootdisk0, bootdisk1)]
			cmd.extend(mcliflags)
			cmd.append('-a%d' % i)
			megacli(cmd)
			del disk[bootdisk0]
			del disk[bootdisk1]
		elif bootdisk0 in disk.keys():
			print 'create boot volume (%s)' % bootdisk0
			cmd = ['-CfgLdAdd', '-r0', '[%s]' % bootdisk0]
			cmd.extend(mcliflags)
			cmd.append('-a%d' % i)
			megacli(cmd)
			del disk[bootdisk0]

		if bootdisk0 in disk.keys():
			cmd = ['-AdpBootDrive', '-Set',
				'-L0', '-a%d' % i]
			megacli(cmd)

	return disk


def doDefaultDataDisks(disk, mcliflags):
	for i in range(0, numAdapters()):
		for d in diskInfo(i):
			key = '%d:%d' % (d['enclosure'], d['id'])
			if key in disk.keys():
				cmd = ['-CfgLdAdd', '-r0', '[%s]' % key]
				cmd.extend(mcliflags)
				cmd.append('-a%d' % i)
				megacli(cmd)

				del disk[key]

