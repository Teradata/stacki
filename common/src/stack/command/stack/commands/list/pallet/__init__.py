# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
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

	<param type='bool' name='expanded' optional='0'>
	Displays an additional column containing the url of the pallet.
	</param>

	<example cmd='list pallet kernel'>		
	List the status of the kernel pallet.
	</example>
	
	<example cmd='list pallet'>
	List the status of all the available pallets.
	</example>

	<example cmd='list pallet expanded=true'>
	List the status of all the available pallets and their urls.
	</example>

	<related>add pallet</related>
	<related>remove pallet</related>
	<related>enable pallet</related>
	<related>disable pallet</related>
	<related>create pallet</related>
	"""		

	def run(self, params, args):
		self.beginOutput()

		expanded, = self.fillParams([ ('expanded', 'false') ])
		expanded = self.str2bool(expanded)

		for (roll, version, release) in self.getRollNames(args, params):
			rows = self.db.select("""r.arch, r.os, r.url, r.urlauthUser, r.urlauthPass from rolls r 
					where r.name=%s and r.version=%s and 
					r.rel=%s """
					, (roll, version, release))


			for arch, osname, url, urlauthUser, urlauthPass in rows:
				self.db.execute("""select b.name from stacks s, rolls r, 
						boxes b where r.name=%s and r.arch=%s 
						and r.version=%s and r.rel=%s and 
						s.roll=r.id and s.box=b.id """
						, (roll, arch, version, release))


				boxes = []
				for box, in self.db.fetchall():
					boxes.append(box)

			
				targets = [version, release, arch, osname, ' '.join(boxes)]
				if expanded:
					targets.append(url)
					targets.append(urlauthUser)
					targets.append(urlauthPass)
				self.addOutput(roll, targets)

		header = ['name', 'version', 'release', 'arch', 'os', 'boxes']			
		if expanded:
			header.append('url')
			header.append('urlauthUser')
			header.append('urlauthPass')
		
		self.endOutput(header, trimOwner=False)

