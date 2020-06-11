import json

class TestListRepo:
	def test_invalid(self, host):
		result = host.run('stack list repo test')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

	def test_args(self, host, add_repo):
		# Add a second repo so we can make sure it is skipped
		add_repo('test2', 'test2url')

		# Run list repo with just the test box
		result = host.run('stack list repo test output-format=json')
		assert result.rc == 0

		# Make sure we got data only for the test box
		repo_data = json.loads(result.stdout)
		assert len(repo_data) == 1
		assert repo_data[0]['name'] == 'test'

		# now get all of them
		# assert both repos are in the list data
		result = host.run('stack list repo output-format=json')
		repo_data = json.loads(result.stdout)
		assert len(repo_data) == 2
		assert {'test', 'test2'} == {repo['name'] for repo in repo_data}

		# now get all of them, by explicitly asking for them
		# assert both repos are in the list data
		result = host.run('stack list repo test test2 output-format=json')
		new_repo_data = json.loads(result.stdout)
		assert len(new_repo_data) == 2
		assert {'test', 'test2'} == {repo['name'] for repo in new_repo_data}

	def test_removed_not_listed(self, host, add_repo, revert_etc):
		# Run list repo with just the test box
		result = host.run('stack list repo test output-format=json')
		assert result.rc == 0

		# Make sure we got data only for the test box
		repo_data = json.loads(result.stdout)
		assert len(repo_data) == 1
		assert repo_data[0]['name'] == 'test'

		result = host.run('stack remove repo test')
		assert result.rc == 0

		# Run list repo again
		result = host.run('stack list repo test output-format=json')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

	def test_expanded_columns(self, host, host_os, add_repo):
		# Run list repo with just the test box
		result = host.run('stack list repo test expanded=true output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "test",
				"alias": "test",
				"url": "test_url",
				"autorefresh": False,
				"assumeyes": False,
				"type": "rpm-md",
				"is_mirrorlist": False,
				"gpgcheck": False,
				"gpgkey": None,
				"os": host_os,
				"pallet name": None
			}
		]

	def test_add_repo_with_pallet(self, host, host_os, add_repo, create_pallet_isos, revert_export_stack_pallets, revert_pallet_hooks, revert_etc):
		result = host.run(f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso')
		#result = host.run(f'stack add pallet /root/minimal-1.0-sles12.x86_64.disk1.iso')
		assert result.rc == 0

		result = host.run('stack list pallet minimal output-format=json')
		assert result.rc == 0

		pallet_data = json.loads(result.stdout)
		assert len(pallet_data) == 1

		# get pallet id, as well as the -'d name in the correct order
		from stack.commands import DatabaseConnection, get_mysql_connection, Command
		from stack.argument_processors.pallet import PalletArgProcessor
		from operator import attrgetter
		p = PalletArgProcessor()
		p.db = DatabaseConnection(get_mysql_connection())
		minimal_pallet = p.get_pallets(args=['minimal'], params=pallet_data[0])[0]
		pallet_name = '-'.join(attrgetter('name', 'version', 'rel', 'os', 'arch')(minimal_pallet))

		# now attach the test repo to the pallet
		result = host.run(f'stack set repo test pallet={minimal_pallet.id}')
		assert result.rc == 0

		# now verify it is attached to that pallet
		result = host.run('stack list repo test expanded=true output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "test",
				"alias": "test",
				"url": "test_url",
				"autorefresh": False,
				"assumeyes": False,
				"type": "rpm-md",
				"is_mirrorlist": False,
				"gpgcheck": False,
				"gpgkey": None,
				"os": host_os,
				"pallet name": pallet_name
			}
		]

		# now verify that removing that pallet removes the repo as well
		result = host.run('stack remove pallet minimal')
		assert result.rc == 0

		result = host.run('stack list repo')
		assert result.rc == 0
		assert result.stdout == ''
