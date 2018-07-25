import pytest
import re

@pytest.mark.usefixtures('revert_database')
class TestSetHostInterfaceMac:
	def test_set_duplicate_mac(self, host):
		result = host.run('stack add host interface frontend-0-0 interface=eth0 mac=00:11:22:33:44:55')
		assert result.rc == 0
		result = host.run('stack add host interface frontend-0-0 interface=eth2 mac=00:11:22:33:44:00')
		# Set interface MAC to that of another MAC in the database (invalid)
		result = host.run('stack set host interface mac frontend-0-0 interface=eth2 mac=00:11:22:33:44:55')
		assert result.rc != 0
		assert re.search(r'MAC ".+" already exists on host', result.stderr) is not None

	def test_reset_mac(self, host):
		result = host.run('stack add host interface frontend-0-0 interface=eth0 mac=00:11:22:33:44:55')
		assert result.rc == 0
		# set interface MAC to its current value
		result = host.run('stack set host interface mac frontend-0-0 interface=eth0 mac=00:11:22:33:44:55')
		assert result.rc == 0

