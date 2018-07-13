# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import pexpect
import re
import stack.commands
from stack.exception import CommandError
from stack.switch.e1050 import SwitchCelesticaE1050


class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch_interface = args[0]

		# handle bad ip/creds?
		self.switch_address = switch_interface['ip']
		self.switch_name = switch_interface['host']
		self.switch_username = self.owner.getHostAttr(self.switch_name, 'switch_username')
		self.switch_password = self.owner.getHostAttr(self.switch_name, 'switch_password')
		self.switch = SwitchCelesticaE1050(self.switch_address, self.switch_name, self.switch_username, self.switch_password)

		self.ssh_copy_id()
		try:
			# `stack report switch` output
			for command in open(f'/asdf/{self.switch_name}/new_config').readlines():
				self.switch.rpc_req_text(cmd=command.strip())

			print(self.switch.rpc_req_text(cmd='pending'))
			self.switch.rpc_req_text(cmd='abort')  # commit
		except:
			self.switch.rpc_req_text(cmd='abort')

		# set switch host name?

	# does this belong in switch class?
	def ssh_copy_id(self):
		child = pexpect.spawn(f'ssh-copy-id -i /root/.ssh/id_rsa.pub {self.switch_username}@{self.switch_address}')
		try:
			child.expect('password')
			child.sendline(self.switch_password)
			child.expect(pexpect.EOF)

			print(f'{self.switch_name}:', re.search(r'Number of (.+)', child.before.decode('utf-8')).group())
		except pexpect.EOF:
			print(f'{self.switch_name}:', re.findall(r'WARNING: (.+)', child.before.decode('utf-8'))[0])

