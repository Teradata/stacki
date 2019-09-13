import stack.api

def test_sync_host_network_hosts(host):
	# TODO fixture for restoring host files???
	''' sync host network should also sync /etc/hosts '''
	# get the frontend's hostfilec
	with open('/etc/hosts') as fi:
		hostsfiledata = fi.read()

	# get the number of hosts
	hosts = [h['host'] for h in stack.api.Call('list.host', ['a:backend'])]
	assert len(hosts) > 0

	def assert_files_diff():
		''' verify files modified '''
		for this_host in hosts:
			# grep for a known string
			result = host.run(rf"ssh {this_host} grep \'curatorial nonsense garbage\' /etc/hosts")
			assert result.rc == 0
			# ensure hosts and its backup differ
			result = host.run(f'ssh {this_host} cmp /etc/hosts /etc/hosts.bak')
			assert result.rc != 0

	# backup hosts and then write garbage to it
	result = host.run("stack run host a:backend command='cp /etc/hosts /etc/hosts.bak'")
	assert result.rc == 0
	garbage_str = 'curatorial nonsense garbage'
	result = host.run(f'''stack run host a:backend command='printf "\n# {garbage_str}\n" >> /etc/hosts' ''')
	assert result.rc == 0
	# write the frontend's version for later comparison
	result = host.run(f"stack iterate host a:backend command='scp /etc/hosts %:/etc/hosts.fe'")

	# verify files modified
	assert_files_diff()

	# run sync host network without manage.hostsfile (defaults to False)
	result = host.run('stack sync host network a:backend')
	assert result.rc == 0

	# verify files still modified
	assert_files_diff()

	# enable syncing hostfile and call sync host network
	result = host.run('stack set host attr a:backend attr=manage.hostsfile value=True')
	assert result.rc == 0
	result = host.run('stack set host attr a:backend attr=sync.hostsfile value=True')
	assert result.rc == 0
	result = host.run('stack sync host network a:backend')
	assert result.rc == 0

	result = host.run(f'''stack iterate host a:backend command='grep "curatorial nonsense garbage" /etc/hosts' ''')
	assert result.rc == 0
	output = result.stdout.strip().splitlines()
	assert len(output) == 0

	# verify hostfile clobber
	for this_host in hosts:
		result = host.run(f'ssh {this_host} cmp /etc/hosts /etc/hosts.fe')
		assert result.rc == 0

	# cleanup
	result = host.run("stack run host a:backend command='mv /etc/hosts.bak /etc/hosts'")
	result = host.run("stack run host a:backend command='rm /etc/hosts.fe'")
	result = host.run('stack remove host attr a:backend attr=manage.hostsfile')
	result = host.run('stack remove host attr a:backend attr=sync.hostsfile')
	assert result.rc == 0
