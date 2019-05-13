import pytest
import paramiko
import testinfra
from stack import api
from stack.util import _exec

testinfra_hosts = [host['host'] for host in api.Call('list host', ['a:frontend', 'a:backend'])]
class TestPackageInstall:

	""" Test if the packages stacki installed during setup are still currently installed on the host"""
	def test_package_installs(self, host):

		# Get hostname and see if we can ssh
		# into the host
		try:
			hostname = host.check_output('hostname')

		except paramiko.ssh_exception.NoValidConnectionsError:
			pytest.fail(f'Could not ssh into host')

		config_packages = None
		installer = None
		missing_packages = []

		# Get the OS
		host_os = host.system_info.distribution

		# Different package managers depending on OS
		if host_os == 'sles':
			installer = 'zypper install -f -y'

		elif host_os == 'centos':
			installer = 'yum install -y'

		if installer:

			output = _exec(f'stack list host profile {hostname} chapter=main profile=bash | grep "{installer}"', shell=True).stdout
			if output:

				# Format the package list to be just the packages without the package manager arguments
				config_packages = output.replace(installer, '').strip().split(' ')

			else:
				pytest.skip('No stacki installed packages found')


		# Use testinfra to check if every package stacki installed is currently
		# still installed on the host
		for conf_package in config_packages:
			if not host.package(conf_package).is_installed:

				# If a package isn't installed, use rpm to see if another installed package
				# provides it instead
				try:
					provide_package = host.check_output(f'rpm -q --whatprovides {conf_package}')

				# If an rpm doesn't provide the package, an assertion is rasied by testinfra
				except AssertionError:
					missing_packages.append(conf_package)


		assert not missing_packages, f'On host {hostname} the following packages were not found on the installed system: {", ".join(missing_packages)}'
