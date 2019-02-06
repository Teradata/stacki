import os
import re
import shutil

import pytest


class TestReportZones:
	@pytest.fixture()
	def custom_entries(self, host, host_os):
		# Figure out our base directroy
		if host_os == "sles":
			base_dir = '/var/lib/named'
		else:
			base_dir = '/var/named'

		# Copy over our custom zone files
		for name in ('reverse.test.domain.local', 'test.domain.local'):
			shutil.copyfile(
				f'/export/test-files/report/zones_{name}',
				os.path.join(base_dir, name)
			)

		yield

		# Clean up our custom zone files
		for name in ('reverse.test.domain.local', 'test.domain.local'):
			os.remove(os.path.join(base_dir, name))

	def test_no_custom_entries_sles(self, host, add_host, add_network, fake_os_sles, revert_etc):
		# Set DNS on our test network
		result = host.run('stack set network dns test dns=true')
		assert result.rc == 0

		# Add an interface on our test network to our backend
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test ip=192.168.0.2')
		assert result.rc == 0

		# Add another with no ip address, which should get skipped
		result = host.run('stack add host interface backend-0-0 interface=eth1 network=test mac=00:00:00:00:00:01')
		assert result.rc == 0

		# Add an alias th generate a CNAME
		result = host.run('stack add host alias backend-0-0 alias=foo interface=eth0')
		assert result.rc == 0

		# Report our zones
		result = host.run('stack report zones')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/zones_no_custom_entries_sles.txt') as output:
			# The serial will change between runs, so we have to replace them with something known
			zones = re.sub(r'\d+ ; Serial', '0000000000 ; Serial', result.stdout)

			assert zones == output.read()

	def test_no_custom_entries_redhat(self, host, add_host, add_network, fake_os_redhat, revert_etc):
		# Set DNS on our test network
		result = host.run('stack set network dns test dns=true')
		assert result.rc == 0

		# Add an interface on our test network to our backend
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test ip=192.168.0.2')
		assert result.rc == 0

		# Add another with no ip address, which should get skipped
		result = host.run('stack add host interface backend-0-0 interface=eth1 network=test mac=00:00:00:00:00:01')
		assert result.rc == 0

		# Add an alias th generate a CNAME
		result = host.run('stack add host alias backend-0-0 alias=foo interface=eth0')
		assert result.rc == 0

		# Report our zones
		result = host.run('stack report zones')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/zones_no_custom_entries_redhat.txt') as output:
			# The serial will change between runs, so we have to replace them with something known
			zones = re.sub(r'\d+ ; Serial', '0000000000 ; Serial', result.stdout)

			assert zones == output.read()

	def test_with_custom_entries(self, host, add_host, add_network, host_os, custom_entries):
		# Set DNS on our test network
		result = host.run('stack set network dns test dns=true')
		assert result.rc == 0

		# Add an interface on our test network to our backend
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test ip=192.168.0.2')
		assert result.rc == 0

		# Add an alias while we're at it
		result = host.run('stack add host alias backend-0-0 alias=foo interface=eth0')
		assert result.rc == 0

		# Report our zones
		result = host.run('stack report zones')
		assert result.rc == 0

		# Does the output match what we expect?
		with open(f'/export/test-files/report/zones_with_custom_entries_{host_os}.txt') as output:
			# The serial will change between runs, so we have to replace them with something known
			zones = re.sub(r'\d+ ; Serial', '0000000000 ; Serial', result.stdout)

			assert zones == output.read()
