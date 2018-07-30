import pytest
import json

class TestDumpApi:

        """
        Test that dumping the api data works properly by adding some api information
        then dumping it and checking that it is valid
        """

        def test_dump_api(self, host):

                # first lets add some api info so we know what to look for then we dump
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

                # dump our api information
                results = host.run('stack dump api')
                assert results.rc == 0
                dumped_data = json.loads(results.stdout)

                # check to make sure that the information we just added is in the dump data
                for group, data in dumped_data['api']['group'].items():
                        if group == 'testgroup1':
                                assert 'testuser1' and 'testuser2' in data['users']
                                assert 'dump' in data['permissions']
                        if group == 'testgroup2':
                                assert not data['users']
                                assert 'load*' and 'add*' in data['permissions']

                for user in dumped_data['api']['user']:
                        if user['username'] == 'testuser1':
                                assert user['admin'] == False
                                assert 'testgroup1' in user['groups']
                                assert 'report*' in user['permissions']
                        if user['username'] == 'testuser2':
                                assert user['admin'] == False
                                assert 'testgroup1' in user['groups']
                                assert not user['permissions']
                assert 'remove host interface' and 'add host interface' in dumped_data['api']['blacklist commands']
