import pytest
import os

def test_tftpd_enabled_and_running(host):
	xinetd = host.service('xinetd')
	fbtftpd = host.service('fbtftpd')
	if not xinetd.is_enabled and not fbtftpd.is_enabled:
		err = print("No tftp server is enabled.")
		assert err

	if not xinetd.is_running and not fbtftpd.is_running:
		err = print("No tftp server is running.")
		assert err

SERVICES = [
	'dhcpd',
	'named',
	'rmq-processor',
	'rmq-producer',
	'rmq-publisher',
]

if os.path.exists('/etc/SuSE-release'):
	SERVICES.append('apache2')
	SERVICES.append('mysql')
else:
	SERVICES.append('httpd')
	SERVICES.append('mariadb')

@pytest.mark.parametrize("service,", SERVICES)
def test_service_enabled_and_running(host, service):
	daemon = host.service(service)
	assert daemon.is_enabled
	assert daemon.is_running
