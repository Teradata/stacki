import json


class TestStackiAppliance:
	def test_add_appliance(self, host, run_ansible_module):
		# Add the appliance
		result = run_ansible_module("stacki_appliance", name="test")

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list appliance test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"appliance": "test",
				"public": "yes"
			}
		]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_appliance", name="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_modify_appliance_no_node(self, host, run_ansible_module):
		# Add the appliance without giving it a node parameter
		result = run_ansible_module("stacki_appliance", name="test")

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Confirm there is no node attr for the appliance
		result = host.run("stack list appliance attr test attr=node")
		assert result.rc == 0
		assert result.stdout == ""

		# Now change the node
		result = run_ansible_module("stacki_appliance", name="test", node="backend")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that node attr changed
		result = host.run("stack list appliance attr test attr=node output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"appliance": "test",
				"scope": "appliance",
				"type": "var",
				"attr": "node",
				"value": "backend"
			}
		]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_appliance", name="test", node="backend")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False


	def test_modify_appliance_with_node(self, host, run_ansible_module):
		# Add the appliance with a node parameter
		result = run_ansible_module("stacki_appliance", name="test", node="test")

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Confirm that the node attr is set for the appliance
		result = host.run("stack list appliance attr test attr=node output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"appliance": "test",
				"scope": "appliance",
				"type": "var",
				"attr": "node",
				"value": "test"
			}
		]

		# Now change the node
		result = run_ansible_module("stacki_appliance", name="test", node="backend")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that node attr changed
		result = host.run("stack list appliance attr test attr=node output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"appliance": "test",
				"scope": "appliance",
				"type": "var",
				"attr": "node",
				"value": "backend"
			}
		]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_appliance", name="test", node="backend")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_remove_appliance(self, add_appliance, host, run_ansible_module):
		# Remove the appliance
		result = run_ansible_module("stacki_appliance", name="test", state="absent")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# And confirm it is gone
		result = host.run("stack list appliance test")
		assert result.rc == 255
		assert "not a valid appliance" in result.stderr

		# Test idempotency by removing it again
		result = run_ansible_module("stacki_appliance", name="test", state="absent")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_bad_name(self, run_ansible_module):
		result = run_ansible_module("stacki_appliance", name="%", state="absent")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "more than one appliance matches name" in result.data["msg"]
