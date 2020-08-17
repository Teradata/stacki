import json


class TestStackiBox:
	def test_add_box(self, host, host_os, run_ansible_module):
		# Add the box
		result = run_ansible_module("stacki_box", name="test")

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list box test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "test",
				"os": host_os,
				"pallets": "",
				"carts": "",
				"repos": "",
			}
		]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_box", name="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_change_os(self, host, host_os, run_ansible_module):
		# Add the box
		result = run_ansible_module("stacki_box", name="test")

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list box test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "test",
				"os": host_os,
				"pallets": "",
				"carts": "",
				"repos": "",
			}
		]

		# Now change to OS
		result = run_ansible_module("stacki_box", name="test", os="ubuntu")

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that the OS is changed
		result = host.run("stack list box test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"name": "test",
				"os": "ubuntu",
				"pallets": "",
				"carts": "",
				"repos": "",
			}
		]

	def test_remove_box(self, add_box, host, run_ansible_module):
		# Remove the box
		result = run_ansible_module("stacki_box", name="test", state="absent")

		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# And confirm it is gone
		result = host.run("stack list box test")
		assert result.rc == 255
		assert "not a valid box" in result.stderr

		# Test idempotency by removing it again
		result = run_ansible_module("stacki_box", name="test", state="absent")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_bad_name(self, add_box, run_ansible_module):
		result = run_ansible_module("stacki_box", name="%", state="absent")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "more than one box matches name" in result.data["msg"]
