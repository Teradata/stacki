def test_sync_host_network_backend_without_ifaces(host, add_host, revert_etc):
	# test should pass as sync host network ignores backends without networking
	result = host.run('stack sync host network')
	assert result.rc == 0

def test_sync_host_network_frontend_only(host, revert_etc):
	result = host.run('stack sync host network localhost')
	assert result.rc == 0

def test_sync_host_network_resolv(host, revert_etc):
	''' sync host network should also sync resolv.conf '''
	# write garbage to it
	with open('/etc/resolv.conf', 'a+') as fi:
		fi.seek(0)
		og_resolv_data = fi.read()
		fi.write('# curatorial nonsense garbage')
		fi.seek(0)
		garbagedata = fi.read()
		assert garbagedata != og_resolv_data

	# call sync host network
	result = host.run('stack sync host network localhost')
	assert result.rc == 0

	# verify we actually do rewrite resolv.conf
	with open('/etc/resolv.conf') as fi:
		assert og_resolv_data == fi.read()

def test_ensure_hostfile_matches_database(host, revert_etc):
	# ensure starting hostfile is what the FE would write
	# get the og hostfile
	with open('/etc/hosts') as fi:
		og_hostsfiledata = fi.read()

	# this command will always overwrite /etc/hosts
	result = host.run('stack report host | stack report script | bash')
	assert result.rc == 0

	with open('/etc/hosts') as fi:
		hostsfiledata = fi.read()
		assert og_hostsfiledata == hostsfiledata


def test_sync_host_network_hosts(host, revert_etc):
	''' sync host network should also sync /etc/hosts '''
	with open('/etc/hosts') as fi:
		hostsfiledata = fi.read()

	# write garbage to it
	with open('/etc/hosts', 'a+') as fi:
		fi.write('# curatorial nonsense garbage')
		fi.seek(0)
		garbagehostsdata = fi.read()
		assert garbagehostsdata != hostsfiledata

	# run sync host network without sync.hosts (defaults to False)
	result = host.run('stack sync host network localhost')
	assert result.rc == 0
	# verify hostfile same
	with open('/etc/hosts') as fi:
		assert garbagehostsdata == fi.read()

	# enable syncing hostfile and call sync host network
	result = host.run('stack set host attr localhost attr=sync.hosts value=True')
	assert result.rc == 0
	result = host.run('stack sync host network localhost')
	assert result.rc == 0

	# verify hostfile clobber
	with open('/etc/hosts') as fi:
		assert hostsfiledata == fi.read()

def test_sync_host_network_hosts_with_synchosts(host, revert_etc):
	''' sync host network should sync /etc/hosts only if sync.hosts==True '''
	with open('/etc/hosts') as fi:
		hostsfiledata = fi.read()

	# write garbage to it
	with open('/etc/hosts', 'a+') as fi:
		fi.write('# curatorial nonsense garbage')
		fi.seek(0)
		garbagehostsdata = fi.read()
		assert garbagehostsdata != hostsfiledata

	# disable syncing hostfile and sync
	result = host.run('stack set host attr localhost attr=sync.hosts value=False')
	assert result.rc == 0
	result = host.run('stack sync host')
	assert result.rc == 0
	# verify hostfile same
	with open('/etc/hosts') as fi:
		assert garbagehostsdata == fi.read()

	# enable syncing hostfile and sync
	result = host.run('stack set host attr localhost attr=sync.hosts value=True')
	assert result.rc == 0
	result = host.run('stack sync host')
	assert result.rc == 0

	# verify hostfile clobber
	with open('/etc/hosts') as fi:
		assert hostsfiledata == fi.read()
