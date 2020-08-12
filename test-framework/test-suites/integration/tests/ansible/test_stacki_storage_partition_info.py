class TestStackiStoragePartitionInfo:
	def test_global_scope_no_name(self, host, run_ansible_module):
		result = host.run(
			"stack add storage partition device=/dev/sda1"
			" mountpoint=/ size=10000 type=ext4 partid=1"
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_partition_info")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["partitions"] == [{
			"device": "/dev/sda1",
			"fstype": "ext4",
			"mountpoint": "/",
			"options": "",
			"partid": 1,
			"size": "10000"
		}]

	def test_global_scope_with_name(self, run_ansible_module):
		result = run_ansible_module("stacki_storage_partition_info", name="foo")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "Arguments are not allowed" in result.data["msg"]

	def test_appliance_scope_no_name(self, host, run_ansible_module):
		result = host.run(
			"stack add appliance storage partition backend"
			" device=/dev/sda1 mountpoint=/ size=10000 type=ext4 partid=1"
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_partition_info", scope="appliance")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["partitions"] == [{
			"appliance": "backend",
			"device": "/dev/sda1",
			"fstype": "ext4",
			"mountpoint": "/",
			"options": "",
			"partid": 1,
			"size": "10000"
		}]

	def test_appliance_scope_with_name(self, host, run_ansible_module):
		result = host.run(
			"stack add appliance storage partition backend"
			" device=/dev/sda1 mountpoint=/ size=10000 type=ext4 partid=1"
		)
		assert result.rc == 0

		result = host.run(
			"stack add appliance storage partition frontend"
			" device=/dev/sdb1 mountpoint=/ size=20000 type=ext3 partid=2"
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_partition_info", scope="appliance", name="backend")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["partitions"] == [{
			"appliance": "backend",
			"device": "/dev/sda1",
			"fstype": "ext4",
			"mountpoint": "/",
			"options": "",
			"partid": 1,
			"size": "10000"
		}]

	def test_os_scope_no_name(self, host, run_ansible_module):
		result = host.run(
			"stack add os storage partition sles"
			" device=/dev/sda1 mountpoint=/ size=10000 type=ext4 partid=1"
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_partition_info", scope="os")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["partitions"] == [{
			"device": "/dev/sda1",
			"fstype": "ext4",
			"mountpoint": "/",
			"options": "",
			"os": "sles",
			"partid": 1,
			"size": "10000"
		}]

	def test_os_scope_with_name(self, host, run_ansible_module):
		result = host.run(
			"stack add os storage partition sles"
			" device=/dev/sda1 mountpoint=/ size=10000 type=ext4 partid=1"
		)
		assert result.rc == 0

		result = host.run(
			"stack add os storage partition ubuntu"
			" device=/dev/sdb1 mountpoint=/ size=20000 type=ext3 partid=2"
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_partition_info", scope="os", name="sles")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["partitions"] == [{
			"device": "/dev/sda1",
			"fstype": "ext4",
			"mountpoint": "/",
			"options": "",
			"os": "sles",
			"partid": 1,
			"size": "10000"
		}]

	def test_environment_scope_no_name(self, host, add_environment, run_ansible_module):
		result = host.run(
			"stack add environment storage partition test"
			" device=/dev/sda1 mountpoint=/ size=10000 type=ext4 partid=1"
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_partition_info", scope="environment")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["partitions"] == [{
			"device": "/dev/sda1",
			"environment": "test",
			"fstype": "ext4",
			"mountpoint": "/",
			"options": "",
			"partid": 1,
			"size": "10000"
		}]

	def test_environment_scope_with_name(self, host, add_environment, run_ansible_module):
		add_environment("foo")

		result = host.run(
			"stack add environment storage partition test"
			" device=/dev/sda1 mountpoint=/ size=10000 type=ext4 partid=1"
		)
		assert result.rc == 0

		result = host.run(
			"stack add environment storage partition foo"
			" device=/dev/sdb1 mountpoint=/ size=20000 type=ext3 partid=2"
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_partition_info", scope="environment", name="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["partitions"] == [{
			"device": "/dev/sda1",
			"environment": "test",
			"fstype": "ext4",
			"mountpoint": "/",
			"options": "",
			"partid": 1,
			"size": "10000"
		}]

	def test_host_scope_no_name(self, host, add_host, run_ansible_module):
		add_host("backend-0-1", "0", "1", "backend")

		result = host.run(
			"stack add host storage partition backend-0-0"
			" device=/dev/sda1 mountpoint=/ size=10000 type=ext4 partid=1"
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_partition_info", scope="host")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["partitions"] == [{
			"device": "/dev/sda1",
			"fstype": "ext4",
			"host": "backend-0-0",
			"mountpoint": "/",
			"options": "",
			"partid": 1,
			"size": "10000",
			"source": "H"
		}]

	def test_host_scope_with_name(self, host, add_host, run_ansible_module):
		add_host("backend-0-1", "0", "1", "backend")

		result = host.run(
			"stack add host storage partition backend-0-0"
			" device=/dev/sda1 mountpoint=/ size=10000 type=ext4 partid=1"
		)
		assert result.rc == 0

		result = host.run(
			"stack add host storage partition backend-0-1"
			" device=/dev/sdb1 mountpoint=/ size=20000 type=ext3 partid=2"
		)
		assert result.rc == 0

		result = run_ansible_module("stacki_storage_partition_info", scope="host", name="backend-0-0")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert result.data["partitions"] == [{
			"device": "/dev/sda1",
			"fstype": "ext4",
			"host": "backend-0-0",
			"mountpoint": "/",
			"options": "",
			"partid": 1,
			"size": "10000",
			"source": "H"
		}]

	def test_bad_name(self, run_ansible_module):
		result = run_ansible_module("stacki_storage_partition_info", scope="appliance", name="foo")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "not a valid appliance" in result.data["msg"]
