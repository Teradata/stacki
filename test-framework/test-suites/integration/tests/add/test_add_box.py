import json
from textwrap import dedent


class TestAddBox:
	def test_no_args(self, host):
		result = host.run('stack add box')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "box" argument must be unique
			{box} [os=string]
		''')

	def test_no_os(self, host, host_os):
		# Add the box
		result = host.run('stack add box test')
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list box test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "test",
				"os": host_os,
				"pallets": "",
				"carts": "",
				"repos": "",
			}
		]

	def test_with_os(self, host):
		# Add the box (with an OS we won't be testing under)
		result = host.run('stack add box test os=ubuntu')
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list box test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "test",
				"os": "ubuntu",
				"pallets": "",
				"carts": "",
				"repos": "",
			}
		]
	
	def test_with_invalid_os(self, host):
		result = host.run('stack add box test os=foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "foo" argument is not a valid OS
			{box} [os=string]
		''')
	
	def test_duplicate(self, host):
		result = host.run('stack add box default')
		assert result.rc == 255
		assert result.stderr == 'error - box "default" exists\n'
