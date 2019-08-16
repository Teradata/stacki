# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import sys
import subprocess

import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(
	stack.commands.run.command,
	stack.commands.PalletArgumentProcessor,
	stack.commands.BoxArgumentProcessor
):
	"""
	Installs a pallet on the fly

	<arg optional='0' type='string' name='pallet' repeat='1'>
	List of pallets. This should be the pallet base name (e.g., base, hpc,
	kernel).
	</arg>

	<param type='string' name='version'>
	The version number of the pallets to be ran. If no version number is
	supplied, then all versions of a pallet will be ran.
	</param>

	<param type='string' name='release'>
	The release number of the pallet to be ran. If no release number is
	supplied, then all releases of a pallet will be ran.
	</param>

	<param type='string' name='arch'>
	The architecture of the pallet to be ran. If no architecture is
	supplied, then all architectures of a pallet will be ran.
	</param>

	<param type='string' name='os'>
	The OS of the pallet to be ran. If no OS is supplied, then all OS
	versions of a pallet will be ran.
	</param>

	<example cmd='run pallet ubuntu'>
	Installs the Ubuntu pallet onto the current system.
	</example>
	"""

	def run(self, params, args):
		(database,) = self.fillParams([ ('database', 'true') ])
		database = self.str2bool(database)

		if database:
			# If we have a database then you have to specify a pallet
			if not args:
				raise ArgRequired(self, 'pallet')

			# Make sure the pallets exist and are enabled for the frontend box
			box = self.call("list.host",["localhost"])[0]["box"]
			# List of all pallets enabled for the frontend
			fe_pallets = self.getBoxPallets(box)
			# List of all pallets specified on the command line
			arg_pallets = self.getPallets(args, params)
			# Find the intersection of the 2 list of pallets
			pallets = [ pallet.name for pallet in arg_pallets if pallet in fe_pallets ]
			# If there aren't any, raise a command error and exit out.
			if not pallets:
				for pallet in arg_pallets:
					raise CommandError(self, f"{pallet.name} is not in box {box}")
		else:
			# No DB so we use the pallet names from the args
			pallets = args

		# Generate the scripts
		script = []
		script.append('#!/bin/sh')

		if sys.stdin.isatty():
			cmd_params = ['localhost']
			if pallets:
				cmd_params.append('pallet=%s' % ','.join(pallets))

			xml = self.command('list.host.xml', cmd_params)
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
