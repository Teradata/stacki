class TestStackiApplianceInfo:
	def test_no_name(self, run_ansible_module):
		result = run_ansible_module("stacki_appliance_info")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert len(result.data["appliances"]) > 1

	def test_with_name(self, run_ansible_module):
		result = run_ansible_module("stacki_appliance_info", name="backend")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["appliances"] == [{
			"appliance": "backend",
			"public": True
		}]

	def test_bad_name(self, run_ansible_module):
		result = run_ansible_module("stacki_appliance_info", name="foo")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "not a valid appliance" in result.data["msg"]
