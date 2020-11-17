import json


class TestStackiHost:
	def test_add_host(self, host, host_os, add_group, test_file):
		# Run the ansible playbook to add our test host
		result = host.run(f"ansible-playbook {test_file('ansible/add_host.yaml')}")
		assert result.rc == 0
		assert "changed=1" in result.stdout

		# Check that it is there now
		result = host.run("stack list host test-backend output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'default',
			'comment': 'test host',
			'environment': None,
			'host': 'test-backend',
			'installaction': 'console',
			'os': host_os,
			'osaction': 'default',
			'rack': '10',
			'rank': '4'
		}]

		# Check that the interface is there too
		result = host.run("stack list host interface test-backend output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': True,
			'host': 'test-backend',
			'interface': 'eth0',
			'ip': '10.10.10.10',
			'mac': '00:11:22:33:44:55',
			'module': None,
			'name': None,
			'network': None,
			'options': None,
			'vlan': None
		}]

		# And the host group
		result = host.run("stack list host group test-backend output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'groups': 'test',
			'host': 'test-backend'
		}]

		# Test idempotency by running it again
		result = host.run(f"ansible-playbook {test_file('ansible/add_host.yaml')}")
		assert result.rc == 0
		assert "changed=0" in result.stdout

	def test_edit_host(self, host, add_group, host_os, test_file):
		# Add a few extra groups
		add_group("foo")
		add_group("bar")

		# Add a test backend
		result = host.run("stack add host test-backend appliance=frontend rack=0 rank=1")
		assert result.rc == 0

		# Give it a few groups:
		# test: not touched, foo: removed, bar: added by the playbook

		result = host.run("stack add host group test-backend group=test")
		assert result.rc == 0

		result = host.run("stack add host group test-backend group=foo")
		assert result.rc == 0

		# Give it a bunch of interfaces to modify by the playbook:
		# eth0: not touched,  eth1: removed, eth2: added by the playbook

		result = host.run("stack add host interface test-backend interface=eth0 ip=10.10.0.1")
		assert result.rc == 0

		result = host.run("stack add host interface test-backend interface=eth1 ip=10.10.1.1")
		assert result.rc == 0

		# Run the ansible playbook to modify our test host
		result = host.run(f"ansible-playbook {test_file('ansible/edit_host.yaml')}")
		assert result.rc == 0
		assert "changed=1" in result.stdout

		# Check that it is there now
		result = host.run("stack list host test-backend output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'default',
			'comment': 'test host',
			'environment': None,
			'host': 'test-backend',
			'installaction': 'console',
			'os': host_os,
			'osaction': 'default',
			'rack': '10',
			'rank': '4'
		}]

		# Check that the interfaces are there too
		result = host.run("stack list host interface test-backend output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'test-backend',
				'interface': 'eth0',
				'ip': '10.10.0.1',
				'mac': None,
				'module': None,
				'name': None,
				'network': None,
				'options': None,
				'vlan': None
			},
			{
				'channel': None,
				'default': None,
				'host': 'test-backend',
				'interface': 'eth2',
				'ip': '10.10.2.1',
				'mac': '00:11:22:33:44:55',
				'module': None,
				'name': None,
				'network': None,
				'options': None,
				'vlan': None
			}
		]

		# And the host group
		result = host.run("stack list host group test-backend output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'groups': 'bar test',
			'host': 'test-backend'
		}]

		# Test idempotency by running it again
		result = host.run(f"ansible-playbook {test_file('ansible/edit_host.yaml')}")
		assert result.rc == 0
		assert "changed=0" in result.stdout

	def test_update_host_mac(self, host, test_file):
		# Add a test backend
		result = host.run("stack add host test-backend appliance=frontend rack=0 rank=1")
		assert result.rc == 0

		# Give it an interface with a mac to update
		result = host.run("stack add host interface test-backend interface=eth0 mac=00:11:22:33:44:55")
		assert result.rc == 0

		# Run the ansible playbook to modify our test host
		result = host.run(f"ansible-playbook {test_file('ansible/update_host_mac.yaml')}")
		assert result.rc == 0
		assert "changed=1" in result.stdout

		# Check that the interface is updated
		result = host.run("stack list host interface test-backend output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
			'host': 'test-backend',
			'interface': 'eth0',
			'ip': None,
			'mac': '11:22:33:44:55:66',
			'module': None,
			'name': None,
			'network': None,
			'options': None,
			'vlan': None
		}]

		# Test idempotency by running it again
		result = host.run(f"ansible-playbook {test_file('ansible/update_host_mac.yaml')}")
		assert result.rc == 0
		assert "changed=0" in result.stdout

	def test_update_host_interface(self, host, test_file):
		# Add a test backend
		result = host.run("stack add host test-backend appliance=frontend rack=0 rank=1")
		assert result.rc == 0

		# Give it an interface with a mac to update
		result = host.run("stack add host interface test-backend interface=eth0 mac=00:11:22:33:44:55")
		assert result.rc == 0

		# Run the ansible playbook to modify our test host
		result = host.run(f"ansible-playbook {test_file('ansible/update_host_interface.yaml')}")
		assert result.rc == 0
		assert "changed=1" in result.stdout

		# Check that the interface is updated
		result = host.run("stack list host interface test-backend output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
			'host': 'test-backend',
			'interface': 'eth1',
			'ip': None,
			'mac': '00:11:22:33:44:55',
			'module': None,
			'name': None,
			'network': None,
			'options': None,
			'vlan': None
		}]

		# Test idempotency by running it again
		result = host.run(f"ansible-playbook {test_file('ansible/update_host_interface.yaml')}")
		assert result.rc == 0
		assert "changed=0" in result.stdout

	def test_remove_host(self, host, test_file):
		# Add a test backend
		result = host.run("stack add host test-backend appliance=backend rack=0 rank=1")
		assert result.rc == 0

		# Run the ansible playbook to remove our test host
		result = host.run(f"ansible-playbook {test_file('ansible/remove_host.yaml')}")
		assert result.rc == 0
		assert "changed=1" in result.stdout

		# Check that the host is gone
		result = host.run("stack list host test-backend")
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "test-backend"\n'

		# Test idempotency by running it again
		result = host.run(f"ansible-playbook {test_file('ansible/remove_host.yaml')}")
		assert result.rc == 0
		assert "changed=0" in result.stdout
