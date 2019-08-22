def test_sync_host_network_backend_without_ifaces(host, add_host, revert_etc):
	# test should pass as sync host network ignores backends without networking
	result = host.run('stack sync host network')
	assert result.rc == 0

def test_sync_host_network_frontend_only(host, revert_etc):
	result = host.run('stack sync host network localhost')
	assert result.rc == 0

def test_sync_host_network_resolv(host, revert_etc):
	''' sync host network should rewrite resolv.conf '''
	# RHEL (and possibly others) writes garbage to /etc/resolv.conf
	# Since the FE has the same data, just call `sync host network localhost`
	# this changes the original file, but the purpose of the test is to verify
	# that we will overwrite resolv.conf

	# call sync host network
	result = host.run('stack sync host network localhost')
	assert result.rc == 0

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
	result = host.run('stack sync host')
	assert result.rc == 0

	with open('/etc/hosts') as fi:
		hostsfiledata = fi.read()
		assert og_hostsfiledata == hostsfiledata
