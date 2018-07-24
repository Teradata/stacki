import pytest
import json

class TestExportGlobal:

	"""
	Test that exporting the global data works properly by adding some global information
	then exporting it and checking that it is valid
	"""

	def test_export_global(self, host):

		# first lets add some data so we have something to check for
		results = host.run('stack add attr attr=test value=testvalue shadow=false')
		assert results.rc == 0
		results = host.run('stack add route address=192.168.0.0 gateway=192.168.0.1 interface=eth1 netmask=255.255.255.0')
		assert results.rc == 0
		results = host.run('stack add firewall action=accept chain=input protocol=udp service=www network=private output-network=private rulename=test table=filter comment="test" flags="-m set"')
		assert results.rc == 0
		results = host.run('stack add storage partition device=test options="test option" size=1 mountpoint=test partid=1 type=ext4')
		assert results.rc == 0
		results = host.run('stack add storage controller adapter=1 arrayid=2 enclosure=3 raidlevel=4 slot=5 options="test" scope=global')
		assert results.rc == 0

		# export our global information
		results = host.run('stack export global')
		assert results.rc == 0
		exported_data = json.loads(results.stdout)

		# check to make sure that the information we just added is in the export data
		for attr in exported_data['global']['attrs']:
			if attr['attr'] == 'test':
				assert attr['scope'] == 'global'
				assert attr['type'] == 'var'
				assert attr['value'] == 'testvalue'

		for route in exported_data['global']['route']:
			if route['network'] == '192.168.0.0':
				assert route['netmask'] == '255.255.255.0'
				assert route['gateway'] == '192.168.0.1'

		for firewall in exported_data['global']['firewall']:
			if firewall['name'] == 'test':
				assert firewall['table'] == 'filter'
				assert firewall['service'] == 'www'
				assert firewall['protocol'] == 'udp'
				assert firewall['chain'] == 'INPUT'
				assert firewall['action'] == 'ACCEPT'
				assert firewall['network'] == 'private'
				assert firewall['output-network'] == 'private'
				assert firewall['flags'] == '-m set'
				assert firewall['comment'] == 'test'
				assert firewall['source'] == 'G'
				assert firewall['type'] == 'var'

		for partition in exported_data['global']['partition']:
			if partition['device'] == 'test':
				assert partition['partid'] == 1
				assert partition['mountpoint'] == 'test'
				assert partition['size'] == 1
				assert partition['fstype'] == 'ext4'
				assert partition['options'] == 'test option'

		for controller in exported_data['global']['controller']:
			if controller['options'] == 'test':
				assert controller['enclosure'] == 3
				assert controller['adapter'] == 1
				assert controller['slot'] == 5
				assert controller['raidlevel'] == '4'
				assert controller['arrayid'] == 2