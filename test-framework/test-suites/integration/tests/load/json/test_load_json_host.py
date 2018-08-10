import pytest

class TestLoadJsonHost:

	"""
	Test that the load json host is able to load what dump host dumps
	"""

	def test_load_json_host(self, host):

		# lets first add some dummy host data that we can later remove to make sure load works
		results = host.run('stack add host backend-test box=default longname=Backend rack=1 rank=1')
		assert results.rc == 0
		results = host.run('stack set host comment backend-test comment=test')
		assert results.rc == 0
		results = host.run('stack set host metadata backend-test metadata=test')
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

		# dump the host data
		results = host.run('stack dump host')
		assert results.rc == 0
		initial_host_data = results.stdout

		#write the output to a file
		with open ('host.json', 'w+') as file:
			file.write(initial_host_data)

		# now lets remove the extra data we added to make sure it all get re-added by load
		results = host.run('stack remove host backend-test')
		assert results.rc == 0

		#reload the host json file
		results = host.run('stack load json host file=host.json')
		assert results.rc == 0

		# re-dump the data and check that nothing has changed
		results = host.run('stack dump host')
		assert results.rc == 0
		final_host_data = results.stdout

		# make sure that they are the same
		value = set(initial_host_data) - set(final_host_data)
		assert not value
