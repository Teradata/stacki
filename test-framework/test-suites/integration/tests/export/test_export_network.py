import pytest
import json

@pytest.mark.usefixtures("revert_database")
class TestExportNetwork:

	"""
	Test that exporting the network data works properly by adding some network information
	then exporting it and checking that it is valid
	"""

	def test_export_network(self, host):

		# first lets add a network so we know what to look for in the export
		results = host.run('stack add network test address=192.168.0.0 mask=255.255.255.0 dns=False gateway=192.168.0.1 mtu=1500 pxe=False zone=test')
		assert results.rc == 0


		# export our network information
		results = host.run('stack export network')
		assert results.rc == 0
		exported_data = json.loads(results.stdout)

		# check to make sure that the information we just added is in the export data
		for network in exported_data['network']:
			if network['name'] == 'test':
				assert network['address'] == '192.168.0.0'
				assert network['gateway'] == '192.168.0.1'
				assert network['netmask'] == '255.255.255.0'
				assert network['dns'] == False
				assert network['pxe'] == False
				assert network['mtu'] == 1500
				assert network['zone'] == 'test'

