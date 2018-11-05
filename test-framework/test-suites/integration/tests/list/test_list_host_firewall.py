import json

class TestListHostFirewall:
	def test_frontend_intrinsic_no_dns(self, host):
		# Make sure the intrinsic rules match what we expect
		result = host.run('stack list host firewall frontend-0-0 output-format=json')
		assert result.rc == 0

		with open(f'/export/test-files/list/host_firewall_frontend_intrinsic_no_dns.json') as output:
			assert json.loads(result.stdout) == json.loads(output.read())

	def test_frontend_intrinsic_with_dns(self, host):
		# Toggle on DNS for the private network
		result = host.run('stack set network dns private dns=true')
		assert result.rc == 0

		# Make sure the intrinsic rules match what we expect
		result = host.run('stack list host firewall frontend-0-0 output-format=json')
		assert result.rc == 0

		with open(f'/export/test-files/list/host_firewall_frontend_intrinsic_with_dns.json') as output:
			assert json.loads(result.stdout) == json.loads(output.read())

	def test_backend_intrinsic(self, host, add_host_with_interface):
		# Make sure the intrinsic rules match what we expect
		result = host.run('stack list host firewall backend-0-0 output-format=json')
		assert result.rc == 0

		with open(f'/export/test-files/list/host_firewall_backend_intrinsic.json') as output:
			assert json.loads(result.stdout) == json.loads(output.read())

	def test_scope_overriding(self, host, add_host_with_interface, add_environment, host_os):
		# Add our host to the test environment
		result = host.run('stack set host environment backend-0-0 environment=test')
		assert result.rc == 0

		# Add a bunch of rules to get applied to the host
		result = host.run(
			'stack add firewall backend service=1 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=global_rule'
		)
		assert result.rc == 0

		result = host.run(
			'stack add appliance firewall backend service=2 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=appliance_rule'
		)
		assert result.rc == 0

		result = host.run(
			f'stack add os firewall {host_os} service=3 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=os_rule'
		)
		assert result.rc == 0

		result = host.run(
			'stack add environment firewall test service=4 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=environment_rule'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host firewall backend-0-0 service=5 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=host_rule'
		)
		assert result.rc == 0

		# Add a bunch of rules that will be overridden to just one rule
		result = host.run(
			'stack add firewall service=6 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=override_rule'
		)
		assert result.rc == 0

		result = host.run(
			'stack add appliance firewall backend service=7 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=override_rule'
		)
		assert result.rc == 0

		result = host.run(
			f'stack add os firewall {host_os} service=8 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=override_rule'
		)
		assert result.rc == 0

		result = host.run(
			'stack add environment firewall test service=9 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=override_rule'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host firewall backend-0-0 service=10 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=override_rule'
		)
		assert result.rc == 0

		# Now list all the host rules and see if they match what we expect
		result = host.run('stack list host firewall backend-0-0 output-format=json')
		assert result.rc == 0

		with open(f'/export/test-files/list/host_firewall_scope_overriding.json') as output:
			assert json.loads(result.stdout) == json.loads(output.read())
