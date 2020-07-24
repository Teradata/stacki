import json


class TestStackiBoxInfo:
	def test_no_name(self, run_ansible_module):
		result = run_ansible_module("stacki_box_info")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert len(result.data["boxes"]) == 2

	def test_with_name(self, run_ansible_module):
		result = run_ansible_module("stacki_box_info", name="default")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

		assert len(result.data["boxes"]) == 1
		assert result.data["boxes"][0]["name"] == "default"

	def test_bad_name(self, run_ansible_module):
		result = run_ansible_module("stacki_box_info", name="foo")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "not a valid box" in result.data["msg"]
