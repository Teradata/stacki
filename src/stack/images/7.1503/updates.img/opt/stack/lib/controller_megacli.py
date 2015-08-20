#!/opt/stack/bin/python

from subprocess import *

class CLI:

	def run(self, args):
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

	def doNuke(self, adapter):
		self.run(['-CfgClr', '-a%d' % adapter])
		self.run(['-CfgForeign', '-Clear', '-a%d' % adapter])
		self.run(['-AdpSetProp', 'BootWithPinnedCache', '1',
			'-a%d' % adapter])

	def getAdapter(self):
		for (k, v) in self.run(['-adpCount']):
			if k == 'Controller Count':
				try:
					controllers = int(v)
					if controllers > 0:
						#
						# '0' is the address of the
						# first controller
						#
						return 0
				except:
					pass
		return None

	def getEnclosure(self, adapter):
		for (k, v) in self.run(['-EncInfo', '-a%d' % adapter]):
			if k == 'Device ID':
				return v

		return None

	def getSlots(self, adapter):
		slots = []
		for (k, v) in self.run(['-PDList', '-a%d' % adapter]):
			if k == 'Slot Number':
				slots.append(int(v))

		return slots

	def doRaid(self, raidlevel, adapter, enclosure, slots, hotspares,
			flags):
		cmd = [ '-CfgLdAdd', '-r%d' % raidlevel ]

		disks = []
		for slot in slots:
			disks.append('%s:%d' % (enclosure, slot))

		cmd.append('[%s]' % ','.join(disks)) 

		if flags:
			cmd.extend(flags)

		if hotspares:
			hs = []
			for hotspare in hotspares:
				hs.append('%s:%d' % (enclosure, hotspare))

			cmd.append('-Hsp[%s]' % ','.join(hs))

		cmd.append('-a%d' % adapter)
		self.run(cmd)

	def doGlobalHotSpare(self, adapter, enclosure, hotspares):
		for hotspare in hotspares:
			cmd = [ '-PDHSP', '-Set', '-PhysDrv',
				'[%s:%d]' % (enclosure, hotspare),
				'-a%d' % adapter ]

			self.run(cmd)

