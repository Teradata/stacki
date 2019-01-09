class TestReportHostFirewall:
	def test_no_rules_added(self, host, add_host_with_interface):
		# Generate the firewall rules
		result = host.run('stack report host firewall backend-0-0')
		assert result.rc == 0

		# Do they match what we expect?
		with open('/export/test-files/report/host_firewall_no_rules_added.txt') as output:
			assert result.stdout == output.read()

	def test_nat_rules(self, host, add_host_with_interface, add_network):
		# Add the eth0 interface to our private network
		result = host.run('stack set host interface network backend-0-0 interface=eth0 network=private')
		assert result.rc == 0

		# Add a second interface to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth1 network=test')
		assert result.rc == 0

		# Add rules to NAT eth1 through eth0
		result = host.run(
			'stack add host firewall backend-0-0 table=nat chain=POSTROUTING '
			'output-network=private action=MASQUERADE service=all protocol=all'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host firewall backend-0-0 chain=FORWARD network=test '
			'action=ACCEPT service=all protocol=all'
		)
		assert result.rc == 0

		# Generate the firewall rules
		result = host.run('stack report host firewall backend-0-0')
		assert result.rc == 0

		# Do they match what we expect?
		with open('/export/test-files/report/host_firewall_nat_rules.txt') as output:
			assert result.stdout == output.read()

	def test_drop_rule(self, host, add_host_with_interface):
		# Add rules to drop all traffic to port 21
		result = host.run(
			'stack add host firewall backend-0-0 chain=INPUT '
			'action=DROP service=23 protocol=all'
		)
		assert result.rc == 0

		# Generate the firewall rules
		result = host.run('stack report host firewall backend-0-0')
		assert result.rc == 0

		# Do they match what we expect?
		with open('/export/test-files/report/host_firewall_drop_rule.txt') as output:
			assert result.stdout == output.read()

	def test_skip_output_network(self, host, add_host_with_interface):
		# Add a NAT rule, which should get skipped because the
		# host isn't in the private network
		result = host.run(
			'stack add host firewall backend-0-0 table=nat chain=POSTROUTING '
			'output-network=private action=MASQUERADE service=all protocol=all'
		)
		assert result.rc == 0

		# Generate the firewall rules
		result = host.run('stack report host firewall backend-0-0')
		assert result.rc == 0

		# Do they match what we expect?
		with open('/export/test-files/report/host_firewall_skip_output_network.txt') as output:
			assert result.stdout == output.read()
