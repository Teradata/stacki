import json
from operator import itemgetter
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
