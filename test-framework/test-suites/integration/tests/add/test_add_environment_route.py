import pytest

class TestAddEnvironmentRoute:
	def test_add_environment_route(self, host):
		result = host.run('stack add environment test')
		assert result.rc == 0

		result = host.run('stack add environment route test address=test gateway=test')
		assert result.rc == 0

		result = host.run('stack list environment route output-format=json')
		assert result.rc == 0
		with open('/export/test-files/add/add_environment_route_output.json') as f:
			assert result.stdout == f.read()

