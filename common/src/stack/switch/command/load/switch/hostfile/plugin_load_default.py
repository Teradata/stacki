# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@

import sys
import stack.commands
from stack.bool import str2bool


class Plugin(stack.commands.HostArgumentProcessor, stack.commands.Plugin):

	def provides(self):
		return 'default'


	def removeHosts(self, switch, host):
		self.owner.call('remove.switch.host',
			[ switch, 'host=%s' % host ])


	def run(self, args):
		hosts = args
		existinghosts = self.getHostnames()

		sys.stderr.write('\tAdd Host\n')
		for host in hosts.keys():

			sys.stderr.write('\t\t%s\r' % host)

			#
			# add the host if it does exist
			#
			if host in existinghosts:
				switch		= hosts[host].get('switch')
				name		= hosts[host].get('host')
				port		= hosts[host].get('port')
				interface	= hosts[host].get('interface')

				# delete the previous entry in case the interface 
				# has changed
				self.owner.call('remove.switch.host', [
						switch,
						"host=%s" % name,
						])

				# add switch host

				switch_args = [switch, "host=%s" % name, "port=%s" % port]

				# if interface column is not null, add it to switch args
				if interface:
					switch_args.append("interface=%s" % interface)

				self.owner.call('add.switch.host', switch_args)

			sys.stderr.write('\t\t%s\r' % (' ' * len(host)))

