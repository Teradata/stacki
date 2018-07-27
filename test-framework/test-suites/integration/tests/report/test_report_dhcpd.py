import pytest

class TestReportDhcpd:
	def test_duplicate_interface(self, host):
		result = host.run('stack add host interface frontend-0-0 interface=eth0 mac=00:11:22:33:44:55 ip=1.2.3.4 network=private')
		assert result.rc == 0
		result = host.run('stack set host interface interface frontend-0-0 mac=00:11:22:33:44:55 interface=eth1')
		assert result.rc == 0

		# duplicate interface should be excluded from report
		result = host.run('stack report dhcpd')
		assert result.rc == 0
		assert result.stdout.count('eth1') == 2

	def test_invalid_channel(self, host):
		result = host.run('stack add host interface frontend-0-0 interface=eth0 mac=00:11:22:33:44:55 channel=alvin')
		assert result.rc == 0

		# interface with invalid channel should be excluded from report
		result = host.run('stack report dhcpd')
		assert result.rc == 0
		assert 'eth0' not in result.stdout

	def test_invalid_ipmi_channel(self, host):
		result = host.run('stack add host interface frontend-0-0 interface=ipmi channel=1')
		assert result.rc == 0

		# interface with invalid channel should be excluded from report
		result = host.run('stack report dhcpd')
		assert result.rc == 0
		assert 'eth0' not in result.stdout

