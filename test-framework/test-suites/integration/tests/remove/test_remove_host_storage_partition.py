import json
from textwrap import dedent


class TestRemoveHostStoragePartition:
	def test_no_args(self, host):
		result = host.run('stack remove host storage partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} [device=string] [mountpoint=string]
		''')

	def test_remove(self, host, add_host):
		# Add our partition config
		result = host.run(
			'stack add host storage partition backend-0-0 device=sda mountpoint=/ '
			'size=1024 type=ext4 options=test_options partid=1'
		)
		assert result.rc == 0

		# Make sure it got added
		result = host.run('stack list host storage partition backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"host": "backend-0-0",
			"device": "sda",
			"partid": 1,
			"mountpoint": "/",
			"size": 1024,
			"fstype": "ext4",
			"options": "test_options",
			"source": "H"
		}]

		# Now remove it
		result = host.run('stack remove host storage partition backend-0-0 device=sda mountpoint=/')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list host storage partition backend-0-0')
		assert result.rc == 0
		assert result.stdout == ''
