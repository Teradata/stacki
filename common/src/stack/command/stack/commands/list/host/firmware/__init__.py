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
import os
import re
from collections import OrderedDict
from stack.commands.argument_processors import FirmwareArgumentProcessor

class command(
	stack.commands.HostArgumentProcessor,
	stack.commands.list.command,
	FirmwareArgumentProcessor,
):
	pass


class Command(command):
	"""
	List the hosts, and their corresponding available and installed firmwares.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list firmware backend-0-0'>
	List info for backend-0-0.
	</example>

	<example cmd='list firmware'>
	List info for all known hosts.
	</example>

	"""

	def run(self, params, args):
		order, expanded, hashit = self.fillParams(
			names = [
				('order', 'asc'),
				('expanded', False),
				('hash', False)
			],
			params = params
		)

		hosts = self.getHostnames(names = args, order = order)
		expanded = self.str2bool(expanded)
		hashit = self.str2bool(hashit)

		header = ['host']
		values = {host: [] for host in hosts}

		for provides, result in self.runPlugins((hosts, expanded, hashit)):
			header.extend(result['keys'])
			for host, items in result['values'].items():
				values[host].extend(items)

		self.beginOutput()
		for host in hosts:
			self.addOutput(host, values[host])
		self.endOutput(header = header)
