import pytest
import json

class TestDumpApi:

	"""
	Test that dumping the api data works properly by adding some api information
	then dumping it and checking that it is valid
	"""

	def test_dump_api(self, host):

		results = host.run('stack add api group testgroup1')
		results = host.run('stack add api group testgroup2')
		results = host.run('stack add api user testuser1 admin=false group=testgroup1')
		results = host.run('stack add api user testuser2 admin=false group=testgroup1')
		results = host.run('stack add api group perms testgroup1 perm=dump')
		results = host.run('stack add api group perms testgroup2 perm=load*')
		results = host.run('stack add api group perms testgroup2 perm=add*')
		results = host.run('stack add api user perms testuser1 perm=report*')
		results = host.run('stack add api blacklist command command="remove host interface"')
		results = host.run('stack add api blacklist command command="add host interface"')

		results = host.run('stack dump api')
		assert results.rc == 0
		dump = json.loads(results.stdout)

		found1 = False
		found2 = False
		for group in dump['api']['group']:
			name = group['name']
			perm = group['perm']
			if name == 'testgroup1':
				found1 = True
				assert 'dump' in perm
			elif name == 'testgroup2':
				found2 = True
				assert 'load*' and 'add*' in perm
		assert found1
		assert found2

		found1 = True
		found2 = True
		for user in dump['api']['user']:
			name   = user['name']
			admin  = user['admin']
			group  = user['group']
			perm   = user['perm']
			if user == 'testuser1':
				found1 = True
				assert admin == False
				assert 'testgroup1' in group
				assert 'report*' in perm
			if name == 'testuser2':
				found2 = True
				assert admin == False
				assert 'testgroup1' in group
				assert not perm
		assert found1
		assert found2

		assert 'remove host interface' and 'add host interface' in dump['api']['blacklist']
