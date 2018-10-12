class TestReportHost:
	def test_exclude_interface_ip_no_network(self, host, add_host_with_interface):
		# set interface IP, but not network
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=1.1.1.1')
		assert result.rc == 0
		# report should exclude incorrectly configured interface
		result = host.run('stack report host interface')
		assert result.rc == 0
		assert 'backend-0-0' not in result.stdout
