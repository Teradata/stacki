import json
from textwrap import dedent

class TestReportHostRepo:
	def test_no_args(self, host, host_os, host_repo_file):
		# get the frontend box's pallets, so we aren't assuming a count
		result = host.run('stack list box pallet frontend output-format=json')
		assert result.rc == 0
		pal_count = len(json.loads(result.stdout))
		result = host.run('stack report host repo')
		assert result.rc == 0
		# default repofile should be two lines xml tags, one bash command line, and 4xN repo options lines
		assert len(result.stdout.splitlines()) >= (4 * pal_count + 3)

		if host_os == 'sles':
			last_line = 'zypper clean --all'
		elif host_os == 'redhat':
			last_line = 'yum clean all'
		# TODO ubuntu elif host_os == 'ubuntu':

		first_line = f'<stack:file stack:name="{host_repo_file}">'

		assert result.stdout.splitlines()[0] == first_line
		assert result.stdout.splitlines()[-1] == last_line

	def test_with_repo(self, host, host_os, host_repo_file, add_host, add_repo, add_box):
		result = host.run('stack enable repo test box=test')
		assert result.rc == 0
		result = host.run('stack set host box backend-0-0 box=test')
		assert result.rc == 0
		
		result = host.run('stack report host repo backend-0-0')
		assert result.rc == 0
		# default repofile should be two lines xml tags, one bash command line

		if host_os == 'sles':
			last_line = 'zypper clean --all'
		elif host_os == 'redhat':
			last_line = 'yum clean all'
		# TODO ubuntu elif host_os == 'ubuntu':

		output_single_repo = dedent(f'''\
			<stack:file stack:name="{host_repo_file}">
			[test]
			name=test
			baseurl=test_url
			type=rpm-md
			gpgcheck=0
			</stack:file>
			{last_line}
			'''
		)
		assert result.stdout == output_single_repo

		# add another
		add_repo('test2', 'test_url2', gpgkey='some.asc', gpgcheck=True, assumeyes=True)
		result = host.run('stack enable repo test2 box=test')
		assert result.rc == 0

		result = host.run('stack report host repo backend-0-0')
		assert result.rc == 0
		assert result.stdout == dedent(f'''\
			<stack:file stack:name="{host_repo_file}">
			[test]
			name=test
			baseurl=test_url
			type=rpm-md
			gpgcheck=0

			[test2]
			name=test2
			baseurl=test_url2
			type=rpm-md
			assumeyes=1
			gpgkey=some.asc
			gpgcheck=1
			</stack:file>
			{last_line}
			'''
		)

		result = host.run('stack disable repo test2 box=test')
		assert result.rc == 0

		result = host.run('stack set repo test gpgcheck=True')
		assert result.rc == 0

		# now update the remaining repo and ensure the report changes
		result = host.run('stack report host repo backend-0-0')
		assert result.rc == 0
		assert result.stdout == output_single_repo.replace('gpgcheck=0', 'gpgcheck=1')

	def test_repo_templating(self, host, host_os, host_repo_file, add_host, add_repo, add_box):
		''' test that the repo templating feature works correctly '''
		result = host.run('stack set repo test url="http://{{ Kickstart_PrivateAddress }}/test"')
		assert result.rc == 0

		# setup the box
		result = host.run('stack set host box backend-0-0 box=test')
		assert result.rc == 0
		result = host.run('stack enable repo test box=test')
		assert result.rc == 0
		result = host.run('stack list box test output-format=json')
		assert result.rc == 0

		assert json.loads(result.stdout) == [
			{
				"name": "test",
				"os": host_os,
				"pallets": "",
				"carts": "",
				"repos": "test"
			}
		]


		# list commands should display the non-rendered data
		result = host.run('stack list repo test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "test",
				"alias": "test",
				"url": "http://{{ Kickstart_PrivateAddress }}/test"
			}
		]

		# now grab the attribute
		result = host.run('stack list host attr backend-0-0 attr=Kickstart_PrivateAddress output-format=json')
		assert result.rc == 0
		attr = json.loads(result.stdout)[0]['value']

		if host_os == 'sles':
			last_line = 'zypper clean --all'
		elif host_os == 'redhat':
			last_line = 'yum clean all'
		# TODO ubuntu elif host_os == 'ubuntu':

		# report commands should show the rendered template with the variable substituted
		result = host.run('stack report host repo backend-0-0')
		assert result.rc == 0
		assert result.stdout == dedent(f'''\
			<stack:file stack:name="{host_repo_file}">
			[test]
			name=test
			baseurl=http://{attr}/test
			type=rpm-md
			gpgcheck=0
			</stack:file>
			{last_line}
			'''
		)
