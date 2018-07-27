import pytest

@pytest.mark.usefixtures('revert_database')
class TestReportHost:
	@pytest.mark.usefixtures('add_host_with_interface')
	def test_ip_no_network_fails(self, host):
		# set interface IP, but not network
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=1.1.1.1')
		assert result.rc == 0
		# invalid configuration; should error
		result = host.run('stack report host interface')
		assert result.rc != 0
		assert 'has an IP but no network' in result.stderr
