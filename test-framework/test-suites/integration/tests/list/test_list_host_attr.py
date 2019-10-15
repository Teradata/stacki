import json
from operator import itemgetter
import os
from itertools import groupby


class TestListHostAttr:
	def test_invalid(self, host):
		result = host.run('stack list host attr test')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

	def test_no_args_frontend_only(self, host):
		result = host.run('stack list host attr output-format=json')
		assert result.rc == 0
		attr_obj = json.loads(result.stdout)

		# with no other hosts in the db, these commands produce identical output
		result = host.run('stack list host attr localhost output-format=json')
		assert result.rc == 0
		json.loads(result.stdout) == attr_obj

		# test appliance selector, too
		result = host.run('stack list host attr a:frontend output-format=json')
		assert result.rc == 0
		json.loads(result.stdout) == attr_obj

		# there should be exactly one host
		assert len({row['host'] for row in attr_obj}) == 1

	def test_with_backend(self, host, add_host):
		result = host.run('stack list host attr output-format=json')
		assert result.rc == 0
		attr_obj = json.loads(result.stdout)

		# with other hosts in the db, this will be different
		result = host.run('stack list host attr localhost output-format=json')
		assert result.rc == 0
		json.loads(result.stdout) != attr_obj

		# test appliance selector, too
		result = host.run('stack list host attr a:frontend output-format=json')
		assert result.rc == 0
		json.loads(result.stdout) != attr_obj

		# both selectors should work together, though
		result = host.run('stack list host attr a:frontend a:backend output-format=json')
		assert result.rc == 0
		json.loads(result.stdout) == attr_obj

		# both hostnames specified should be the same as none by default
		result = host.run('stack list host attr localhost backend-0-0 output-format=json')
		assert result.rc == 0
		json.loads(result.stdout) == attr_obj

		# there should be exactly two hosts
		assert len({row['host'] for row in attr_obj}) == 2

	def test_common_with_only_frontend(self, host):
		result = host.run('stack list host attr display=common output-format=json')
		assert result.rc == 0
		attr_obj = json.loads(result.stdout)

		# there should be one "host" called '_common_'
		assert len({row['host'] for row in attr_obj}) == 1
		assert attr_obj[0]['host'] == '_common_'

	def test_distinct_with_multiple_hosts(self, host, add_host):
		result = host.run('stack list host attr display=distinct output-format=json')
		assert result.rc == 0
		attr_obj = json.loads(result.stdout)

		host_attrs = {
			k: {i['attr']: i['value'] for i in v}
			for k, v in groupby(attr_obj, itemgetter('host'))
		}

		# don't hardcode FE hostname
		fe_hostname = [h for h in host_attrs if h != 'backend-0-0'].pop()
		assert len(host_attrs) == 2
		assert {'backend-0-0', fe_hostname} == set(host_attrs)

		# some keys will only be in common (by default)
		assert 'Kickstart_PrivateRootPassword' not in host_attrs[fe_hostname]
		assert 'Kickstart_PrivateRootPassword' not in host_attrs['backend-0-0']
		# some keys will always be distinct
		assert 'hostname' in host_attrs['backend-0-0']
		# backend doesn't have a hostaddr here
		assert 'hostaddr' in host_attrs[fe_hostname]

		result = host.run('stack add host attr backend-0-0 attr=foo value=bar')
		assert result.rc == 0

		result = host.run('stack list host attr display=distinct output-format=json')
		assert result.rc == 0
		new_attr_obj = json.loads(result.stdout)

		new_host_attrs = {
			k: {i['attr']: i['value'] for i in v}
			for k, v in groupby(new_attr_obj, itemgetter('host'))
		}

		assert len(new_host_attrs['backend-0-0']) == len(host_attrs['backend-0-0']) + 1
		assert len(new_host_attrs[fe_hostname]) == len(host_attrs[fe_hostname])

		result = host.run('stack list host attr display=common output-format=json')
		assert result.rc == 0
		common_attr_obj = json.loads(result.stdout)

		common_host_attrs = {
			k: {i['attr']: i['value'] for i in v}
			for k, v in groupby(common_attr_obj, itemgetter('host'))
		}

		# the set of common attrs and distinct attrs should never overlap
		assert set(common_host_attrs['_common_']).isdisjoint(new_host_attrs['backend-0-0'])

	def test_common_with_multiple_hosts_single_attr_param(self, host, add_host):
		result = host.run('stack list host attr display=distinct attr=hostname output-format=json')
		assert result.rc == 0
		attr_obj = json.loads(result.stdout)

		# only two hosts, no common attrs here
		assert len({row['host'] for row in attr_obj}) == 2

		result = host.run('stack list host attr display=common attr=rank output-format=json')
		assert result.rc == 0
		attr_obj = json.loads(result.stdout)

		# by default these will resolve to the same, so only common will be listed
		assert {row['host'] for row in attr_obj} == {'_common_'}

	def test_scope_resolving(self, host, add_host, add_environment, host_os, test_file):
		# Add our host to the test environment
		result = host.run('stack set host environment backend-0-0 environment=test')
		assert result.rc == 0

		# Add a bunch of attrs to get applied to the host, in different scopes
		result = host.run(
			'stack add attr attr=test.global value=test_1'
		)
		assert result.rc == 0

		result = host.run(
			'stack add appliance attr backend attr=test.appliance value=test_2'
		)
		assert result.rc == 0

		result = host.run(
			f'stack add os attr {host_os} attr=test.os value=test_3'
		)
		assert result.rc == 0

		result = host.run(
			'stack add environment attr test attr=test.environment value=test_4'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host attr backend-0-0 attr=test.host value=test_5'
		)
		assert result.rc == 0

		# Add a bunch of attrs that will be overridden to just one output
		result = host.run(
			'stack add attr attr=test.override value=test_6'
		)
		assert result.rc == 0

		result = host.run(
			'stack add appliance attr backend attr=test.override value=test_7'
		)
		assert result.rc == 0

		result = host.run(
			f'stack add os attr {host_os} attr=test.override value=test_8'
		)
		assert result.rc == 0

		result = host.run(
			'stack add environment attr test attr=test.override value=test_9'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host attr backend-0-0 attr=test.override value=test_10'
		)
		assert result.rc == 0

		# Now list all the host attrs and see if they match what we expect
		result = host.run(
			"stack list host attr backend-0-0 attr='test.*' output-format=json"
		)
		assert result.rc == 0

		with open(test_file('list/host_attr_scope_resolving.json')) as output:
			assert json.loads(result.stdout) == json.loads(output.read())

	def test_scope_no_enviroment(self, host, add_host, test_file):
		# Create some more hosts
		add_host('backend-0-1', '0', '1', 'backend')
		add_host('backend-0-2', '0', '2', 'backend')

		# Add a route to each host
		result = host.run(
			'stack add host attr backend-0-0 attr=test.backend_0 value=test_0'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host attr backend-0-1 attr=test.backend_1 value=test_1'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host attr backend-0-2 attr=test.backend_2 value=test_2'
		)
		assert result.rc == 0

		# Now list all the host attrs and see if they match what we expect
		result = host.run(
			"stack list host attr backend-0-0 attr='test.*' output-format=json"
		)
		assert result.rc == 0

		with open(test_file('list/host_attr_scope_no_enviroment.json')) as output:
			assert json.loads(result.stdout) == json.loads(output.read())

	def test_normal_user_no_shadow(self, host, add_host):
		# Add a shadow attr
		result = host.run('stack set host attr backend-0-0 attr=test value=True shadow=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list host attr backend-0-0 attr=test shadow=True output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'host': 'backend-0-0',
			'scope': 'host',
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
				'list host attr backend-0-0 attr=test shadow=True output-format=json'
			)

		assert result.rc == 0
		assert result.stdout == ""

	def test_const_overwrite(self, host, add_host):
		result = host.run('stack set host attr backend-0-0 attr=const_overwrite value=False')
		assert result.rc == 0

		# Now overwrite the os attribute
		result = host.run('stack set host attr backend-0-0 attr=os value=test')
		assert result.rc == 0

		# Confirm we have overwritten it
		result = host.run('stack list host attr backend-0-0 attr=os output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'os',
			'host': 'backend-0-0',
			'scope': 'host',
			'type': 'var',
			'value': 'test'
		}]

		# A non-overwritten const should return as normal
		result = host.run('stack list host attr backend-0-0 attr=rack output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'rack',
			'host': 'backend-0-0',
			'scope': 'host',
			'type': 'const',
			'value': '0'
		}]
