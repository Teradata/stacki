import json


class TestStackiNetwork:
	def test_add_network(self, host, run_ansible_module):
		# Add the network
		result = run_ansible_module(
			"stacki_network", name="test", address="10.10.0.0", mask="255.255.255.0",
			gateway="10.10.0.1", mtu=1000, zone="foo.com", dns=True, pxe=True
		)

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list network test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"network": "test",
				"address": "10.10.0.0",
				"mask": "255.255.255.0",
				"gateway": "10.10.0.1",
				"mtu": 1000,
				"zone": "foo.com",
				"dns": True,
				"pxe": True
			}
		]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_network", name="test", address="10.10.0.0", mask="255.255.255.0")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_modify_network(self, host, run_ansible_module):
		# Add the network
		result = run_ansible_module(
			"stacki_network", name="test", address="10.10.0.0", mask="255.255.255.0"
		)

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list network test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"network": "test",
				"address": "10.10.0.0",
				"mask": "255.255.255.0",
				"gateway": "",
				"mtu": None,
				"zone": "test",
				"dns": False,
				"pxe": False
			}
		]

		# Now change all the fields of a network
		result = run_ansible_module(
			"stacki_network", name="test", address="10.20.0.0", mask="255.255.0.0",
			gateway="10.20.0.1", mtu=1000, zone="foo.com", dns=True, pxe=True
		)
		assert result.status == "CHANGED"
		assert result.data["changed"] == True


		# Check that the fields changed
		result = host.run("stack list network test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"network": "test",
				"address": "10.20.0.0",
				"mask": "255.255.0.0",
				"gateway": "10.20.0.1",
				"mtu": 1000,
				"zone": "foo.com",
				"dns": True,
				"pxe": True
			}
		]

		# Test idempotency by adding again
		result = run_ansible_module(
			"stacki_network", name="test", address="10.20.0.0", mask="255.255.0.0",
			gateway="10.20.0.1", mtu=1000, zone="foo.com", dns=True, pxe=True
		)
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_remove_network(self, add_network, host, run_ansible_module):
		# Remove the network
		result = run_ansible_module("stacki_network", name="test", state="absent")

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# And confirm it is gone
		result = host.run("stack list network test")
		assert result.rc == 255
		assert "not a valid network" in result.stderr

		# Test idempotency by removing it again
		result = run_ansible_module("stacki_network", name="test", state="absent")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_bad_name(self, add_network, run_ansible_module):
		result = run_ansible_module("stacki_network", name="%", state="absent")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "more than one network matches name" in result.data["msg"]
