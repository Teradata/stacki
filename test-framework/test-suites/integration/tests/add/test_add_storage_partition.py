import json
from textwrap import dedent


class TestAddStoragePartition:
	def test_no_device(self, host):
		result = host.run('stack add storage partition size=1024')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "device" parameter is required
			{device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_blank_device(self, host):
		result = host.run('stack add storage partition device="" size=1024')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "device" parameter is required
			{device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_no_size(self, host):
		result = host.run('stack add storage partition device=sda')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "size" parameter is required
			{device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_blank_size(self, host):
		result = host.run('stack add storage partition device=sda size=""')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "size" parameter is required
			{device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_invalid_size(self, host):
		result = host.run('stack add storage partition device=sda mountpoint=/ size=recommended')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "size" parameter must be an integer
			{device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_negative_size(self, host):
		result = host.run('stack add storage partition device=sda size=-1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "size" parameter must be >= 0
			{device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_invalid_partid(self, host):
		result = host.run('stack add storage partition device=sda size=1024 partid=foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "partid" parameter must be an integer
			{device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_negative_partid(self, host):
		result = host.run('stack add storage partition device=sda size=1024 partid=-1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "partid" parameter must be >= 0
			{device=string} {size=integer} [mountpoint=string] [options=string] [partid=integer] [type=string]
		''')

	def test_existing_partition(self, host):
		# Add it once
		result = host.run('stack add storage partition device=sda mountpoint=/ size=1024')
		assert result.rc == 0

		# Add it again
		result = host.run('stack add storage partition device=sda mountpoint=/ size=1024')
		assert result.rc == 255
		assert result.stderr == 'error - partition specification for device "sda" and mount point "/" already exists\n'

	def test_minimal(self, host):
		result = host.run('stack add storage partition device=sda size=1024')
		assert result.rc == 0

		result = host.run('stack list storage partition output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"device": "sda",
			"partid": None,
			"mountpoint": None,
			"size": 1024,
			"fstype": None,
			"options": ""
		}]

	def test_all_params(self, host):
		result = host.run(
			'stack add storage partition device=sda mountpoint=/ '
			'size=1024 type=ext4 options=test_options partid=1'
		)
		assert result.rc == 0

		result = host.run('stack list storage partition output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"device": "sda",
			"partid": 1,
			"mountpoint": "/",
			"size": 1024,
			"fstype": "ext4",
			"options": "test_options"
		}]
