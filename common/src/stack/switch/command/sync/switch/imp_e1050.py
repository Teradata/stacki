# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import pexpect
import re
import subprocess
import stack.commands
from stack.exception import CommandError
from stack.switch.e1050 import SwitchCelesticaE1050


class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch_interface = args[0]

		self.switch_address = switch_interface['ip']
		self.switch_name = switch_interface['host']
		self.switch_username = self.owner.getHostAttr(self.switch_name, 'switch_username')
		self.switch_password = self.owner.getHostAttr(self.switch_name, 'switch_password')
		self.switch = SwitchCelesticaE1050(self.switch_address, self.switch_name, self.switch_username, self.switch_password)

		self.switch.ssh_copy_id()
		try:
			for command in open(f'/tmp/{self.switch_name}/new_config').readlines():
				self.switch.run(command.strip())

			#print(self.switch.run('pending'))
			self.switch.run('commit')
		except:
			print('shit')
			self.switch.run('abort')
		finally:
			subprocess.run(f'rm -rf /tmp/{self.switch_name}'.split(), stdout=subprocess.PIPE)

		subprocess.run(f'ssh {self.switch_username}@{self.switch_address} hostnamectl set-hostname {self.switch_name}'.split(),
				stdout=subprocess.PIPE)

