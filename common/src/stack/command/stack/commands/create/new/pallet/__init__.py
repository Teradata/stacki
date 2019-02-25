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

import os
import shutil
from jinja2 import Template
import stack
import stack.commands

class Command(stack.commands.create.new.command):
	"""	
	Create a skeleton directory structure for a pallet source.

	This command is to be used mainly by pallet developers.

	This command creates a directory structure from
	templates that can be then be populated with required
	software and configuration.

	Refer to Pallet Developer Guide for more information.

	<param type='string' name='name' optional='0'>	
	Name of the new pallet to be created.
	</param>
	
	<param type='string' name='version'>
	Version of the pallet. Typically the version of the
	application to be palletized.
	</param>

	<param type='string' name='os'>
	The OS of the pallet. 'sles', 'redhat' are acceptable options.
	Any other values will result in a pallet unrecognized by stacki.
	The default is the current OS.
	</param>

	<example cmd='create new pallet name=valgrind version=3.10.1'>
	Creates a new pallet for Valgrind version 3.10.1.
	</example>
	"""

	def createPalletSkeleton(self, tmplt_vars):
		""" Create directory structure for the new pallet"""
		name = tmplt_vars['pallet_name']

		if os.path.exists('./template'):
			template_dir = './template'
		else:
			template_dir = \
				'/opt/stack/share/build/src/pallet/template'

		# copy the template structure over
		shutil.copytree(template_dir, name)

		# rename all directories as needed
		for r, d, f in os.walk(name):
			for orig_dir in d:
				newdir = orig_dir.replace('PALLET', name)
				os.rename(os.path.join(r, orig_dir),
						os.path.join(r, newdir))

		# now re-scan the tree and rename (and perform template rendering on) files
		for r, d, f in os.walk(name):
			for orig_file in f:
				fi_name = os.path.join(r, orig_file.replace('PALLET', name))
				os.rename(os.path.join(r, orig_file), fi_name)

				# rewrite the file with template substitution
				with open(fi_name, 'r+') as fi:
					rendered = Template(fi.read()).render(**tmplt_vars)
					fi.seek(0)
					fi.truncate()
					fi.write(rendered)

	def run(self, params, args):

		name, version, os = self.fillParams([
			('name', None, True),
			('version', '1.0'),
			('os', self.os),
		])

		self.createPalletSkeleton({
			'pallet_name': name,
			'version': version,
			'os': os,
		})
