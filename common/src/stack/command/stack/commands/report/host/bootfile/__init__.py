# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from operator import itemgetter
from itertools import groupby

from stack.argument_processors.host import HostArgProcessor
import stack.commands
from stack.exception import CommandError


class Command(HostArgProcessor, stack.commands.Command):
	"""
	Output the PXE file for a host
	<arg name="host" type="string" repeat="1">
	One or more hostnames
	</arg>
	<param name="action" type="string" optional="0">
	Generate PXE file for a specified action
	</param>
	"""


	def run(self, params, args):

		hosts = self.getHostnames(args, managed_only=True)

		action, = self.fillParams([
			('action', None)
		])

		# If there are no host appliances there is no need to proceed
		if len(hosts) == 0:
			return

		# only populated if action != None
		list_host_boot_actions = {k: None for k in hosts}
		if not action: # param can override the db
			for row in self.call('list.host.boot', hosts):
				list_host_boot_actions[row['host']] = row['action']

		host_attributes = self.getHostAttrDict(hosts)

		# works just like getHostAttrDict()
		# get all hosts in a dictionary with their interaces.
		cond = lambda iface: all(itemgetter('ip', 'pxe')(iface))
		host_interfaces = {
			k: {i['interface']: i for i in v if cond(i)}
			for k, v in groupby(
				self.call('list.host.interface', hosts + ['expanded=true']),
				itemgetter('host'))
		}

		host_data = {}
		for host_row in self.call('list.host', hosts):
			# don't build bootfiles for the frontend
			if host_row['appliance'] == 'frontend':
				continue

			hostname = host_row['host']

			# don't build bootfiles for hosts with no interfaces
			if hostname not in host_interfaces:
				continue

			this_host = {
				'host'       : hostname,
				'type'       : action or list_host_boot_actions[hostname],
				'attrs'      : host_attributes[hostname],
				'os'         : host_row['os'],
				'appliance'  : host_row['appliance'],
			}

			if this_host['type'] == 'install':
				this_host['action'] = host_row['installaction']
			elif this_host['type'] == 'os':
				this_host['action'] = host_row['osaction']

			# if this host has no boot action currently set - don't try to write a bootfile for it
			if this_host['action'] == None:
				continue

			this_host['interfaces'] = host_interfaces[hostname].values()

			host_data[hostname] = this_host

		# This condition is checked again because the previous block updates the list of hosts
		if len(host_data) == 0:
			return

		ba = {}
		for row in self.call('list.bootaction'):
			ba[(row['bootaction'], row['type'], row['os'])] = row

		for host in host_data:
			h   = host_data[host]
			key = (h['action'], h['type'], None)
			if key in ba:
				b = ba[key]
				h['kernel']  = b['kernel']
				h['ramdisk'] = b['ramdisk']
				h['args']    = b['args']
			key = (h['action'], h['type'], h['os'])
			if key in ba:
				b = ba[key]
				h['kernel']  = b['kernel']
				h['ramdisk'] = b['ramdisk']
				h['args']    = b['args']

		self.beginOutput()
		self.runPlugins(host_data)
		self.endOutput(padChar='', trimOwner=True)

