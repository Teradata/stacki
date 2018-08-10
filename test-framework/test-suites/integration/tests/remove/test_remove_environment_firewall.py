import pytest

class TestRemoveEnvironmentFirewall:
	def test_remove_environment_firewall(self, host):
		result = host.run('stack add environment test')
		assert result.rc == 0

		result = host.run('stack add environment firewall test action=ACCEPT chain=INPUT protocol=all service=all network=private rulename=test')
		assert result.rc == 0

		result = host.run('stack remove environment firewall test rulename=test')
		assert result.rc == 0

		result = host.run('stack list environment firewall output-format=json')
		assert result.rc == 0
		assert result.stdout == ''

