import os


def test_apache_enabled_and_running(host):
	if os.path.exists('/etc/SuSE-release'):
		apache = host.service('apache2')
	else:
		apache = host.service('httpd')

	assert apache.is_enabled
	assert apache.is_running

def test_mariadb_enabled_and_running(host):
	mariadb = host.service('mysql')
	assert mariadb.is_enabled
	assert mariadb.is_running

def test_tftpd_enabled_and_running(host):
	xinetd = host.service('xinetd')
	fbtftpd = host.service('fbtftpd')
	if not xinetd.is_enabled and not fbtftpd.is_enabled:
		err = print("No tftp server is enabled.")
		assert err

	if not xinetd.is_running and not fbtftpd.is_running:
		err = print("No tftp server is running.")
		assert err

def test_dhcp_enabled_and_running(host):
	dhcp = host.service('dhcpd')
	assert dhcp.is_enabled
	assert dhcp.is_running

def test_rmq_processor_enabled_and_running(host):
	rmq_processor = host.service('rmq-processor')
	assert rmq_processor.is_enabled
	assert rmq_processor.is_running

def test_rmq_producer_enabled_and_running(host):
	rmq_producer = host.service('rmq-producer')
	assert rmq_producer.is_enabled
	assert rmq_producer.is_running

def test_rmq_publisher_enabled_and_running(host):
	rmq_publisher = host.service('rmq-publisher')
	assert rmq_publisher.is_enabled
	assert rmq_publisher.is_running
