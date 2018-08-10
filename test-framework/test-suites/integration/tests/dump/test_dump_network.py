import pytest
import json

class TestDumpNetwork:

	"""
	Test that dumping the network data works properly by adding some network information
	then dumping it and checking that it is valid
	"""

	def test_dump_network(self, host):

		# first lets add a network so we know what to look for in the dump
		results = host.run('stack add network test address=192.168.0.0 mask=255.255.255.0 dns=False gateway=192.168.0.1 mtu=1500 pxe=False zone=test')
		assert results.rc == 0


		# dump our network information
		results = host.run('stack dump network')
		assert results.rc == 0
		dumped_data = json.loads(results.stdout)

		# check to make sure that the information we just added is in the dump data
		for network in dumped_data['network']:
			if network['name'] == 'test':
				assert network == {
					'name': 'test',
					'address': '192.168.0.0',
					'gateway': '192.168.0.1',
					'netmask': '255.255.255.0',
					'dns': False,
					'pxe': False,
					'mtu': 1500,
					'zone': 'test'
				}

