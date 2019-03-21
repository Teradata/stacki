import pytest
import os
import stack.api

SERVICES = [
	'dhcpd',
	'named',
	'rsyslog',
	'smq-processor',
	'smq-producer',
	'smq-publisher',
	'sshd',
]

SKIP_SVCS = {}

HOST_OS = 'unknown'

# handle os-specific service names
if os.path.exists('/etc/SuSE-release'):
	HOST_OS = 'sles'
	SERVICES.append('apache2')
	SERVICES.append('mysql')
elif os.path.exists('/etc/redhat-release'):
	HOST_OS = 'redhat'
	SERVICES.append('httpd')
	SERVICES.append('mariadb')

# only check named if it actually needs to be running
results = stack.api.Call('list.network', ['dns=true'])
if not results:
	SKIP_SVCS['named'] = 'named should only be running if a network is set to dns=true'

@pytest.mark.parametrize("service,", SERVICES)
def test_service_enabled_and_running(host, service):
	if service in SKIP_SVCS:
		pytest.skip(SKIP_SVCS[service])

	daemon = host.service(service)
	assert daemon.is_enabled
	assert daemon.is_running

def test_tftpd_enabled_and_running(host):
	xinetd = host.service('xinetd')
	fbtftpd = host.service('fbtftpd')
	if not xinetd.is_enabled and not fbtftpd.is_enabled:
		err = print("No tftp server is enabled.")
		assert err

	if not xinetd.is_running and not fbtftpd.is_running:
		err = print("No tftp server is running.")
		assert err

def test_logrotate_enabled_and_configured(host):
	# note, logrotate doesn't stay running, and only runs on sles?
	if HOST_OS == 'sles':
		daemon = host.service('logrotate')
		assert daemon.is_enabled

	result = host.run('/usr/sbin/logrotate /etc/logrotate.conf -d')
	assert result.exit_status == 0, "logrotate configuration is invalid"
