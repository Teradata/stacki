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

import os
import string
import stack.file
import stack.commands


class Command(stack.commands.RollArgumentProcessor,
	stack.commands.list.command):
	"""
	List the commands provided by a pallet.
	
	<arg optional='1' type='string' name='pallet' repeat='1'>
	List of pallets. This should be the pallet base names (e.g., base, hpc,
	kernel). If no pallets are listed, then commands for all the pallets
	are listed.
	</arg>
	
	<example cmd='list pallet command stacki'>
	Returns the the list of commands installed by the stacki pallet.
	</example>		
	"""		

	def run(self, params, args):

		tree = stack.file.Tree(stack.commands.__path__[0])

		dict = {}
		for dir in sorted(tree.getDirs()):
			if not dir:
				continue
			modpath = 'stack.commands.%s' % '.'.join(dir.split(os.sep))
			__import__(modpath)
			module = eval(modpath)
			try:
				o = getattr(module, 'Command')
			except AttributeError:
				continue
			try:
				o = getattr(module, 'RollName')
			except AttributeError:
				continue
			if o not in dict:
				dict[o] = []
			dict[o].append(string.join(dir.split(os.sep), ' '))

		# If args are mentioned then use them, if not get all
		# pallet names from the database
		if len(args) == 0:
			roll_list = self.getRollNames(args, params)
			rolls = map(lambda x: x[0], roll_list)
		else:
			rolls = args
			
		seenrolls = []

		self.beginOutput()
		for roll in rolls:
			if roll in seenrolls:
				continue
			seenrolls.append(roll)
		
			if roll in dict:
				for command in dict[roll]:
					self.addOutput(roll, command)
			else:
				if len(rolls) > 1:
					self.addOutput(roll, '')
		self.endOutput(header=['pallet', 'command'])

