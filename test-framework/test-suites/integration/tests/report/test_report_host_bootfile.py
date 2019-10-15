class TestReportHostBootfile:
	def test_on_fresh_install(self, host):
		result = host.run('stack report host bootfile')
		assert result.rc == 0

	def test_for_host_with_full_IP_config(self, host):
		# Setup for a host with full IP config (host, network, interface)
		result = host.run('stack add host backend-1-1')
		assert result.rc == 0
		result = host.run('stack add network public address=192.172.0.0 mask=255.255.255.0 pxe=True')
		assert result.rc == 0
		result = host.run('stack add host interface backend-1-1 interface=eth1 ip=192.172.0.2 network=public default=True mac=52:54:00:6e:50:91')
		assert result.rc == 0

		# When Bootaction is set to OS (Produces a Bootfile)
		#
		# stack add host does this by default (always start with the os boot action)
		result = host.run('stack report host bootfile')
		assert result.rc == 0
		result_specific = host.run('stack report host bootfile backend-1-1')
		result_action_os = result_specific.stdout
		assert result_specific.rc == 0
		assert result.stdout == result_specific.stdout

		# When Bootaction is set to Install (Produces a Bootfile)
		result = host.run('stack set host boot backend-1-1 action=install')
		assert result.rc == 0
		result = host.run('stack report host bootfile')
		assert result.rc == 0
		result_specific = host.run('stack report host bootfile backend-1-1')
		result_action_install = result_specific.stdout
		assert result_specific.rc == 0
		assert result.stdout == result_specific.stdout

		# Output of Bootaction OS and Intall are different
		assert result_action_os != result_action_install

	def test_for_host_with_no_interface(self, host):
		# Setup for a host without a interface (host)
		result = host.run('stack add host backend-1-1')
		assert result.rc == 0

		# When Bootaction is set to None (Doesn't produce a Bootfile and is Skipped)
		result = host.run('stack report host bootfile')
		assert result.rc == 0
		result_specific = host.run('stack report host bootfile backend-1-1')
		assert result_specific.rc == 0
		assert result.stdout == result_specific.stdout
		assert result.stdout == ""

		# When Bootaction is set to OS (Doesn't produce a Bootfile and is Skipped)
		result = host.run('stack set host boot backend-1-1 action=os')
		assert result.rc == 0
		result = host.run('stack report host bootfile')
		assert result.rc == 0
		result_specific = host.run('stack report host bootfile backend-1-1')
		assert result_specific.rc == 0
		assert result.stdout == result_specific.stdout
		assert result.stdout == ""

		# When Bootaction is set to Install (Doesn't produce a Bootfile and is Skipped)
		result = host.run('stack set host boot backend-1-1 action=install')
		assert result.rc == 0
		result = host.run('stack report host bootfile')
		assert result.rc == 0
		result_specific = host.run('stack report host bootfile backend-1-1')
		assert result_specific.rc == 0
		assert result.stdout == result_specific.stdout
		assert result.stdout == ""

	def test_for_host_with_interface_but_no_IP_or_network(self, host):
		# Setup for a host with an interface but no IP or network (host, interface)
		result = host.run('stack add host backend-1-1')
		assert result.rc == 0
		result = host.run('stack add host interface backend-1-1 interface=eth1 default=True mac=52:54:00:6e:50:91')
		assert result.rc == 0

		# When Bootaction is set to None (Doesn't produce a Bootfile and is Skipped)
		result = host.run('stack report host bootfile')
		assert result.rc == 0
		result_specific = host.run('stack report host bootfile backend-1-1')
		assert result_specific.rc == 0
		assert result.stdout == result_specific.stdout
		assert result.stdout == ""

		# When Bootaction is set to OS (Doesn't produce a Bootfile and is Skipped)
		result = host.run('stack set host boot backend-1-1 action=os')
		assert result.rc == 0
		result = host.run('stack report host bootfile')
		assert result.rc == 0
		result_specific = host.run('stack report host bootfile backend-1-1')
		assert result_specific.rc == 0
		assert result.stdout == result_specific.stdout
		assert result.stdout == ""

		# When Bootaction is set to Install (Doesn't produce a Bootfile and is Skipped)
		result = host.run('stack set host boot backend-1-1 action=install')
		assert result.rc == 0
		result = host.run('stack report host bootfile')
		assert result.rc == 0
		result_specific = host.run('stack report host bootfile backend-1-1')
		assert result_specific.rc == 0
		assert result.stdout == result_specific.stdout
		assert result.stdout == ""

	def test_for_combination_of_no_host_interface_and_full_config(self, host):
		# Setup for a host without a interface (host) and Bootaction set to OS
		result = host.run('stack add host backend-2-2')
		assert result.rc == 0
		result = host.run('stack set host boot backend-2-2 action=os')
		assert result.rc == 0

		# Setup for a host with full IP config (host, network, interface) and Bootaction set to OS
		result = host.run('stack add host backend-1-1')
		assert result.rc == 0
		result = host.run('stack add network public address=192.172.0.0 mask=255.255.255.0 pxe=True')
		assert result.rc == 0
		result = host.run('stack add host interface backend-1-1 interface=eth1 ip=192.172.0.2 network=public default=True mac=52:54:00:6e:50:91')
		assert result.rc == 0
		result = host.run('stack set host boot backend-1-1 action=os')
		assert result.rc == 0

		# Produces a Bootfile only for the host with full config and the other is skipped
		result = host.run('stack report host bootfile')
		assert result.rc == 0
		result_specific = host.run('stack report host bootfile backend-1-1')
		assert result_specific.rc == 0
		assert result.stdout == result_specific.stdout

	def test_for_combination_of_host_with__no_IP_or_network_and_full_config(self, host):
		# Setup for a host with an interface but no IP or network (host, interface) and Bootaction set to Install
		result = host.run('stack add host backend-2-2')
		assert result.rc == 0
		result = host.run('stack add host interface backend-2-2 interface=eth1 default=True mac=52:54:00:6e:50:99')
		assert result.rc == 0
		result = host.run('stack set host boot backend-2-2 action=install')
		assert result.rc == 0

		# Setup for a host with full IP config (host, network, interface) and Bootaction set to OS
		result = host.run('stack add host backend-1-1')
		assert result.rc == 0
		result = host.run('stack add network public address=192.172.0.0 mask=255.255.255.0 pxe=True')
		assert result.rc == 0
		result = host.run('stack add host interface backend-1-1 interface=eth1 ip=192.172.0.2 network=public default=True mac=52:54:00:6e:50:91')
		assert result.rc == 0
		result = host.run('stack set host boot backend-1-1 action=install')
		assert result.rc == 0

		# Produces a Bootfile only for the host with full config and the other is skipped
		result = host.run('stack report host bootfile')
		assert result.rc == 0
		result_specific = host.run('stack report host bootfile backend-1-1')
		assert result_specific.rc == 0
		assert result.stdout == result_specific.stdout
