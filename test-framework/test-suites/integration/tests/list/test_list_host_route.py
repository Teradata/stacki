import json


class TestListHostRoute:
	def test_scope_resolving(self, host, add_host_with_interface, add_environment, host_os, test_file):
		# Add our host to the test environment
		result = host.run('stack set host environment backend-0-0 environment=test')
		assert result.rc == 0

		# Add a bunch of routes to get applied to the host, in different scopes
		result = host.run(
			'stack add route address=192.168.0.3 gateway=private'
		)
		assert result.rc == 0

		result = host.run(
			'stack add appliance route backend address=192.168.0.4 gateway=private'
		)
		assert result.rc == 0

		result = host.run(
			f'stack add os route {host_os} address=192.168.0.5 gateway=private'
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

		# Now list all the host rules and see if they match what we expect
		result = host.run('stack list host route backend-0-0 output-format=json')
		assert result.rc == 0

		with open(test_file('list/host_route_scope_resolving.json')) as output:
			assert json.loads(result.stdout) == json.loads(output.read())

	def test_scope_no_enviroment(self, host, add_host, test_file):
		# Create some more hosts
		add_host('backend-0-1', '0', '1', 'backend')
		add_host('backend-0-2', '0', '2', 'backend')

		# Add a route to each host
		result = host.run(
			'stack add host route backend-0-0 address=192.168.0.10 gateway=private'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host route backend-0-1 address=192.168.0.11 gateway=private'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host route backend-0-2 address=192.168.0.12 gateway=private'
		)
		assert result.rc == 0

		# Now list all the host routes and see if they match what we expect
		result = host.run('stack list host route backend-0-0 output-format=json')
		assert result.rc == 0

		with open(test_file('list/host_route_scope_no_enviroment.json')) as output:
			assert json.loads(result.stdout) == json.loads(output.read())
