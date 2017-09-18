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

import sys
import string
import subprocess
import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.run.command, stack.commands.RollArgumentProcessor):
	"""
	Installs a pallet on the fly
	
	<arg optional='0' type='string' name='pallet' repeat='1'>
	List of pallets. This should be the pallet base name (e.g., base, hpc,
	kernel).
	</arg>

	<example cmd='run pallet ubuntu'>		
	Installs the Ubuntu pallet onto the current system.
	</example>
	"""

	def run(self, params, args):

		(database,) = self.fillParams([ ('database', 'true') ])
		database = self.str2bool(database)

		if database:
			if not args:
				raise ArgRequired(self, 'pallet')

			#
			# calling getRollNames will throw an exception if pallet
			# isn't in the DB
			#
			try:
				self.getRollNames(args, params)
			except CommandError:
				raise

			for arg in args:
				# if a roll/pallet isn't in the stacks table it isn't enabled.
				rows = self.db.execute("""
					select * from stacks
					where roll = (select id from rolls where name = '%s')""" % arg)
				if not rows:
					msg = 'Cannot run a pallet that is not enabled: %s' % arg
					raise CommandError(self, msg)

		script = []
		script.append('#!/bin/sh')

		rolls = []
		for roll in args:
			rolls.append(roll)
		if sys.stdin.isatty():
			cmdparams = [ 'localhost' ]
			if rolls:
				cmdparams.append('pallet=%s' %
					string.join(rolls, ','))
			xml = self.command('list.host.xml', cmdparams)
		else:
			xml = sys.stdin.read()

		p = subprocess.Popen('/opt/stack/bin/stack list host profile chapter=main profile=bash',
				     stdin=subprocess.PIPE,
				     stdout=subprocess.PIPE,
				     stderr=subprocess.PIPE, shell=True)
		p.stdin.write(xml.encode())
		(o, e) = p.communicate()
		if p.returncode == 0:
			sys.stdout.write(o.decode())
		else:
			sys.stderr.write(e.decode())

