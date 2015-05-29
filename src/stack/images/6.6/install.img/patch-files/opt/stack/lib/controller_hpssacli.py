#!/opt/stack/bin/python

from subprocess import *

class Hpssacli:
	debug = 0

	def hpssacli(self, args):
		cmd = [ '/opt/stack/sbin/hpssacli', 'ctrl' ]
		cmd.extend(args)

		file = open('/tmp/hpssacli.log', 'a')
		file.write('cmd: %s\n' % ' '.join(cmd))

		p = Popen(cmd, stdout=PIPE)
		result = p.stdout.readlines()

		file.write('result:\n')
		for line in result:
			file.write('%s' % line)
		file.write('\n\n')
		file.close()

		return result

	def getAdapter(self):
		result = self.hpssacli([ 'all', 'show' ])
		for line in result:
			tokens = line[:-1].split()
			if len(tokens) < 1:
				continue

			#
			# look for 'Slot' in output
			#
			i = None
			try:
				i = tokens.index('Slot')
			except:
				continue

			if i != None and len(tokens) > i + 1:
				#
				# the slot value is the first token after
				# 'Slot' in the result.
				#
				# make sure it is an integer
				#
				slot = None
				try:
					slot = int(tokens[i + 1])
				except:
					pass

				if slot != None:
					return slot
			
		#
		# couldn't find the adapter
		#
		return None

	def getEnclosure(self, adapter, slot=None):
		#
		# the enclosure id is a combination of the 'port' and 'box'
		#
		result = self.hpssacli([ 'slot=%d' % adapter, 'physicaldrive',
			'all', 'show' ])
		for line in result:
			tokens = line[:-1].split()
			if len(tokens) < 1:
				continue

			if tokens[0] != 'physicaldrive' and len(tokens) < 2:
				continue

			addr = tokens[1].split(':')
			if len(addr) != 3:
				continue

			port = addr[0]
			box = addr[1]
			bay = addr[2]

			try:
				bay = int(bay)
				if slot and slot == bay:
					return '%s:%s' % (port, box)
			except:
				pass
			
		#
		# couldn't generate an 'enclosure' address
		#
		return None

	def getSlots(self, adapter):
		slots = []

		#
		# the slots are the 'bay' value
		#
		result = self.hpssacli([ 'slot=%d' % adapter, 'physicaldrive',
			'all', 'show' ])
		for line in result:
			tokens = line[:-1].split()
			if len(tokens) < 1:
				continue

			if tokens[0] != 'physicaldrive' and len(tokens) < 2:
				continue

			addr = tokens[1].split(':')
			if len(addr) != 3:
				continue

			port = addr[0]
			box = addr[1]
			bay = addr[2]

			slot = None
			try:
				slot = int(bay)
				slots.append(slot)
			except:
				continue

		return slots

	def getArrays(self, adapter):
		#
		# return a list of the currently configured arrays
		#
		arrays = []

		result = self.hpssacli([ 'slot=%d' % adapter, 'show',
			'config' ])
		for line in result:
			tokens = line[:-1].split()
			if len(tokens) < 2:
				continue

			#
			# look for 'array' in output
			#
			if tokens[0] == 'array':
				arrays.append(tokens[1])

		return arrays

	def doNuke(self, adapter):
		result = self.hpssacli([ 'slot=%d' % adapter, 'delete',
			'forced', 'override' ])

	def doRaid(self, raidlevel, adapter, enclosure, slots, hotspares,
			flags):

		drives = []
		for slot in slots:
			#
			# lookup the enclosure
			#
			enclosure = self.getEnclosure(adapter, slot)
			drives.append('%s:%d' % (enclosure, slot))

		if not drives:
			return

		if hotspares:
			#
			# if there are hotspares, need to first get the list
			# of all currently configured arrays so we can do
			# a 'diff' after we create the new array so we can
			# add the hotspares to the newly configured array. 
			#
			prearrayids = self.getArrays(adapter)

		cmd = [ 'slot=%d' % adapter, 'create',
			'type=logicaldrive', 'drives=%s' % ','.join(drives),
			'raid=%d' % raidlevel ]

		if flags:
			cmd.extend(flags)

		result = self.hpssacli(cmd)

		if hotspares:
			#
			# if there is a hot spare associated with this RAID,
			# then determine the name of the new array, then add
			# the hotspare to it
			#
			postarrayids = self.getArrays(adapter)

			arrayid = None
			for a in postarrayids:
				if a not in prearrayids:
					arrayid = a
					break

			if arrayid:
				spares = []
				for slot in hotspares:
					enclosure = self.getEnclosure(
						adapter, slot)
					spares.append('%s:%d' %
						(enclosure, slot))

				cmd = [ 'slot=%d' % adapter, 'array', arrayid,
					'add', 'spares=%s' % ','.join(spares) ]
				result = self.hpssacli(cmd)

	def doGlobalHotSpare(self, adapter, enclosure, hotspares):
		spares = []
		for slot in hotspares:
			enclosure = self.getEnclosure(adapter, slot)
			spares.append('%s:%d' % (enclosure, slot))

		cmd = [ 'slot=%d' % adapter, 'array', 'all', 'add',
			'spares=%s' % ','.join(spares) ]
		result = self.hpssacli(cmd)

