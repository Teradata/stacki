import pytest

@pytest.mark.usefixtures('revert_database')
class TestReportDhcpd:
	def test_duplicate_interface(self, host):
		result = host.run('stack add host interface frontend-0-0 interface=eth0 mac=00:11:22:33:44:55')
		assert result.rc == 0
		result = host.run('stack set host interface interface frontend-0-0 mac=00:11:22:33:44:55 interface=eth1')
		assert result.rc == 0

		# generate report with duplicate host interface (invalid)
		result = host.run('stack report dhcpd')
		assert result.rc != 0
		assert 'Duplicate interface' in result.stderr

	def test_invalid_channel(self, host):
		result = host.run('stack add host interface frontend-0-0 interface=eth0 mac=00:11:22:33:44:55 channel=alvin')
		assert result.rc == 0

		# generate report with channel not matching any interface name (invalid)
		result = host.run('stack report dhcpd')
		assert result.rc != 0
		assert 'does not match any other interface' in result.stderr

	def test_invalid_ipmi_channel(self, host):
		result = host.run('stack add host interface frontend-0-0 interface=ipmi channel=1')
		assert result.rc == 0

		# generate report with channeled ipmi interface lacking IP
		result = host.run('stack report dhcpd')
		assert result.rc != 0
		assert 'has a channel but no IP' in result.stderr

