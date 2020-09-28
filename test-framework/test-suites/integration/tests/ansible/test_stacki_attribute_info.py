class TestStackiAttributeInfo:
	def test_global_scope_no_name(self, run_ansible_module):
		result = run_ansible_module("stacki_attribute_info")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert len(result.data["attributes"]) > 1

	def test_global_scope_no_name_with_attr(self, host, run_ansible_module):
		result = host.run("stack add attr attr=test value=foo")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", attr="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [{
			"attr": "test",
			"scope": "global",
			"type": "var",
			"value": "foo"
		}]

	def test_global_scope_no_name_without_shadow(self, run_ansible_module):
		result = run_ansible_module("stacki_attribute_info", shadow=False)

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert len(result.data["attributes"]) > 1

		for attribute in result.data["attributes"]:
			assert attribute["type"] != "shadow"

	def test_global_scope_with_name(self, run_ansible_module):
		result = run_ansible_module("stacki_attribute_info", name="foo")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "Arguments are not allowed" in result.data["msg"]

	def test_appliance_scope_no_name(self, run_ansible_module):
		result = run_ansible_module("stacki_attribute_info", scope="appliance")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert len(result.data["attributes"]) > 1

	def test_appliance_scope_no_name_with_attr(self, host, run_ansible_module):
		result = host.run("stack add appliance attr backend attr=test value=foo")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", scope="appliance", attr="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [{
			"appliance": "backend",
			"attr": "test",
			"scope": "appliance",
			"type": "var",
			"value": "foo"
		}]

	def test_appliance_scope_with_name(self, run_ansible_module):
		result = run_ansible_module("stacki_attribute_info", scope="appliance", name="backend")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert len(result.data["attributes"]) > 1

	def test_appliance_scope_with_name_with_attr(self, host, run_ansible_module):
		result = host.run("stack add appliance attr backend attr=test value=foo")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", scope="appliance", name="backend", attr="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [{
			"appliance": "backend",
			"attr": "test",
			"scope": "appliance",
			"type": "var",
			"value": "foo"
		}]

	def test_os_scope_no_name(self, host, run_ansible_module):
		result = host.run("stack add os attr sles attr=test value=foo")
		assert result.rc == 0

		result = host.run("stack add os attr redhat attr=test value=bar")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", scope="os")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [
			{
				"attr": "test",
				"os": "redhat",
				"scope": "os",
				"type": "var",
				"value": "bar"
			},
			{
				"attr": "test",
				"os": "sles",
				"scope": "os",
				"type": "var",
				"value": "foo"
			}
		]

	def test_os_scope_no_name_with_attr(self, host, run_ansible_module):
		result = host.run("stack add os attr sles attr=test value=foo")
		assert result.rc == 0

		result = host.run("stack add os attr redhat attr=test value=bar")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", scope="os", attr="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [
			{
				"attr": "test",
				"os": "redhat",
				"scope": "os",
				"type": "var",
				"value": "bar"
			},
			{
				"attr": "test",
				"os": "sles",
				"scope": "os",
				"type": "var",
				"value": "foo"
			}
		]

	def test_os_scope_with_name(self, host, run_ansible_module):
		result = host.run("stack add os attr sles attr=test value=foo")
		assert result.rc == 0

		result = host.run("stack add os attr redhat attr=test value=bar")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", name="sles", scope="os")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [{
			"attr": "test",
			"os": "sles",
			"scope": "os",
			"type": "var",
			"value": "foo"
		}]

	def test_os_scope_with_name_with_attr(self, host, run_ansible_module):
		result = host.run("stack add os attr sles attr=test value=foo")
		assert result.rc == 0

		result = host.run("stack add os attr redhat attr=test value=bar")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", name="sles", scope="os", attr="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [{
			"attr": "test",
			"os": "sles",
			"scope": "os",
			"type": "var",
			"value": "foo"
		}]

	def test_environment_scope_no_name(self, host, add_environment, run_ansible_module):
		result = host.run("stack add environment attr test attr=test value=foo")
		assert result.rc == 0

		result = host.run("stack add environment attr test attr=bar value=baz")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", scope="environment")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [
			{
				"attr": "bar",
				"environment": "test",
				"scope": "environment",
				"type": "var",
				"value": "baz"
			},
			{
				"attr": "test",
				"environment": "test",
				"scope": "environment",
				"type": "var",
				"value": "foo"
			}
		]

	def test_environment_scope_no_name_with_attr(self, host, add_environment, run_ansible_module):
		result = host.run("stack add environment attr test attr=test value=foo")
		assert result.rc == 0

		result = host.run("stack add environment attr test attr=bar value=baz")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", scope="environment", attr="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [{
			"attr": "test",
			"environment": "test",
			"scope": "environment",
			"type": "var",
			"value": "foo"
		}]

	def test_environment_scope_with_name(self, host, add_environment, run_ansible_module):
		result = host.run("stack add environment attr test attr=test value=foo")
		assert result.rc == 0

		result = host.run("stack add environment attr test attr=bar value=baz")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", scope="environment", name="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [
			{
				"attr": "bar",
				"environment": "test",
				"scope": "environment",
				"type": "var",
				"value": "baz"
			},
			{
				"attr": "test",
				"environment": "test",
				"scope": "environment",
				"type": "var",
				"value": "foo"
			}
		]

	def test_environment_scope_with_name_with_attr(self, host, add_environment, run_ansible_module):
		result = host.run("stack add environment attr test attr=test value=foo")
		assert result.rc == 0

		result = host.run("stack add environment attr test attr=bar value=baz")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", scope="environment", name="test", attr="bar")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [{
			"attr": "bar",
			"environment": "test",
			"scope": "environment",
			"type": "var",
			"value": "baz"
		}]

	def test_host_scope_no_name(self, host, add_host, run_ansible_module):
		result = run_ansible_module("stacki_attribute_info", scope="host")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert len(result.data["attributes"])

	def test_host_scope_no_name_with_attr(self, host, add_host, run_ansible_module):
		result = host.run("stack add host attr backend-0-0 attr=test value=foo")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", scope="host", attr="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [{
			"attr": "test",
			"host": "backend-0-0",
			"scope": "host",
			"type": "var",
			"value": "foo"
		}]

	def test_host_scope_with_name(self, host, add_host, run_ansible_module):
		result = run_ansible_module("stacki_attribute_info", scope="host", name="backend-0-0")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert len(result.data["attributes"])
		for attribute in result.data["attributes"]:
			assert attribute["host"] == "backend-0-0"

	def test_host_scope_with_name_with_attr(self, host, add_host, run_ansible_module):
		result = host.run("stack add host attr backend-0-0 attr=test value=foo")
		assert result.rc == 0

		result = run_ansible_module("stacki_attribute_info", scope="host", name="backend-0-0", attr="test")

		assert result.status == "SUCCESS"
		assert result.data["changed"] == False
		assert result.data["attributes"] == [{
			"attr": "test",
			"host": "backend-0-0",
			"scope": "host",
			"type": "var",
			"value": "foo"
		}]

	def test_bad_name(self, run_ansible_module):
		result = run_ansible_module("stacki_attribute_info", scope="appliance", name="foo")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "not a valid appliance" in result.data["msg"]
