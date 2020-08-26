class TestStackiHostInfo:
	def test_no_name(self, add_host_with_interface, run_ansible_module, host_os):
		result = run_ansible_module("stacki_host_info")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		# The frontend's mac will change each run, so assert it is set then remove it
		assert result.data["hosts"][0]["interfaces"][0]["mac"]
		del result.data["hosts"][0]["interfaces"][0]["mac"]

		# DBS pallet adds to the status, so assert it is set then remove it
		assert result.data["hosts"][0]["status"]
		del result.data["hosts"][0]["status"]

		assert result.data["hosts"][1]["status"]
		del result.data["hosts"][1]["status"]

		assert result.data["hosts"] == [
			{
				'appliance': 'frontend',
				'boot': {
					'action': 'os',
					'nukecontroller': False,
					'nukedisks': False
				},
				'box': 'frontend',
				'comment': None,
				'environment': None,
				'groups': [],
				'host': 'frontend-0-0',
				'installaction': 'default',
				'interfaces': [{
					'channel': None,
					'default': True,
					'interface': 'eth1',
					'ip': '192.168.0.2',
					'module': None,
					'name': 'frontend-0-0',
					'network': 'private',
					'options': None,
					'vlan': None
				}],
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '0'
			},
			{
				'appliance': 'backend',
				'boot': {
					'action': 'os',
					'nukecontroller': False,
					'nukedisks': False
				},
				'box': 'default',
				'comment': None,
				'environment': None,
				'groups': [],
				'host': 'backend-0-0',
				'installaction': 'default',
				'interfaces': [{
					'channel': None,
					'default': None,
					'interface': 'eth0',
					'ip': None,
					'mac': None,
					'module': None,
					'name': None,
					'network': None,
					'options': None,
					'vlan': None
				}],
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '0'
			}
		]

	def test_with_name(self, add_host_with_interface, add_group, host, run_ansible_module, host_os):
		# Add our backend to a few groups
		result = host.run('stack add host group backend-0-0 group=test')
		assert result.rc == 0

		add_group("foo")
		result = host.run('stack add host group backend-0-0 group=foo')
		assert result.rc == 0

		# Run out module and check its output
		result = run_ansible_module("stacki_host_info", name="backend-0-0")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False


		# DBS pallet adds to the status, so assert it is set then remove it
		assert result.data["hosts"][0]["status"]
		del result.data["hosts"][0]["status"]

		assert result.data["hosts"] == [{
 			'appliance': 'backend',
			'boot': {
				'action': 'os',
				'nukecontroller': False,
				'nukedisks': False
			},
			'box': 'default',
			'comment': None,
			'environment': None,
			'groups': ['foo', 'test'],
			'host': 'backend-0-0',
			'installaction': 'default',
			'interfaces': [{
				'channel': None,
				'default': None,
				'interface': 'eth0',
				'ip': None,
				'mac': None,
				'module': None,
				'name': None,
				'network': None,
				'options': None,
				'vlan': None
			}],
			'os': host_os,
			'osaction': 'default',
			'rack': '0',
			'rank': '0'
		}]

	def test_bad_name(self, run_ansible_module):
		result = run_ansible_module("stacki_host_info", name="foo")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert 'cannot resolve host "foo"' in result.data["msg"]
