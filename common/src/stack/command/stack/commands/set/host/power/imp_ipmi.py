# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Implementation(stack.commands.Implementation):
	def run(self, args):
		host = args[0]
		cmd = args[1]
		impl_output = args[2]
		ipmi_ip = ''

		# See if the host has an ipmi interface, raise an error if not
		for interface in self.owner.call('list.host.interface', args = [host]):
			if interface['interface'] == 'ipmi':
				ipmi_ip = interface['ip']
				break
		if not ipmi_ip:
			return impl_output('', f'{host} missing ipmi interface', False)

		# Try to get ipmi username/passwords, otherwise try defaults
		username = self.owner.getHostAttrDict(host)[host].get('ipmi_username', 'root')
		password = self.owner.getHostAttrDict(host)[host].get('ipmi_password', 'admin')

		# Run the actual ipmitool command
		ipmi = f'ipmitool -I lanplus -H {ipmi_ip} -U {username} -P {password} chassis power {cmd}'

		cmd_output = self.owner._exec(ipmi, shlexsplit=True)
		if cmd_output.returncode != 0:
			return impl_output('' , cmd_output.stderr, False)
		return impl_output(cmd_output.stdout, '', True)
