import json
from textwrap import dedent


class TestAddHostStoragePartition:
	def test_no_args(self, host):
		result = host.run('stack add host storage partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_all_params(self, host, add_host):
		result = host.run(
			'stack add host storage partition backend-0-0 device=sda mountpoint=/ '
			'size=1024 type=ext4 options=test_options partid=1'
		)
		assert result.rc == 0

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
