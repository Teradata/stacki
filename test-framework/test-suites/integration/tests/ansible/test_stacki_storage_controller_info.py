class TestStackiStorageControllerInfo:
	def test_global_scope_no_name(self, run_ansible_module):
		result = run_ansible_module("stacki_storage_controller_info")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["controllers"] == [{
			"adapter": None,
			"arrayid": "*",
			"enclosure": None,
			"options": "",
			"raidlevel": "0",
			"slot": "*"
		}]

	def test_global_scope_with_name(self, run_ansible_module):
		result = run_ansible_module("stacki_storage_controller_info", name="foo")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "Arguments are not allowed" in result.data["msg"]

	def test_appliance_scope_no_name(self, host, run_ansible_module):
		result = host.run(
			'stack add appliance storage controller backend raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_controller_info", scope="appliance")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["controllers"] == [{
			"adapter": 2,
			"appliance": "backend",
			"arrayid": "4",
			"enclosure": 1,
			"options": "",
			"raidlevel": "0",
			"slot": "3"
		}]

	def test_appliance_scope_with_name(self, host, run_ansible_module):
		result = host.run(
			'stack add appliance storage controller backend raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_controller_info", scope="appliance", name="backend")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["controllers"] == [{
			"adapter": 2,
			"appliance": "backend",
			"arrayid": "4",
			"enclosure": 1,
			"options": "",
			"raidlevel": "0",
			"slot": "3"
		}]

	def test_os_scope_no_name(self, host, run_ansible_module):
		result = host.run(
			'stack add os storage controller sles raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_controller_info", scope="os")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["controllers"] == [{
			"adapter": 2,
			"arrayid": "4",
			"enclosure": 1,
			"options": "",
			"os": "sles",
			"raidlevel": "0",
			"slot": "3"
		}]

	def test_os_scope_with_name(self, host, run_ansible_module):
		result = host.run(
			'stack add os storage controller sles raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_controller_info", scope="os", name="sles")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["controllers"] == [{
			"adapter": 2,
			"arrayid": "4",
			"enclosure": 1,
			"options": "",
			"os": "sles",
			"raidlevel": "0",
			"slot": "3"
		}]

	def test_environment_scope_no_name(self, host, add_environment, run_ansible_module):
		result = host.run(
			'stack add environment storage controller test raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_controller_info", scope="environment")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["controllers"] == [{
			"adapter": 2,
			"arrayid": "4",
			"enclosure": 1,
			"environment": "test",
			"options": "",
			"raidlevel": "0",
			"slot": "3"
		}]

	def test_environment_scope_with_name(self, host, add_environment, run_ansible_module):
		result = host.run(
			'stack add environment storage controller test raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_controller_info", scope="environment", name="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["controllers"] == [{
			"adapter": 2,
			"arrayid": "4",
			"enclosure": 1,
			"environment": "test",
			"options": "",
			"raidlevel": "0",
			"slot": "3"
		}]

	def test_host_scope_no_name(self, host, add_host, run_ansible_module):
		result = host.run(
			'stack add host storage controller backend-0-0 raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_controller_info", scope="host")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["controllers"] == [
			{
				"adapter": 2,
				"arrayid": "4",
				"enclosure": 1,
				"host": "backend-0-0",
				"options": "",
				"raidlevel": "0",
				"slot": "3",
				"source": "H"
			},
			{
				"adapter": None,
				"arrayid": "*",
				"enclosure": None,
				"host": "frontend-0-0",
				"options": "",
				"raidlevel": "0",
				"slot": "*",
				"source": "G"
			}
		]

	def test_host_scope_with_name(self, host, add_host, run_ansible_module):
		result = host.run(
			'stack add host storage controller backend-0-0 raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_controller_info", scope="host", name="backend-0-0")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["controllers"] == [{
			"adapter": 2,
			"arrayid": "4",
			"enclosure": 1,
			"host": "backend-0-0",
			"options": "",
			"raidlevel": "0",
			"slot": "3",
			"source": "H"
		}]

	def test_bad_name(self, run_ansible_module):
		result = run_ansible_module("stacki_storage_controller_info", scope="appliance", name="foo")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "not a valid appliance" in result.data["msg"]
