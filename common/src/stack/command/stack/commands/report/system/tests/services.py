def test_apache_enabled_and_running(host):
	apache = host.service('httpd')
	assert apache.is_enabled
	assert apache.is_running

def test_mariadb_enabled_and_running(host):
	mariadb = host.service('mariadb')
	assert mariadb.is_enabled
	assert mariadb.is_running

def test_xinetd_enabled_and_running(host):
	xinetd = host.service('xinetd')
	assert xinetd.is_enabled
	assert xinetd.is_running

def test_ludicrous_server_enabled_and_running(host):
	ludicrous = host.service('ludicrous-server')
	assert ludicrous.is_enabled
	assert ludicrous.is_running

def test_dhcp_enabled_and_running(host):
	dhcp = host.service('dhcpd')
	assert dhcp.is_enabled
	assert dhcp.is_running
