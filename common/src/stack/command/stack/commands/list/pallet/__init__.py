# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Command(stack.commands.RollArgumentProcessor,
	stack.commands.list.command):
	"""
	List the status of available pallets.
	
	<arg optional='1' type='string' name='pallet' repeat='1'>
	List of pallets. This should be the pallet base name (e.g., base, hpc,
	kernel). If no pallets are listed, then status for all the pallets are
	listed.
	</arg>

	<example cmd='list pallet kernel'>		
	List the status of the kernel pallet.
	</example>
	
	<example cmd='list pallet'>
	List the status of all the available pallets.
	</example>

	<related>add pallet</related>
	<related>remove pallet</related>
	<related>enable pallet</related>
	<related>disable pallet</related>
	<related>create pallet</related>
	"""		

	def run(self, params, args):
		self.beginOutput()

		for (roll, version, release) in self.getRollNames(args, params):
			self.db.execute("""select r.arch, r.os from rolls r
				where r.name='%s' and r.version='%s' and
				r.rel='%s' """
				% (roll, version, release))
			
			# For each pallet determine it is enabled
			# in any boxes.
			
			for arch, osname in self.db.fetchall():
				self.db.execute("""select b.name from
					stacks s, rolls r, boxes b where
					r.name='%s' and r.arch='%s' and
					r.version='%s' and r.rel='%s' and
					s.roll=r.id and s.box=b.id """
					% (roll, arch, version, release))

				boxes = []
				for box, in self.db.fetchall():
					boxes.append(box)

				self.addOutput(roll, (version, release, arch,
						      osname, ' '.join(boxes)))

		self.endOutput(header=['name', 'version', 'release', 'arch',
			'os', 'boxes'], trimOwner=False)
		
