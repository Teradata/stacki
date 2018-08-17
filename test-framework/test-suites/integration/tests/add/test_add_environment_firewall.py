import pytest

class TestAddEnvironmentFirewall:
	def test_add_environment_firewall(self, host):
		result = host.run('stack add environment test')
		assert result.rc == 0

		result = host.run('stack add environment firewall test action=ACCEPT chain=INPUT protocol=all service=all network=private rulename=test')
		assert result.rc == 0

		result = host.run('stack list environment firewall output-format=json')
		assert result.rc == 0
		with open('/export/test-files/add/add_environment_firewall_output.json') as f:
			assert result.stdout == f.read()

