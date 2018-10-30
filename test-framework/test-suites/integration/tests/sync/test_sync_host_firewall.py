def test_sync_host_network_backend(host, add_host):
	# create an unreachable host and check the command continues/succeeds even if we can't reach it
	result = host.run('stack sync host firewall')
	assert result.rc == 0

def test_sync_host_network_frontend_only(host):
	result = host.run('stack sync host firewall')
	assert result.rc == 0
