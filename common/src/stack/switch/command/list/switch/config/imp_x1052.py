# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError
from stack.switch import SwitchException
from stack.switch.x1052 import SwitchDellX1052


class Implementation(stack.commands.Implementation):
	def run(self, args):

		switch = args[0]

		# Get frontend ip for tftp address
		try:
			(_frontend, *args) = [host for host in self.owner.call('list.host.interface', ['localhost'])
					if host['network'] == switch['network']]
		except:
			raise CommandError(self, '"%s" and the frontend do not share a network' % switch['host'])

		frontend_tftp_address	= _frontend['ip']
		switch_address		= switch['ip']
		switch_name		= switch['host']
		switch_username		= self.owner.getHostAttr(switch_name, 'switch_username')
		switch_password		= self.owner.getHostAttr(switch_name, 'switch_password')

		list_switch_host = self.owner.call('list.switch.host', [ switch_name ])

		# Connect to the switch
		with SwitchDellX1052(switch_address, switch_name, switch_username, switch_password) as switch:
			try:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.connect()
				switch.download()

				filename = '%s/%s' % (switch.tftpdir, switch.current_config)
				with open(filename, 'r') as f:
					lines = f.readlines()
					_printline = True
					port = None
					porttype = None
					vlan = 'untagged'
					for line in lines:
						if not self.owner.raw:
							if 'crypto' in line:
								break

							if 'gigabitethernet' in line:
								port = line.split('/')[-1].strip()

							l = line.split()
							if len(l) == 3 and l[0] == 'switchport' and l[1] == 'mode':
								porttype = l[2].strip()

							if len(l) == 4 and l[0] == 'switchport' \
									and l[1] == porttype:
								vlan = l[3].strip()
								
							if '!' in line and port and porttype:
								host = None
								interface = None
								for o in list_switch_host:
									oport = '%s' % o['port']
									if oport == port:
										host = o['host']
										interface = o['interface']
										break

								self.owner.addOutput(switch_name,
									[ port, vlan, porttype,
									host, interface ])

								port = None
								porttype = None
								vlan = 'untagged'

						# This is the line that gets hit if raw=true
						else:
							if _printline:
								print(line, end='')
			except SwitchException as switch_error:
				raise CommandError(self, switch_error)
			except Exception:
				raise CommandError(self, "There was an error downloading the running config from the switch")

