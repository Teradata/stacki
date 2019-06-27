def test_sync_dns(host, revert_etc):
	named = host.service('named')

	# by default, stacki creates a basic named file, but it should not be running
	assert not named.is_running

	# the test framework does not set the private network (only network present during test) dns=True
	# so list network dns=True should return nothing
	result = host.run('stack list network dns=True')
	assert result.rc == 0
	assert result.stdout == ''

	# nothing is using named, shut it down and verify sync doesn't restart it
	host.run('systemctl stop named')
	result = host.run('stack sync dns')
	assert result.rc == 0
	assert not named.is_running

	# setting the network to dns=true, stopping named and re-syncing should start named
	result = host.run('stack set network dns private dns=true')
	assert result.rc == 0

	assert not named.is_running
	result = host.run('stack sync dns')
	assert result.rc == 0
	assert named.is_running
