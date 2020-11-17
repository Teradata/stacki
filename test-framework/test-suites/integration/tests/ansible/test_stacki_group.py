import json


class TestStackiGroup:
	def test_add_group(self, host, run_ansible_module):
		# Add the group
		result = run_ansible_module("stacki_group", name="test")

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list group test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"group": "test",
			"hosts": ""
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_group", name="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_remove_group(self, add_group, host, run_ansible_module):
		# Remove the group
		result = run_ansible_module("stacki_group", name="test", state="absent")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# And confirm it is gone
		result = host.run("stack list group test")
		assert result.stdout == ""

		# Test idempotency by removing it again
		result = run_ansible_module("stacki_group", name="test", state="absent")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_bad_name(self, add_group, run_ansible_module):
		add_group("foo")

		result = run_ansible_module("stacki_group", name="%", state="absent")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "more than one group matches name" in result.data["msg"]
