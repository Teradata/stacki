import json
from textwrap import dedent


class TestAddOSStoragePartition:
	def test_no_args(self, host):
		result = host.run('stack add os storage partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "os" argument is required
			{os ...} {device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_all_params(self, host):
		result = host.run(
			'stack add os storage partition sles device=sda mountpoint=/ '
			'size=1024 type=ext4 options=test_options partid=1'
		)
		assert result.rc == 0

		result = host.run('stack list os storage partition sles output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"os": "sles",
			"device": "sda",
			"partid": 1,
			"mountpoint": "/",
			"size": 1024,
			"fstype": "ext4",
			"options": "test_options"
		}]
