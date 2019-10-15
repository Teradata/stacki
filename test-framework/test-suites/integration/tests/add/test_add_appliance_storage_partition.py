import json
from textwrap import dedent


class TestAddApplianceStoragePartition:
	def test_no_args(self, host):
		result = host.run('stack add appliance storage partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" argument is required
			{appliance ...} {device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_all_params(self, host):
		result = host.run(
			'stack add appliance storage partition backend device=sda mountpoint=/ '
			'size=1024 type=ext4 options=test_options partid=1'
		)
		assert result.rc == 0

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
