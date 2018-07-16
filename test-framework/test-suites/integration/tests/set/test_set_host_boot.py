import pytest

class TestSetHostBoot:
	def test_set_host_boot_with_valid_but_empty_appliance(self, host):
		result = host.run('stack add appliance foo')
		assert result.rc == 0

		result = host.run('stack set host boot action=install a:foo')
		assert result.rc == 0
