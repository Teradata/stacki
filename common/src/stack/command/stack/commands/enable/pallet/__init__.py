# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@


import os
import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.RollArgumentProcessor,
	stack.commands.enable.command):
	"""
	Enable an available pallet. The pallet must already be copied on the
	system using the command "stack add pallet".

	<arg type='string' name='pallet' repeat='1'>
	List of pallets to enable. This should be the pallet base name (e.g.,
	stacki, boss, os).
	</arg>
	
	<param type='string' name='version'>
	The version number of the pallet to be enabled. If no version number is
	supplied, then all versions of a pallet will be enabled.
	</param>

	<param type='string' name='release'>
	The release number of the pallet to be enabled. If no release number is
	supplied, then all releases of a pallet will be enabled.
	</param>

	<param type='string' name='arch'>
	If specified enables the pallet for the given architecture.  The default
	value is the native architecture of the host.
	</param>

	<param type='string' name='box'>
	The name of the box in which to enable the pallet. If no
	box is specified the pallet is enabled for the default box.
	</param>

	<example cmd='enable pallet kernel'>
	Enable the kernel pallet.
	</example>

	<example cmd='enable pallet ganglia version=5.0 arch=i386'>
	Enable version 5.0 the Ganglia pallet for i386 nodes.
	</example>

	<related>add pallet</related>
	<related>remove pallet</related>
	<related>disable pallet</related>
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
			select * from boxes where name='%s'
			""" % box)
		if not rows:
			raise CommandError(self, 'unknown box "%s"' % box)
		
		for (roll, version, release) in self.getRollNames(args, params):
			if release:
				rel = "rel='%s'" % release
			else:
				rel = 'rel=""'

			rows = self.db.execute("""
				select b.name from
				stacks s, rolls r, boxes b where
				r.name = '%s' and
				r.version = '%s' and %s and
				r.arch = '%s' and
				b.name = '%s' and
				s.box = b.id and s.roll=r.id
				""" % (roll, version, rel, arch, box))

			if not rows:
				self.db.execute("""
					insert into stacks(box, roll)
					values (
					(select id from boxes where name='%s'),
					(select id from rolls where name='%s'
					and version='%s' and %s and arch='%s')
					)""" % (box, roll, version, rel, arch))

		# Regenerate stacki.repo
		os.system("""
			/opt/stack/bin/stack report host repo localhost | 
			/opt/stack/bin/stack report script | 
			/bin/sh
			""")
