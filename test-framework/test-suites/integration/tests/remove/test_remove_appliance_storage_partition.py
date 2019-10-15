import json
from textwrap import dedent


class TestRemoveApplianceStoragePartition:
	def test_no_args(self, host):
		result = host.run('stack remove appliance storage partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" argument is required
			{appliance ...} [device=string] [mountpoint=string]
		''')

	def test_remove(self, host):
		# Add our partition config
		result = host.run(
			'stack add appliance storage partition backend device=sda mountpoint=/ '
			'size=1024 type=ext4 options=test_options partid=1'
		)
		assert result.rc == 0

		# Make sure it got added
		result = host.run('stack list appliance storage partition backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"appliance": "backend",
			"device": "sda",
			"partid": 1,
			"mountpoint": "/",
			"size": 1024,
			"fstype": "ext4",
			"options": "test_options"
		}]

		# Now remove it
		result = host.run('stack remove appliance storage partition backend device=sda mountpoint=/')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list appliance storage partition backend')
		assert result.rc == 0
		assert result.stdout == ''
