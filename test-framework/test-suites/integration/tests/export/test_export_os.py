import pytest
import json

@pytest.mark.usefixtures("revert_database")
class TestExportOs:

	"""
	Test that exporting the os data works properly by adding some os information
	then exporting it and checking that it is valid
	"""

	def test_export_os(self, host):

		# first lets add some os info so we know what to look for in the export
		results = host.run('stack add os attr redhat attr=test value=test shadow=False')
		assert results.rc == 0
		results = host.run('stack add os route redhat address=192.168.0.0 gateway=192.168.0.1 netmask=255.255.255.0')
		assert results.rc == 0
		results = host.run('stack add os firewall redhat action=accept chain=input protocol=udp service=www network=private output-network=private rulename=ostest table=filter comment="test" flags="-m set"')
		assert results.rc == 0
#		results = host.run('stack add storage partition redhat device=test options="test option" size=1 mountpoint=test partid=1 type=ext4')
#		assert results.rc == 0
#		results = host.run('stack add storage controller redhat adapter=1 arrayid=2 enclosure=3 raidlevel=4 slot=5')
#		assert results.rc == 0

		# export our os information
		results = host.run('stack export os')
		assert results.rc == 0
		exported_data = json.loads(results.stdout)

		# check to make sure that the information we just added is in the export data
		for os in exported_data['os']:
			if os['name'] == 'redhat':

				for attr in os['attrs']:
					if attr['attr'] == 'test':
						assert attr['scope'] == 'os'
						assert attr['type'] == 'var'
						assert attr['value'] == 'test'

				for route in os['route']:
					if route['network'] == '192.168.0.0':
						assert route['os'] == 'redhat'
						assert route['netmask'] == '255.255.255.0'
						assert route['gateway'] == '192.168.0.1'

				for firewall in os['firewall']:
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
						assert firewall['source'] == 'O'
						assert firewall['type'] == 'var'

# The following is commented out awaiting storage controller fixes
#				for partition in os['partition']:
#					if partition['device'] == 'test':
#						assert partition['partid'] == 1
#						assert partition['mountpoint'] == 'test'
#						assert partition['size'] == 1
#						assert partition['fstype'] == 'ext4'
#						assert partition['options'] == 'test option'
#				for controller in os['controller']:
#					if controller['options'] == 'test':
#						assert controller['enclosure'] == 3
#						assert controller['adapter'] == 1
#						assert controller['slot'] == 5
#						assert controller['raidlevel'] == '4'
#						assert controller['arrayid'] == 2
