import pytest
import re

@pytest.mark.usefixtures('revert_database')
class TestSetHostInterfaceInterface:
	def test_set_duplicate_interface(self, host):
		result = host.run('stack add host interface frontend-0-0 interface=eth0 mac=00:11:22:33:44:55')
		assert result.rc == 0
		# Set host interface name to that of an existing interface on the same host (invalid)
		result = host.run('stack set host interface interface frontend-0-0 interface=eth1 mac=00:11:22:33:44:55')
		assert result.rc != 0
		assert re.search(r'Interface ".+" already exists on host', result.stderr) is not None

	def test_reset_interface(self, host):
		result = host.run('stack add host interface frontend-0-0 interface=eth0 mac=00:11:22:33:44:55')
		assert result.rc == 0
		# Set host interface name to its current value
		result = host.run('stack set host interface interface frontend-0-0 interface=eth0 mac=00:11:22:33:44:55')
		assert result.rc == 0

