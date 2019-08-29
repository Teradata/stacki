import re


class TestReportHost:
	def test_with_default_network_behaviour(self, host, revert_etc):
		result = host.run('stack add network test address=10.10.0.0 mask=255.255.255.0 zone=')
		assert result.rc == 0

		result = host.run('stack add host backend-1-0')
		assert result.rc == 0

		result = host.run('stack add host interface backend-1-0 interface=eth0 ip=10.10.11.11 network=test')
		assert result.rc == 0

		result = host.run('stack add host backend-1-1')
		assert result.rc == 0

		result = host.run('stack add host interface backend-1-1 interface=eth1 ip=10.10.11.15 network=private default=True')
		assert result.rc == 0

		result = host.run('stack report host')
		assert result.rc == 0

		result = host.run('stack sync host')
		assert result.rc == 0

		with open('/etc/hosts','r') as hostsFile:
			contents = str(hostsFile.read())

		regexExp = re.compile(r'10\.10\.11\.11\s+backend-1-0')
		assert bool(not regexExp.search(contents))

		regexExp = re.compile(r'10\.10\.11\.15\s+backend-1-1')
		assert bool(regexExp.search(contents))

	def test_with_shortname_behaviour(self, host, revert_etc):
		result = host.run('stack add network test address=10.10.0.0 mask=255.255.255.0 zone=')
		assert result.rc == 0

		result = host.run('stack add host backend-2-0')
		assert result.rc == 0

		result = host.run('stack add host interface backend-2-0 interface=eth0 ip=10.10.11.11 network=test')
		assert result.rc == 0

		result = host.run('stack add host backend-2-2')
		assert result.rc == 0

		result = host.run('stack add host interface backend-2-2 interface=eth2 ip=10.10.11.15 network=test')
		assert result.rc == 0

		result = host.run('stack set host interface options backend-2-2 interface=eth2 options=shortname')
		assert result.rc == 0

		result = host.run('stack report host')
		assert result.rc == 0

		result = host.run('stack sync host')
		assert result.rc == 0

		with open('/etc/hosts','r') as hostsFile:
			contents = str(hostsFile.read())

		regexExp = re.compile(r'10\.10\.11\.11\s+backend-2-0')
		assert bool(not regexExp.search(contents))

		regexExp = re.compile(r'10\.10\.11\.15\s+backend-2-2')
		assert bool(regexExp.search(contents))

	def test_with_network_zone_behaviour(self, host, revert_etc):
		result = host.run('stack add network test address=10.20.0.0 mask=255.255.255.0 zone=')

		result = host.run('stack add host backend-3-0')
		assert result.rc == 0

		result = host.run('stack add host interface backend-3-0 interface=eth0 ip=10.10.11.11 network=test')
		assert result.rc == 0

		result = host.run('stack add host backend-3-3')
		assert result.rc == 0

		result = host.run('stack add network internal address=10.10.0.0 mask=255.255.255.0 zone=zone')
		assert result.rc == 0

		result = host.run('stack add host interface backend-3-3 interface=eth3 ip=10.10.11.15 network=internal')
		assert result.rc == 0

		result = host.run('stack report host')
		assert result.rc == 0

		result = host.run('stack sync host')
		assert result.rc == 0

		with open('/etc/hosts','r') as hostsFile:
			contents = str(hostsFile.read())

		regexExp = re.compile(r'10\.10\.11\.11\s+backend-3-0')
		assert bool(not regexExp.search(contents))

		regexExp = re.compile(r'10\.10\.11\.15\s+backend-3-3\.zone')
		assert bool(regexExp.search(contents))

	def test_with_alias_behaviour(self, host, revert_etc):
		result = host.run('stack add network test address=10.10.0.0 mask=255.255.255.0 zone=')
		assert result.rc == 0

		result = host.run('stack add host backend-4-0')
		assert result.rc == 0

		result = host.run('stack add host interface backend-4-0 interface=eth0 ip=10.10.11.11 network=test')
		assert result.rc == 0

		result = host.run('stack add host backend-4-4')
		assert result.rc == 0

		result = host.run('stack add host interface backend-4-4 interface=eth4 ip=10.10.11.15 network=test')
		assert result.rc == 0

		result = host.run('stack add host interface alias backend-4-4 alias=BACKEND4 interface=eth4')
		assert result.rc == 0

		result = host.run('stack report host')
		assert result.rc == 0

		result = host.run('stack sync host')
		assert result.rc == 0

		with open('/etc/hosts','r') as hostsFile:
			contents = str(hostsFile.read())

		regexExp = re.compile(r'10\.10\.11\.11\s+backend-4-0')
		assert bool(not regexExp.search(contents))

		regexExp = re.compile(r'10\.10\.11\.15\s+BACKEND4')
		assert bool(regexExp.search(contents))

	def test_exclude_interface_ip_no_network(self, host, add_host_with_interface):
		# set interface IP, but not network
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=192.0.2.1')
		assert result.rc == 0

		# report should exclude incorrectly configured interface
		result = host.run('stack report host')
		assert result.rc == 0
		assert 'backend-0-0' not in result.stdout
