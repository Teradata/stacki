import pytest
import json

class TestDumpOs:

	"""
	Test that dumping the os data works properly by adding some os information
	then dumping it and checking that it is valid
	"""

	def test_dump_os(self, host):

		# first lets add some os info so we know what to look for in the dump
		results = host.run('stack add os attr redhat attr=test value=test shadow=False')
		assert results.rc == 0
		results = host.run('stack add os route redhat address=192.168.0.0 gateway=192.168.0.1 netmask=255.255.255.0 interface=eth1')
		assert results.rc == 0
		results = host.run('stack add os firewall redhat action=accept chain=input protocol=udp service=www network=private output-network=private rulename=ostest table=filter comment="test" flags="-m set"')
		assert results.rc == 0
		results = host.run('stack add storage partition redhat device=test options="test option" size=1 mountpoint=test partid=1 type=ext4')
		assert results.rc == 0
		results = host.run('stack add os storage controller redhat adapter=1 arrayid=2 enclosure=3 raidlevel=4 slot=5 options=test')
		assert results.rc == 0

		# dump our os information
		results = host.run('stack dump os')
		assert results.rc == 0
		dumped_data = json.loads(results.stdout)

		# check to make sure that the information we just added is in the dump data
		for os in dumped_data['os']:
			if os['name'] == 'redhat':

				for attr in os['attr']:
					if attr['name'] == 'test':
						assert attr['value'] == 'test'

				for route in os['route']:
					if route['address'] == '192.168.0.0':
						assert route == {
							'address': '192.168.0.0',
							'netmask': '255.255.255.0',
							'gateway': '192.168.0.1',
							'interface': 'eth1'
						}

				for firewall in os['firewall']:
					if firewall['name'] == 'ostest':
						assert firewall == {
								'name':'ostest',
								'table':'filter',
								'service':'www',
								'protocol':'udp',
								'chain':'INPUT',
								'action':'ACCEPT',
								'network':'private',
								'output_network':'private',
								'flags':'-m set',
								'comment':'test',
						}

				for partition in os['partition']:
					if partition['device'] == 'test':
						assert partition == {
								'device': 'test',
								'partid': 1,
								'mountpoint': 'test',
								'size': 1,
								'fstype': 'ext4',
								'options': 'test option'
						}
				for controller in os['controller']:
					if controller['options'] == 'test':
						assert controller == {
								'options': 'test',
								'enclosure': 3,
								'adapter': 1,
								'slot': 5,
								'raidlevel': '4',
								'arrayid': 2
						}
