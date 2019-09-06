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

		# Unlike ipmi, ssh has no way to start a host that is off
		# We still have to handle the command however
		if cmd == 'on':
			return impl_output('', f'Cannot use ssh to start host {host}', False)

		elif cmd == 'off':
			cmd_output = self.owner._exec(f'ssh {host} "shutdown -h now"', shlexsplit=True)
			err = cmd_output.stderr
			if cmd_output.returncode != 0 and f'Connection to {host} closed by remote host' not in err:
				return impl_output('', err.strip(), False)
			return impl_output('', cmd_output.stdout, True)

		elif cmd == 'reset':
			cmd_output = self.owner._exec(f'ssh {host} "reboot"',shlexsplit=True)
			err = cmd_output.stderr

			# After issueing a reboot, ssh will send a Connection closed message in stderr
			# We shouldn't raise an error because of this
			if cmd_output.returncode != 0 and f'Connection to {host} closed by remote host' not in err:
				return impl_output('', err.strip(), False)

			# Return stderr here as stdout is blank
			return impl_output('', err.strip(), True)

		elif cmd == 'status':

			# If we can run a command on the remote host, it's up
			cmd_output = self.owner._exec(f'ssh {host} "hostname"', shlexsplit=True)
			out = cmd_output.stdout
			err = cmd_output.stderr
			if cmd_output.returncode != 0:
				return impl_output('', f'Chassis Power is unreachable via ssh: {err.strip()}', False)
			return impl_output(f'Chassis Power is on\n', '', True)
