import pytest

@pytest.mark.usefixtures('add_host')
def test_sync_host_network_backend(host):
	result = host.run('stack sync host firewall')
	assert 'Could not resolve hostname' in result.stdout
	assert result.rc == 0

def test_sync_host_network_frontend_only(host):
	result = host.run('stack sync host firewall')
	assert result.rc == 0
