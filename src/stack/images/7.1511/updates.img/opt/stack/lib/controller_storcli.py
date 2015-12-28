#!/opt/stack/bin/python

from __future__ import print_function
from subprocess import *
import json

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
		p = Popen(cmd, stdout=PIPE)
		o, e = p.communicate()
		f.write('%s\n\n' % o)
		f.close()
		if json_out:
			j = json.loads(o)
			result = j['Controllers'][0]
		else:
			result = {}
			for line in o.split('\n'):
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

	def doNuke(self, adapter):
		self.run(['/c%d/vall' % adapter,'delete', 'force'])
		self.run(['/c%d/fall' % adapter,'delete'])
		self.run(['/c%d' % adapter, 'set', 'jbod=off'])
		self.run(['/c%d' % adapter, 'set', 'bootwithpinnedcache=on'])

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
		for disk in res['Response Data']['Drive Information']:
			d = disk["EID:Slt"]
			e,s = d.split(":")
			slots.append(int(s))

		return slots

	def doRaid(self, raidlevel, adapter, enclosure, slots, hotspares,
			flags):
		args = ['/c%d' % adapter, 'add','vd',
			'type=r%s' % raidlevel]

		disks = []
		for slot in slots:
			if enclosure:
				disks.append('%s:%d' % (enclosure, slot))
			else:
				disks.append('%s' % slot)

		args.append('drives=%s' % ','.join(disks))

		if flags:
			f = flags.split()
			args.extend(f)

		if hotspares:
			hs = []
			for hotspare in hotspares:
				if enclosure:
					hs.append('%s:%d' % (enclosure, hotspare))
				else:
					hs.append('%d' % hotspare)
	

			args.append('spares=%s' % ','.join(hs))

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
