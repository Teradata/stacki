#!/opt/stack/bin/python3

import subprocess

class CLI:

	setparams = [ 'rw', 'ro', 'blocked', 'removeblocked', 'wt',
		'wb', 'forcedwb', 'immediate', 'ra', 'nora', 'adra', 'dsblpi',
		'cached', 'direct', 'endskcache', 'disdskcache',
		'cachedbadbbu', 'nocachedbadbbu' ]

	def run(self, args, check=False):
		'''
		check=False was added to allow this subprocess wrapper to halt the install on error.
		currently, only commands related to creating RAID volumes will ever have check=True
		other commands may be expected to fail
		'''

		cmd = [ '/opt/stack/sbin/MegaCli' ]
		cmd.extend(args)
		with open('/tmp/MegaCli.log', 'a+') as fi:
			fi.write('cmd: %s\n' % ' '.join(cmd))
		cmd.extend(['-AppLogFile','/tmp/MegaCli.log'])

		result = []

		p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', check=check)

		for line in p.stdout.splitlines():
			tokens = line.split(':', 1)
			if len(tokens) != 2:
				continue
			(k, v) = tokens
			k = k.strip()
			v = v.strip()
			if len(v) and v[-1] == '.':
				v = v[:-1]
			result.append((k,v))
		return result

	def doNuke(self, enclosure, adapter):
		self.run(['-CfgClr', '-a%d' % adapter])
		self.run(['-CfgForeign', '-Clear', '-a%d' % adapter])
		self.run(['-AdpSetProp', 'BootWithPinnedCache', '1',
			'-a%d' % adapter])

		if not enclosure:
			enclosure = self.getEnclosure(adapter)

		for slot in self.getSlots(adapter):
			self.run(['-PDMakeGood', '-PhysDrv',
				"'[%s:%s]'" % (enclosure, slot), '-Force',
				'-a%s' % adapter ])

	def doSecureErase(self, enclosure, adapter, slot):
		self.run(['-PDInstantSecureErase', '-PhysDrv',
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

	def doStrippedRaid(self, raidlevel, adapter, enclosure, slots, hotspares, flags, check):

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
			numarrays = int(len(disks) / pdperarray)
		except:
			numarrays = 1

		j = 0
		for i in range(0, numarrays, 1):
			d = []
			for k in range(j, j + pdperarray, 1):
				d.append(disks[k])
			j += pdperarray

			cmd.append('-Array%d[%s]' % (i, ','.join(d)))

		setpropflags = []
		for f in options:
			#
			# remove the '-' if present in the flag/option
			#
			g = f.replace('-', '')
			if g.lower() in self.setparams:
				setpropflags.append(f)
			else:
				cmd.append(f)

		cmd.append('-force')
		cmd.append('-a%d' % adapter)
		results = self.run(cmd, check=check)

		#
		# apply any flags that are not able to be set in
		# the -CfgSpanAdd command
		#
		vid = None
		for k,v in results:
			value = v.split('Created VD')
			if len(value) == 2:
				try:
					vid = int(value[1])
					break
				except:
					vid = None

		if vid:
			for f in setpropflags:
				cmd = [ '-LDSetProp', f, '-L%d' % vid, 
					'-a%d' % adapter ]
				results = self.run(cmd, check=check)

		# 
		# support for dedicated hot spares for 10, 50 and 60
		# is convoluted with MegaCLI, so we will only support
		# global hot spares with this.
		# 
		self.doGlobalHotSpare(adapter, enclosure, hotspares,
			' '.join(options))


	def doRaid(self, raidlevel, adapter, enclosure, slots, hotspares, flags, check):

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

			setpropflags = []
			if flags:
				for f in flags.split():
					#
					# remove the '-' if present in the
					# flag
					#
					g = f.replace('-', '')
					if g.lower() in self.setparams:
						setpropflags.append(f)
					else:
						cmd.append(f)

			cmd.append('-force')
			cmd.append('-a%d' % adapter)
			results = self.run(cmd, check=check)

			#
			# apply any flags that are not able to be set in
			# the -CfgLdAdd command
			#
			vid = None
			for k,v in results:
				value = v.split('Created VD')
				if len(value) == 2:
					try:
						vid = int(value[1])
						break
					except:
						vid = None

			for f in setpropflags:
				cmd = [ '-LDSetProp', f, '-L%d' % vid, 
					'-a%d' % adapter ]
				results = self.run(cmd, check=check)


	def doGlobalHotSpare(self, adapter, enclosure, hotspares, flags, check):
		for hotspare in hotspares:
			cmd = [ '-PDHSP', '-Set', '-PhysDrv',
				'[%s:%d]' % (enclosure, hotspare),
				'-a%d' % adapter ]

			if flags:
				cmd.append(flags)

			self.run(cmd, check=check)

if __name__ == '__main__':
	s = CLI()
	a = s.getAdapter()
	if a is not None:
		print(s.getEnclosure(a))
		print(s.getSlots(a))
