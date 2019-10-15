import json
from textwrap import dedent


class TestAddEnvironmentStoragePartition:
	def test_no_args(self, host):
		result = host.run('stack add environment storage partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...} {device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_all_params(self, host, add_environment):
		result = host.run(
			'stack add environment storage partition test device=sda mountpoint=/ '
			'size=1024 type=ext4 options=test_options partid=1'
		)
		assert result.rc == 0

		result = host.run('stack list environment storage partition test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"environment": "test",
			"device": "sda",
			"partid": 1,
			"mountpoint": "/",
			"size": 1024,
			"fstype": "ext4",
			"options": "test_options"
		}]
