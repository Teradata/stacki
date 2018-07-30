import pytest
import json

class TestDumpHost:

	"""
	Test that dumping the host data works properly by adding some host information
	then dumping it and checking that it is valid
	"""

	def test_dump_host(self, host):

		# first lets add a host so we know what to look for in the dump
		results = host.run('stack add host backend-test box=default longname=Backend rack=1 rank=1')
		assert results.rc == 0
		results = host.run('stack set host comment backend-test comment=test')
		assert results.rc == 0
		results = host.run('stack set host metadata backend-test metadata=test')
		assert results.rc == 0
		results = host.run('stack add host attr backend-test attr=test value=test shadow=False')
		assert results.rc == 0
		results = host.run('stack add host interface backend-test channel=test default=False interface=eth1 ip=192.168.0.1 mac=00.11.22.33.44.55 module=test name=test network=public vlan=1')
		assert results.rc == 0
		results = host.run('stack set host interface options backend-test interface=eth1 options="test option"')
		assert results.rc == 0
		results = host.run('stack set host interface default backend-test default=True interface=eth1')
		assert results.rc == 0
		results = host.run('stack set host interface network backend-test interface=eth1 network=private')
		assert results.rc == 0
		results = host.run('stack add host route backend-test address=192.168.0.2 gateway=192.168.0.3 netmask=255.255.255.0 syncnow=true')
		assert results.rc == 0
		results = host.run('stack add storage controller backend-test adapter=1 arrayid=2 enclosure=3 raidlevel=4 slot=5')
		assert results.rc == 0
		results = host.run('stack add storage partition backend-test device=test options="test option" size=1 mountpoint=test partid=1 type=ext4')
		assert results.rc == 0
		results = host.run('stack add host firewall backend-test action=accept chain=input protocol=udp service=www comment=test flags="-m state" network=private output-network=private rulename=test table=filter')
		assert results.rc == 0

		# dump our host information
		results = host.run('stack dump host')
		assert results.rc == 0
		dumped_data = json.loads(results.stdout)

		# check to make sure that the information we just added is in the dump data
		for host in dumped_data['host']:
			if host['name'] == 'backend-test':
				assert host['rack'] == '1'
				assert host['rank'] == '1'
				assert host['interface'][0]['interface'] == 'eth1'
				assert host['interface'][0]['default'] == True
				assert host['interface'][0]['mac'] == '00.11.22.33.44.55'
				assert host['interface'][0]['ip'] == '192.168.0.1'
				assert host['interface'][0]['network'] == 'private'
				assert host['interface'][0]['vlan'] == 1
				assert host['interface'][0]['options'] == 'test option'
				assert host['interface'][0]['channel'] == 'test'
				for attr in host['attrs']:
					if attr['name'] == 'test':
						assert attr['value'] == 'test'
						assert attr['shadow'] == False
				assert host['firewall'][0]['name'] == 'test'
				assert host['firewall'][0]['table'] == 'filter'
				assert host['firewall'][0]['service'] == 'www'
				assert host['firewall'][0]['protocol'] == 'udp'
				assert host['firewall'][0]['chain'] == 'INPUT'
				assert host['firewall'][0]['action'] == 'ACCEPT'
				assert host['firewall'][0]['network'] == 'private'
				assert host['firewall'][0]['output-network'] == 'private'
				assert host['firewall'][0]['flags'] == '-m state'
				assert host['firewall'][0]['comment'] == 'test'
				assert host['firewall'][0]['source'] == 'H'
				assert host['firewall'][0]['type'] == 'var'
				assert host['box'] == 'default'
				assert host['appliance'] == 'backend'
				assert host['appliancelongname'] == 'Backend'
				assert host['comment'] == 'test'
				assert host['metadata'] == 'test'
				assert host['osaction'] == 'default'
				assert host['installaction'] == 'default'
				assert host['route'][0]['network'] == '192.168.0.2'
				assert host['route'][0]['netmask'] == '255.255.255.0'
				assert host['route'][0]['gateway'] == '192.168.0.3'
				assert host['route'][0]['source'] == 'H'
				assert host['partition'][0]['device'] == 'test'
				assert host['partition'][0]['partid'] == 1
				assert host['partition'][0]['mountpoint'] == 'test'
				assert host['partition'][0]['size'] == 1
				assert host['partition'][0]['fstype'] == 'ext4'
				assert host['partition'][0]['options'] == 'test option'
				assert host['controller'][0]['enclosure'] == 3
				assert host['controller'][0]['adapter'] == 1
				assert host['controller'][0]['slot'] == 5
				assert host['controller'][0]['raidlevel'] == '4'
				assert host['controller'][0]['arrayid'] == 2

