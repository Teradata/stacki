class TestReportHostInterface:
	def test_exclude_interface_ip_no_network(self, host, add_host_with_interface):
		# set interface IP, but not network
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=1.1.1.1')
		assert result.rc == 0

		# report should exclude incorrectly configured interface
		result = host.run('stack report host interface')
		assert result.rc == 0
		assert 'backend-0-0' not in result.stdout

	def test_single(self, host, add_host, add_network, host_os):
		# Add an interface to our backend with some simple case parameters
		result = host.run(
			'stack add host interface backend-0-0 interface=eth0 mac=00:11:22:33:44:55 network=test ip=192.168.0.2'
		)
		assert result.rc == 0

		# Add a second interface with noreport, which should be skipped
		result = host.run(
			'stack add host interface backend-0-0 interface=eth1 network=test ip=192.168.0.2 options=noreport'
		)
		assert result.rc == 0

		# And add a third interface without a device, which should be skipped
		result = host.run(
			'stack add host interface backend-0-0 mac=00:00:00:00:00:03'
		)
		assert result.rc == 0

		# Report our test backend interface
		result = host.run('stack report host interface backend-0-0')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/host_interface_single_{host_os}.txt') as output:
			assert result.stdout == output.read()

	def test_bridged(self, host, add_host, add_network, host_os):
		# Add the bridge interface to the backend
		result = host.run(
			'stack add host interface backend-0-0 interface=br0 network=test ip=192.168.0.2 options=bridge'
		)
		assert result.rc == 0

		# Add an physical interface to our backend that will be bridged
		result = host.run(
			'stack add host interface backend-0-0 interface=eth0 mac=00:11:22:33:44:55 channel=br0'
		)
		assert result.rc == 0

		# Report our test backend interface
		result = host.run('stack report host interface backend-0-0')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/host_interface_bridged_{host_os}.txt') as output:
			assert result.stdout == output.read()

	def test_bonded(self, host, add_host, add_network, host_os):
		# Add the bond interface to the backend
		result = host.run(
			'stack add host interface backend-0-0 interface=bond0 network=test '
			'ip=192.168.0.2 options=bonding-opts="mode=1 primary=em1"'
		)
		assert result.rc == 0

		# Add two physical interfaces to our backend that will be bonded
		result = host.run('stack add host interface backend-0-0 interface=eth0 mac=00:00:00:00:00:01 channel=bond0')
		assert result.rc == 0

		result = host.run('stack add host interface backend-0-0 interface=eth1 mac=00:00:00:00:00:02 channel=bond0')
		assert result.rc == 0

		# Report our test backend interface
		result = host.run('stack report host interface backend-0-0')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/host_interface_bonded_{host_os}.txt') as output:
			assert result.stdout == output.read()

	def test_vlan(self, host, add_host, add_network, host_os):
		# Add a second network to act as our VLAN
		add_network('vlan', '10.10.10.0')

		# Add an interface to our backend on the test network
		result = host.run(
			'stack add host interface backend-0-0 interface=eth0 mac=00:11:22:33:44:55 network=test ip=192.168.0.2'
		)
		assert result.rc == 0

		# Now add a virtual interface on the VLAN
		result = host.run('stack add host interface backend-0-0 interface=eth0.1 network=vlan ip=10.10.10.2 vlan=1')
		assert result.rc == 0

		# Report our test backend interface
		result = host.run('stack report host interface backend-0-0')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/host_interface_vlan_{host_os}.txt') as output:
			assert result.stdout == output.read()

	def test_ipmi(self, host, add_host, host_os):
		# Add our ipmi network
		result = host.run('stack add network ipmi address=10.10.10.0 mask=255.255.255.0 gateway=10.10.10.1')
		assert result.rc == 0

		# Add an ipmi interface to our test backend
		result = host.run('stack add host interface backend-0-0 interface=ipmi network=ipmi ip=10.10.10.2 channel=1')
		assert result.rc == 0

		# Report our test backend interface
		result = host.run('stack report host interface backend-0-0')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/host_interface_ipmi_{host_os}.txt') as output:
			assert result.stdout == output.read()

	def test_virtual(self, host, add_host, add_network, host_os):
		# Add two virtual interfaces on the test backend
		result = host.run('stack add host interface backend-0-0 interface=eth0:0 network=test ip=192.168.0.2')
		assert result.rc == 0

		result = host.run('stack add host interface backend-0-0 interface=eth0:1 network=test ip=192.168.0.3')
		assert result.rc == 0

		# Report our test backend interfaces
		result = host.run('stack report host interface backend-0-0')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/host_interface_virtual_{host_os}.txt') as output:
			assert result.stdout == output.read()

	def test_dhcp(self, host, add_host, add_network, host_os):
		# Add a dhcp interface on the test backend
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test options=dhcp')
		assert result.rc == 0

		# Report our test backend interfaces
		result = host.run('stack report host interface backend-0-0')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/host_interface_dhcp_{host_os}.txt') as output:
			assert result.stdout == output.read()

	def test_dhcp_default(self, host, add_host, add_network, host_os):
		# Add a dhcp interface on the test backend
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test options=dhcp default=true')
		assert result.rc == 0

		# Report our test backend interfaces
		result = host.run('stack report host interface backend-0-0')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/host_interface_dhcp_default_{host_os}.txt') as output:
			assert result.stdout == output.read()

	def test_manual(self, host, add_host, add_network, host_os):
		# Add an interface with "onboot=no" option
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test options="onboot=no"')
		assert result.rc == 0

		# Report our test backend interfaces
		result = host.run('stack report host interface backend-0-0')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/host_interface_manual_{host_os}.txt') as output:
			assert result.stdout == output.read()

	def test_only_device(self, host, add_host, add_network, host_os):
		# Add an interface with only a device
		result = host.run('stack add host interface backend-0-0 interface=eth0')
		assert result.rc == 0

		# Report our test backend interfaces
		result = host.run('stack report host interface backend-0-0')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/host_interface_only_device_{host_os}.txt') as output:
			assert result.stdout == output.read()
