import json
from textwrap import dedent


class TestListApplianceXML:
	def test_list_appliance__xml_invalid(self, host):
		result = host.run('stack list appliance xml test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid appliance
			[appliance ...]
		''')

	def test_list_appliance_xml_no_args(self, host):
		# Check the command works and returned a bunch of lines
		result = host.run('stack list appliance xml')
		assert result.rc == 0
		assert len(result.stdout) > 100

		# Pull out the first column of the output
		appliances = {
			line.split(' ', 1)[0]
			for line in result.stdout.split('\n') if line
		}

		# Make sure more than one appliance had output
		assert 'backend' in appliances
		assert 'frontend' in appliances

	def test_list_appliance_xml_one_arg(self, host):
		# Check the command works and returned a bunch of lines
		result = host.run('stack list appliance xml backend')
		assert result.rc == 0
		assert len(result.stdout) > 100

		# Pull out the first column of the output
		appliances = {
			line.split(' ', 1)[0]
			for line in result.stdout.split('\n') if line
		}

		# Make sure only the backend appliance had output
		assert appliances == {'backend'}

	def test_list_appliance_xml_multiple_args(self, host):
		# Check the command works and returned a bunch of lines
		result = host.run('stack list appliance xml frontend backend')
		assert result.rc == 0
		assert len(result.stdout) > 100

		# Pull out the first column of the output
		appliances = {
			line.split(' ', 1)[0]
			for line in result.stdout.split('\n') if line
		}

		# Make sure only the backend and frontend appliance had output
		assert appliances == {'backend', 'frontend'}
