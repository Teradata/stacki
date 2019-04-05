import json
from textwrap import dedent


class TestRemoveEnvironmentStoragePartition:
	def test_no_args(self, host):
		result = host.run('stack remove environment storage partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...} [device=string] [mountpoint=string]
		''')

	def test_remove(self, host, add_environment):
		# Add our partition config
		result = host.run(
			'stack add environment storage partition test device=sda mountpoint=/ '
			'size=1024 type=ext4 options=test_options partid=1'
		)
		assert result.rc == 0

		# Make sure it got added
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

		# Now remove it
		result = host.run('stack remove environment storage partition test device=sda mountpoint=/')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list environment storage partition test')
		assert result.rc == 0
		assert result.stdout == ''
