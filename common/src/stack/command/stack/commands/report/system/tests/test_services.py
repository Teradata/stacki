import os


def test_apache_enabled_and_running(host):
	if os.path.exists('/etc/SuSE-release'):
		apache = host.service('apache2')
	else:
		apache = host.service('httpd')

	assert apache.is_enabled
	assert apache.is_running

def test_mariadb_enabled_and_running(host):
	if os.path.exists('/etc/SuSE-release'):
		service_name = 'mysql'
	else:
		service_name = 'mariadb'
	mariadb = host.service(service_name)
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

def test_smq_processor_enabled_and_running(host):
	smq_processor = host.service('smq-processor')
	assert smq_processor.is_enabled
	assert smq_processor.is_running

def test_smq_producer_enabled_and_running(host):
	smq_producer = host.service('smq-producer')
	assert smq_producer.is_enabled
	assert smq_producer.is_running

def test_smq_publisher_enabled_and_running(host):
	smq_publisher = host.service('smq-publisher')
	assert smq_publisher.is_enabled
	assert smq_publisher.is_running
