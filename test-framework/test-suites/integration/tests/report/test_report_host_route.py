import json


class TestReportHostRoute:
	def test_scope_resolving(self, host, add_host_with_interface, add_environment, host_os, test_file):
		# Add our host to the test environment
		result = host.run('stack set host environment backend-0-0 environment=test')
		assert result.rc == 0

		# Set the backend's interface to the private network
		result = host.run(
			'stack set host interface network backend-0-0 '
			'interface=eth0 network=private'
		)
		assert result.rc == 0

		# Add a bunch of routes to get applied to the host, in different scopes
		result = host.run(
			'stack add route address=192.168.0.3 gateway=private'
		)
		assert result.rc == 0

		result = host.run(
			'stack add appliance route backend address=192.168.0.4 '
			'gateway=192.168.0.1 interface=eth0'
		)
		assert result.rc == 0

		result = host.run(
			f'stack add os route {host_os} address=192.168.0.5 gateway=192.168.0.1'
		)
		assert result.rc == 0

		result = host.run(
			'stack add environment route test address=192.168.0.6 gateway=private'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host route backend-0-0 address=192.168.0.7 gateway=private'
		)
		assert result.rc == 0

		# Add a bunch of rules that will be overridden to just one rule
		result = host.run(
			'stack add route address=192.168.0.8 gateway=private'
		)
		assert result.rc == 0

		result = host.run(
			'stack add appliance route backend address=192.168.0.8 gateway=private'
		)
		assert result.rc == 0

		result = host.run(
			f'stack add os route {host_os} address=192.168.0.8 gateway=private'
		)
		assert result.rc == 0

		result = host.run(
			'stack add environment route test address=192.168.0.8 gateway=private'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host route backend-0-0 address=192.168.0.8 gateway=private'
		)
		assert result.rc == 0

		# Now report the host rules and see if they match what we expect
		result = host.run('stack report host route backend-0-0')
		assert result.rc == 0

		with open(test_file(f'report/host_route_scope_resolving_{host_os}.txt')) as output:
			assert result.stdout == output.read()
