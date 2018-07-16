from . import Switch
import itertools
import json
import pexpect
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SwitchCelesticaE1050(Switch):
	"""Class for interfacing with a Celestica Pebble E1050 switch running Cumulus Linux.
	"""

	def run(self, cmd, json_loads=False):
		url = f'https://{self.switch_ip_address}:8080/nclu/v1/rpc'
		payload = {"cmd": cmd}
		auth = (self.username, self.password)
		headers = {'Content-Type': 'application/json'}

		text = requests.post(url, headers=headers, json=payload, auth=auth, verify=False).text
		return json.loads(text) if json_loads else text

	def ssh_copy_id(self):
		child = pexpect.spawn(f'ssh-copy-id -i /root/.ssh/id_rsa.pub {self.username}@{self.switch_ip_address}')
		try:
			child.expect('password')
			child.sendline(self.password)
			child.expect(pexpect.EOF)

		except pexpect.EOF:
			# if ssh key is already copied to switch, expect('password') will fail (ok)
			pass

