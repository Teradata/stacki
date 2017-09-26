#!/opt/stack/bin/python3

import subprocess
import json
import re

class CLI:

	def run(self, args, json_out = False):
		cmd = [ '/opt/stack/sbin/storcli' ]
		cmd.extend(args)
		try:
			if args.index('show') >= 0:
				json_out = True
		except ValueError:
			pass

		if json_out:
			cmd.append('J')

		f = open('/tmp/MegaSAS.log','a')
		f.write('cmd: %s\n\n'  % ' '.join(cmd))
		p = subprocess.run(cmd, stdout=subprocess.PIPE)
		o = p.stdout.decode()
		f.write('%s\n\n' % o)
		f.close()
		if json_out:
			j = json.loads(o)
			result = j['Controllers'][0]
		else:
			result = {}
			for line in o.splitlines():
				line = line.strip()
				tokens = line.split('=')
				if len(tokens) < 2:
					continue
				k = tokens[0].strip()
				v = '='.join(tokens[1:])
				v = v.strip()
				if len(v) and v[-1] == '.':
					v = v[:-1]
				result[k] = v
		return result

	def doNuke(self, enclosure, adapter):
		self.run(['/c%d/vall' % adapter, 'delete', 'force'])
		self.run(['/c%d/fall' % adapter, 'delete'])
		self.run(['/c%d' % adapter, 'set', 'jbod=off', 'force'])
		self.run(['/c%d' % adapter, 'set', 'bootwithpinnedcache=on'])

		if enclosure:
			adapteraddress = '/c%d/e%d' % (adapter, enclosure)
		else:
			adapteraddress = '/c%d' % adapter

		for slot in self.getSlots(adapter):
			self.run(['%s/s%d' % (adapteraddress, slot),
				'set', 'good', 'force'])

	def doSecureErase(self, enclosure, adapter, slot):
		if enclosure:
			slotaddress = '/c%d/e%d/s%d' % \
				(adapter, enclosure, slot)
		else:
			slotaddress = '/c%d/s%d' % (adapter, slot)

		self.run([slotaddress, 'secureerase', 'force'])

	def getAdapter(self):
		res = self.run(['show', 'ctrlcount'])
		if res['Command Status']['Status'] == 'Failure':
			return None
		c = int(res['Response Data']['Controller Count'])
		if c > 0:
			return 0
		return None

	def getEnclosure(self, adapter):
		res = self.run(['/c%d/eall' % adapter,'show'])
		eid = None
		try:
			eid = int(res['Response Data']['Properties'][0]['EID'])
			# Check to make sure there are actually disks
			# connected to the enclosure. If not return eid
			# as none
			o = self.run(['/c%d/e%d/sall' % (adapter, eid),'show'])
			if o['Command Status']['Status'] == 'Failure':
				eid = None
		except:
			pass

		return eid

	def getSlots(self, adapter):
		slots = []
		res = self.run(['/c%d/sall' % adapter, 'show'])
		if res['Command Status']['Status'] == 'Failure':
			eid = self.getEnclosure(adapter)
			if eid:
				res = self.run([
					'/c%d/e%d/sall' % (adapter, eid),
					'show'])

		if res['Command Status']['Status'] == 'Success':
			for disk in res['Response Data']['Drive Information']:
				d = disk["EID:Slt"]
				e,s = d.split(":")
				slots.append(int(s))

		return slots

	def doRaid(self, raidlevel, adapter, enclosure, slots, hotspares,
			flags):
		args = ['/c%d' % adapter, 'add','vd',
			'type=r%s' % raidlevel]

		# Check to see if size argument is present
		# in flags. If it is, it MUST BE added
		# immediately after the type=raidtype argument
		# The size=<vd size> is a positional argument
		# and will fail if it's in any other location
		if flags:
			f = flags.split()
			size_re = re.compile("^size=")
			size_idx = -1
			found = False
			for flag in f:
				size_idx = size_idx + 1
				if size_re.match(flag.lower()):
					found = True
					break
			if found:
				size_arg = f.pop(size_idx)
				args.append(size_arg)

		disks = []
		for slot in slots:
			if enclosure:
				disks.append('%s:%d' % (enclosure, slot))
			else:
				disks.append('%s' % slot)
		args.append('drives=%s' % ','.join(disks))
		if flags:
			args.extend(f)

		# For Striped Raid sets, add a sensible
		# pdperarray= argument if one isn't present.
		if raidlevel in ['10','50','60']:
			try:
				flags.index('pdperarray=')
			except:
				if raidlevel == '10':
					args.append('pdperarray=2')
				if raidlevel == '50':
					args.append('pdperarray=3')
				if raidlevel == '60':
					args.append('pdperarray=4')

		if hotspares:
			hs = []
			for hotspare in hotspares:
				if enclosure:
					hs.append('%s:%d' % (enclosure, hotspare))
				else:
					hs.append('%d' % hotspare)
	

			args.append('spares=%s' % ','.join(hs))

		args.append('force')
		self.run(args)

	def doGlobalHotSpare(self, adapter, enclosure, hotspares, options):
		if enclosure:
			loc = '/c%d/e%d' % (adapter, enclosure)
		else:
			loc = '/c%d' % adapter

		for hotspare in hotspares:
			args = ['%s/s%d' % (loc, hotspare), 'add','hotsparedrive']
			if options:
				f = options.split()
				args.extend(f)
			self.run(args)


if __name__ == '__main__':
	s = StorCLI()
	a = s.getAdapter()
	if a is not None:
		print(s.getEnclosure(a))
		print(s.getSlots(a))
