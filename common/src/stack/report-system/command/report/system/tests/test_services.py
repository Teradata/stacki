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
	'chronyd',
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
	tftpsocket = host.service('tftp.socket')
	assert tftpsocket.is_enabled or xinetd.is_enabled or fbtftpd.is_enabled, "No tftp server is enabled."
	assert tftpsocket.is_running or xinetd.is_running or fbtftpd.is_running, "No tftp server is running."

def test_logrotate_service_enabled(host):
	"""Test that the logrotate service is enabled."""
	# On RedHat, there's a cronjob in /etc/cron.daily/logrotate.
	if HOST_OS == "redhat":
		assert host.file("/etc/cron.daily/logrotate").exists
	# There seems to be a logrotate service on SLES.
	else:
		assert host.service("logrotate").is_enabled

def test_logrotate_configuration_valid(host):
	"""Runs logrotate in debug mode to confirm the logrotate files have no errors."""
	result = host.run("logrotate --debug /etc/logrotate.conf")
	# The command should always return zero even if there are errors,
	# so we need to check for errors in stdout or stderr.
	assert result.rc == 0
	assert "error:" not in result.stdout
	assert "error:" not in result.stderr

def test_stacki_logrotate_file_exists(host):
	"""Asserts that the stacki logrotate file exists."""
	assert host.file("/etc/logrotate.d/stack").exists
