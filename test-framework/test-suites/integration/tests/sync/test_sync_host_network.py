def test_sync_host_network_backend(host, add_host, revert_etc):
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
