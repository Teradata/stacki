#!/opt/stack/bin/python

from subprocess import *

class CLI:

	def run(self, args):
		cmd = [ '/opt/stack/sbin/MegaCli' ]
		cmd.extend(args)
		file = open('/tmp/MegaCli.log', 'a+')
		file.write('cmd: %s\n' % ' '.join(cmd))
		file.close()
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

		enclosure = self.getEnclosure(adapter)
		for slot in self.getSlots(adapter):
			self.run(['-PDMakeGood', '-PhysDrv',
				"'[%s:%s]'" % (enclosure, slot), '-Force',
				'-a%s' % adapter ])

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

	def doStrippedRaid(self, raidlevel, adapter, enclosure, slots,
			hotspares, flags):

		if raidlevel == '10':
			cmd = [ '-CfgSpanAdd', '-r10' ]
			pdperarray = 2
		elif raidlevel == '50':
			cmd = [ '-CfgSpanAdd', '-r50' ]
			pdperarray = 5
		elif raidlevel == '60':
			cmd = [ '-CfgSpanAdd', '-r60' ]
			pdperarray = 6
		else:
			return

		disks = []
		for slot in slots:
			disks.append('%s:%d' % (enclosure, slot))

		options = []
		for f in flags.split():
			opt = f.split('=')
			if opt[0] == 'pdperarray':
				try:
					pdperarray = int(opt[1])
				except:
					pass
			else:
				options.append(f)

		try:
			numarrays = len(disks) / pdperarray
		except:
			numarrays = 1

		j = 0
		for i in range(0, numarrays, 1):
			d = []
			for k in range(j, j + pdperarray, 1):
				d.append(disks[k])
			j += pdperarray

			cmd.append('-Array%d[%s]' % (i, ','.join(d)))

		cmd.append('-force')
		cmd.append('-a%d' % adapter)

		if options:
			cmd.extend(options)

		self.run(cmd)

		# 
		# support for dedicated hot spares for 10, 50 and 60
		# is convoluted with MegaCLI, so we will only support
		# global hot spares with this.
		# 
		self.doGlobalHotSpare(adapter, enclosure, hotspares,
			' '.join(options))


	def doRaid(self, raidlevel, adapter, enclosure, slots, hotspares,
			flags):

		if not enclosure:
			enclosure = ''

		if raidlevel in [ '10', '50', '60' ]:
			self.doStrippedRaid(raidlevel, adapter, enclosure,
				slots, hotspares, flags)
		else:
			cmd = [ '-CfgLdAdd', '-r%s' % raidlevel ]

			disks = []
			for slot in slots:
				disks.append('%s:%d' % (enclosure, slot))

			cmd.append('[%s]' % ','.join(disks)) 

			if hotspares:
				hs = []
				for hotspare in hotspares:
					hs.append('%s:%d' % (enclosure,
						hotspare))
				cmd.append('-Hsp[%s]' % ','.join(hs))
			if flags:
				cmd.append(flags)

			cmd.append('-force')
			cmd.append('-a%d' % adapter)
			self.run(cmd)


	def doGlobalHotSpare(self, adapter, enclosure, hotspares, flags):
		for hotspare in hotspares:
			cmd = [ '-PDHSP', '-Set', '-PhysDrv',
				'[%s:%d]' % (enclosure, hotspare),
				'-a%d' % adapter ]

			if flags:
				cmd.append(flags)

			self.run(cmd)

