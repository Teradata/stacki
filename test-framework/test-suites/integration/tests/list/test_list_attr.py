import json
import os
import re
from textwrap import dedent


class TestListAttr:
	def test_invalid_scope(self, host):
		result = host.run('stack list attr scope=foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "scope" parameter is not valid
			[attr=string] [shadow=boolean]
		''')

	def test_with_shadow(self, host):
		result = host.run('stack list attr output-format=json')
		assert result.rc == 0
		list_attr_output_json = json.loads(result.stdout)

		result = host.run('stack list attr shadow=True output-format=json')
		assert result.rc == 0
		list_attr_shadow_True_output_json = json.loads(result.stdout)

		assert list_attr_output_json == list_attr_shadow_True_output_json

	def test_without_shadow(self, host):
		result = host.run('stack list attr shadow=False output-format=json')
		assert result.rc == 0

		list_attr_shadow_False_output_json = json.loads(result.stdout)
		assert self.validate_attr_list(list_attr_shadow_False_output_json)

		result = host.run('stack list attr shadow=True output-format=json')
		assert result.rc == 0

		list_attr_shadow_True_output_json = json.loads(result.stdout)
		assert list_attr_shadow_False_output_json != list_attr_shadow_True_output_json

	# Checks if any attr in the attr list is of the type shadow and it's corresponding value is Null or None
	def validate_attr_list(self, attr_json_file):
		for attr in attr_json_file:
			if attr['type']=='shadow' :
				if attr['value'] is not None:
					return False
		return True

	def test_intrinsic(self, host, add_network, host_os, test_file):
		# Add a public network
		add_network("public", "192.168.100.0")

		# Add a new interface on the frontend for the public network
		result = host.run(
			'stack add host interface a:frontend interface=eth3 '
			'network=public ip=192.168.100.2 mac=00:11:22:33:44:55'
		)

		# List our const global attrs
		result = host.run('stack list attr var=False output-format=json')
		assert result.rc == 0

		# Assert there is version, then blank it out
		attrs = json.loads(result.stdout)
		for attr in attrs:
			if attr['attr'] == 'version':
				assert attr['value'] and attr['value'].strip()
				attr['value'] = ''
				break

		with open(test_file(f'list/attr_intrinsic_{host_os}.json')) as output:
			assert attrs == json.loads(output.read())

	def test_normal_user_no_shadow(self, host):
		# Add a shadow attr
		result = host.run('stack set attr attr=test value=True shadow=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list attr attr=test shadow=True output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'scope': 'global',
			'type': 'shadow',
			'value': 'True'
		}]

		# Give the vagrant user access to list commands
		result = host.run("stack set access command='list *' group=vagrant")
		assert result.rc == 0

		# Now make sure a normal user can't see it. Gotta preserve the
		# PYTEST_XDIST_WORKER environment variable so we point at the
		# correct database copy.
		injected_env = ""
		if 'PYTEST_XDIST_WORKER' in os.environ:
			injected_env = "PYTEST_XDIST_WORKER=" + os.environ['PYTEST_XDIST_WORKER']

		with host.sudo("vagrant"):
			result = host.run(
				f'{injected_env} /opt/stack/bin/stack '
				'list attr attr=test shadow=True output-format=json'
			)

		assert result.rc == 0
		assert result.stdout == ""

	def test_no_attrs(self, host):
		# Remove all the global attrs
		result = host.run("stack remove attr attr=*")
		assert result.rc == 0

		# Now list var attrs only, to exercise an edge case code
		# path. It should return no results.
		result = host.run('stack list attr const=false output-format=json')
		assert result.rc == 0
		assert result.stdout == ""
