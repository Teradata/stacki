# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


import os
import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.RollArgumentProcessor,
	stack.commands.disable.command):
	"""
	Disable an available pallet. The pallet must already be copied on the
	system using the command "stack add pallet".
	
	<arg type='string' name='pallet' repeat='1'>
	List of pallets to disable. This should be the pallet base name (e.g.,
	base, hpc, kernel).
	</arg>
	
	<param type='string' name='version'>
	The version number of the pallet to be disabled. If no version number is
	supplied, then all versions of a pallet will be disabled.
	</param>
	
	<param type='string' name='arch'>
	If specified disables the pallet for the given architecture. The default
	value is the native architecture of the host.
	</param>

	<param type='string' name='box'>
	The name of the box in which to disable the pallet. If no
	box is specified the pallet is disabled for the default box.
	</param>

	<example cmd='disable pallet kernel'>
	Disable the kernel pallet.
	</example>
	
	<example cmd='disable pallet ganglia version=5.0 arch=i386'>
	Disable version 5.0 the Ganglia pallet for i386 nodes
	</example>
	
	<related>add pallet</related>
	<related>remove pallet</related>
	<related>enable pallet</related>
	<related>list pallet</related>
	<related>create pallet</related>
	"""		

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'pallet')

		(arch, box) = self.fillParams([
			('arch', self.arch),
			('box', 'default')
			])

		rows = self.db.execute("""
			select * from boxes where name = '%s'
			""" % box)
		if not rows:
			raise CommandError(self, 'unknown box "%s"' % box)
		
		for (roll, version, release) in self.getRollNames(args, params):
			if release:
				rel = "rel='%s'" % release
			else:
				rel = 'rel=""'

			self.db.execute("""
				delete from stacks where
				box = (select id from boxes where name='%s')
				and
				roll = (select id from rolls where name='%s'
				and version='%s' and %s and arch='%s') """
				% (box, roll, version, rel, arch))

		# Regenerate stacki.repo
		os.system("""
			/opt/stack/bin/stack report host repo localhost | 
			/opt/stack/bin/stack report script | 
			/bin/sh
			""")
