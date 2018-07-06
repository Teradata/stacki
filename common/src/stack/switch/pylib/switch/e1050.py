from . import Switch
from itertools import groupby
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SwitchCelesticaE1050(Switch):
	"""Class for interfacing with a Celestica e1050 switch running Cumulus Linux.
	"""

	def natural_sort(self, s):
		return [int(''.join(g)) if k else ''.join(g) for k, g in groupby('\0' + s, str.isdigit)]

	def rpc_req_text(self, cmd):
		url = f'https://{self.switch_ip_address}:8080/nclu/v1/rpc'
		payload = {"cmd": cmd}
		auth = (self.username, self.password)
		headers = {'Content-Type': 'application/json'}

		return requests.post(url, headers=headers, json=payload, auth=auth, verify=False).text

	def sorted_keys(self, dct):
		return sorted(dct, key=self.natural_sort)

	def json_loads(self, cmd):
		return json.loads(self.rpc_req_text(cmd))
