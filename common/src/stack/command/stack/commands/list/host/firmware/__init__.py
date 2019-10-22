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
from collections import namedtuple
from stack.argument_processors.firmware import FirmwareArgumentProcessor

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
		# Resolve any provided hostnames
		hosts = self.getHostnames(names = args)

		header = ["host", "make", "model",]
		# build a dictionary keyed by (host + make + model) so that the plugins and implementations
		# can return the data mapped appropriately. We do this by getting all the firmware mappings
		# and looking at the make and model of firmwares mapped to hosts.
		CommonKey = namedtuple("CommonKey", ("host", "make", "model"))
		CommonData = namedtuple("CommonData", ("firmware_version", "firmware_imp"))
		values = {
			CommonKey(*row[0:3]): CommonData(*row[3:]) for row in self.db.select(
				"""
				nodes.Name, firmware_make.name, firmware_model.name, firmware.version, firmware_imp.name
				FROM firmware_mapping
					INNER JOIN nodes
						ON firmware_mapping.node_id = nodes.ID
					INNER JOIN firmware
						ON firmware_mapping.firmware_id = firmware.id
					INNER JOIN firmware_model
						ON firmware.model_id = firmware_model.id
					INNER JOIN firmware_make
						ON firmware_model.make_id = firmware_make.id
					INNER JOIN firmware_imp
						ON firmware_model.imp_id = firmware_imp.id
				WHERE nodes.Name IN %s
				""",
				(hosts,)
			)
		}
		results = {
			key: [] for key in values
		}

		# loop through all the plugin results and extend header and values as necessary.
		CommonResult = namedtuple("CommonResult", ("header", "values"))
		for provides, result in self.runPlugins((CommonResult, values)):
			header.extend(result.header)
			for host_make_model, items in result.values.items():
				results[host_make_model].extend(items)

		# add empty entries for hosts with no firmware mappings.
		results.update(
			{
				# pad out with None for each extra column header added by the plugins
				CommonKey(host, None, None): [None for i in range(len(header) - 3)] for host in hosts
				if host not in (host_make_model.host for host_make_model in values)
			}
		)

		# output the results
		self.beginOutput()
		for host_make_model, result in results.items():
			self.addOutput(
				host_make_model.host,
				[host_make_model.make, host_make_model.model, *result]
			)
		self.endOutput(header = header)
