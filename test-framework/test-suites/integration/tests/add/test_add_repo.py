import json


class TestAddRepo:
	def test_no_args(self, host):
		result = host.run('stack add repo')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

	def test_add_url_is_required(self, host):
		result = host.run('stack add repo test')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

	def test_add_only_one_at_a_time(self, host):
		result = host.run('stack add repo test test2 name=test url=ignore')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

	def test_add_with_name_param(self, host):
		result = host.run('stack add repo test name=test url=ignore')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

	def test_no_alias(self, host, host_os):
		# if alias is not specified, name.replace(' ', '-') is used.
		# Add the repo
		result = host.run('stack add repo "my test" url=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list repo "my test" output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "my test",
				"alias": "my-test",
				"url": "foo"
			}
		]

		# Check expanded columns
		result = host.run('stack list repo "my test" expanded=true output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "my test",
				"alias": "my-test",
				"url": "foo",
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

	def test_with_os(self, host, host_os):
		# Add the box (with an OS we won't be testing under)
		result = host.run('stack add repo test url=foo os=ubuntu')
		assert result.rc == 0

		result = host.run('stack list repo test expanded=true output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "test",
				"alias": "test",
				"url": "foo",
				"autorefresh": False,
				"assumeyes": False,
				"type": "rpm-md",
				"is_mirrorlist": False,
				"gpgcheck": False,
				"gpgkey": None,
				"os": 'ubuntu',
				"pallet name": None
			}
		]
	
	def test_add_duplicate(self, host):
		# attempting to add a dupe is NOT allowed
		result = host.run('stack add repo test url=foo')
		assert result.rc == 0
		result = host.run('stack add repo test url=foo')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')
