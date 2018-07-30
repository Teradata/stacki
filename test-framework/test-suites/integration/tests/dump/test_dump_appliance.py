import pytest
import json

class TestDumpAppliance:

	"""
	Test that dumping the appliance data works properly by adding some appliance information
	then dumping it and checking that it is valid
	"""

	def test_dump_appliance(self, host):

		# first lets add some appliance info so we know what to look for in the dump
		results = host.run('stack add appliance attr backend attr=test value=test shadow=False')
		assert results.rc == 0
		results = host.run('stack add appliance route backend address=192.168.0.0 gateway=192.168.0.1 netmask=255.255.255.0')
		assert results.rc == 0
		results = host.run('stack add appliance firewall backend action=accept chain=input protocol=udp service=www network=private output-network=private rulename=appliancetest table=filter comment="test" flags="-m set"')
		assert results.rc == 0
		results = host.run('stack add storage partition backend device=test options="test option" size=1 mountpoint=test partid=1 type=ext4')
		assert results.rc == 0
		results = host.run('stack add storage controller backend adapter=1 arrayid=2 enclosure=3 raidlevel=4 slot=5')
		assert results.rc == 0

		# dump our appliance information
		results = host.run('stack dump appliance')
		assert results.rc == 0
		dumped_data = json.loads(results.stdout)

		# check to make sure that the information we just added is in the dump data
		for appliance in dumped_data['appliance']:
			if appliance['name'] == 'backend':

				for attr in appliance['attrs']:
					if attr['attr'] == 'test':
						assert attr['scope'] == 'appliance'
						assert attr['type'] == 'var'
						assert attr['value'] == 'test'

				for route in appliance['route']:
					if route['network'] == '192.168.0.0':
						assert route['appliance'] == 'backend'
						assert route['netmask'] == '255.255.255.0'
						assert route['gateway'] == '192.168.0.1'

				for firewall in appliance['firewall']:
					if firewall['name'] == 'ostest':
						assert firewall['table'] == 'filter'
						assert firewall['service'] == 'www'
						assert firewall['protocol'] == 'udp'
						assert firewall['chain'] == 'INPUT'
						assert firewall['action'] == 'ACCEPT'
						assert firewall['network'] == 'private'
						assert firewall['output-network'] == 'private'
						assert firewall['flags'] == '-m set'
						assert firewall['comment'] == 'test'
						assert firewall['source'] == 'A'
						assert firewall['type'] == 'var'

				for partition in appliance['partition']:
					if partition['device'] == 'test':
						assert partition['partid'] == 1
						assert partition['mountpoint'] == 'test'
						assert partition['size'] == 1
						assert partition['fstype'] == 'ext4'
						assert partition['options'] == 'test option'
				for controller in appliance['controller']:
					if controller['options'] == 'test':
						assert controller['enclosure'] == 3
						assert controller['adapter'] == 1
						assert controller['slot'] == 5
						assert controller['raidlevel'] == '4'
						assert controller['arrayid'] == 2
