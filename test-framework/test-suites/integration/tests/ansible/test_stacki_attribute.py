import json


class TestStackiAttribute:
	def test_add_global_attribute(self, host, run_ansible_module):
		# Add the attribute
		result = run_ansible_module("stacki_attribute", attr="test", value="foo")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list attr attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"scope": "global",
			"type": "var",
			"value": "foo"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", attr="test", value="foo")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_add_global_attribute_with_shadow(self, host, run_ansible_module):
		# Add the attribute
		result = run_ansible_module("stacki_attribute", attr="test", value="foo", shadow=True)
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list attr attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"scope": "global",
			"type": "shadow",
			"value": "foo"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", attr="test", value="foo", shadow=True)
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_modify_global_attribute(self, host, run_ansible_module):
		# Add the attribute via the CLI
		result = host.run(f'stack add attr attr=test value=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run("stack list attr attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"scope": "global",
			"type": "var",
			"value": "foo"
		}]

		# Now change the value
		result = run_ansible_module("stacki_attribute", attr="test", value="bar")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that the value changed
		result = host.run("stack list attr attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"scope": "global",
			"type": "var",
			"value": "bar"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", attr="test", value="bar")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_remove_global_attribute(self, host, run_ansible_module):
		# Add the attribute via the CLI
		result = host.run(f'stack add attr attr=test value=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run("stack list attr attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"scope": "global",
			"type": "var",
			"value": "foo"
		}]

		# Remove the attribute
		result = run_ansible_module("stacki_attribute", attr="test", state="absent")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Make sure it got removed
		result = host.run(f'stack list attr attr=test')
		assert result.rc == 0
		assert result.stdout == ''

		# Test idempotency by removing again
		result = run_ansible_module("stacki_attribute", attr="test", state="absent")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_add_appliance_attribute(self, host, run_ansible_module):
		# Add the attribute
		result = run_ansible_module("stacki_attribute", name="backend", scope="appliance", attr="test", value="foo")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list appliance attr backend attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"appliance": "backend",
			"attr": "test",
			"scope": "appliance",
			"type": "var",
			"value": "foo"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", name="backend", scope="appliance", attr="test", value="foo")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_modify_appliance_attribute(self, host, run_ansible_module):
		# Add the attribute via the CLI
		result = host.run(f'stack add appliance attr backend attr=test value=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run("stack list appliance attr backend attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"appliance": "backend",
			"attr": "test",
			"scope": "appliance",
			"type": "var",
			"value": "foo"
		}]

		# Now change the value
		result = run_ansible_module("stacki_attribute", name="backend", scope="appliance", attr="test", value="bar")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that the value changed
		result = host.run("stack list appliance attr backend attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"appliance": "backend",
			"attr": "test",
			"scope": "appliance",
			"type": "var",
			"value": "bar"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", name="backend", scope="appliance", attr="test", value="bar")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_remove_appliance_attribute(self, host, run_ansible_module):
		# Add the attribute via the CLI
		result = host.run(f'stack add appliance attr backend attr=test value=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run("stack list appliance attr backend attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"appliance": "backend",
			"attr": "test",
			"scope": "appliance",
			"type": "var",
			"value": "foo"
		}]

		# Remove the attribute
		result = run_ansible_module("stacki_attribute", name="backend", scope="appliance", attr="test", state="absent")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Make sure it got removed
		result = host.run(f'stack list appliance attr backend attr=test')
		assert result.rc == 0
		assert result.stdout == ''

		# Test idempotency by removing again
		result = run_ansible_module("stacki_attribute", name="backend", scope="appliance", attr="test", state="absent")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_add_os_attribute(self, host, run_ansible_module):
		# Add the attribute
		result = run_ansible_module("stacki_attribute", name="sles", scope="os", attr="test", value="foo")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list os attr sles attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"os": "sles",
			"scope": "os",
			"type": "var",
			"value": "foo"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", name="sles", scope="os", attr="test", value="foo")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_modify_os_attribute(self, host, run_ansible_module):
		# Add the attribute via the CLI
		result = host.run(f'stack add os attr sles attr=test value=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run("stack list os attr sles attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"os": "sles",
			"scope": "os",
			"type": "var",
			"value": "foo"
		}]

		# Now change the value
		result = run_ansible_module("stacki_attribute", name="sles", scope="os", attr="test", value="bar")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that the value changed
		result = host.run("stack list os attr sles attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"os": "sles",
			"scope": "os",
			"type": "var",
			"value": "bar"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", name="sles", scope="os", attr="test", value="bar")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_remove_os_attribute(self, host, run_ansible_module):
		# Add the attribute via the CLI
		result = host.run(f'stack add os attr sles attr=test value=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run("stack list os attr sles attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"os": "sles",
			"scope": "os",
			"type": "var",
			"value": "foo"
		}]

		# Remove the attribute
		result = run_ansible_module("stacki_attribute", name="sles", scope="os", attr="test", state="absent")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Make sure it got removed
		result = host.run(f'stack list os attr sles attr=test')
		assert result.rc == 0
		assert result.stdout == ''

		# Test idempotency by removing again
		result = run_ansible_module("stacki_attribute", name="sles", scope="os", attr="test", state="absent")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_add_environment_attribute(self, add_environment, host, run_ansible_module):
		# Add the attribute
		result = run_ansible_module("stacki_attribute", name="test", scope="environment", attr="test", value="foo")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list environment attr test attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"environment": "test",
			"scope": "environment",
			"type": "var",
			"value": "foo"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", name="test", scope="environment", attr="test", value="foo")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_modify_environment_attribute(self, add_environment, host, run_ansible_module):
		# Add the attribute via the CLI
		result = host.run(f'stack add environment attr test attr=test value=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run("stack list environment attr test attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"environment": "test",
			"scope": "environment",
			"type": "var",
			"value": "foo"
		}]

		# Now change the value
		result = run_ansible_module("stacki_attribute", name="test", scope="environment", attr="test", value="bar")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that the value changed
		result = host.run("stack list environment attr test attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"environment": "test",
			"scope": "environment",
			"type": "var",
			"value": "bar"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", name="test", scope="environment", attr="test", value="bar")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_remove_environment_attribute(self, add_environment, host, run_ansible_module):
		# Add the attribute via the CLI
		result = host.run(f'stack add environment attr test attr=test value=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run("stack list environment attr test attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"environment": "test",
			"scope": "environment",
			"type": "var",
			"value": "foo"
		}]

		# Remove the attribute
		result = run_ansible_module("stacki_attribute", name="test", scope="environment", attr="test", state="absent")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Make sure it got removed
		result = host.run(f'stack list environment attr test attr=test')
		assert result.rc == 0
		assert result.stdout == ''

		# Test idempotency by removing again
		result = run_ansible_module("stacki_attribute", name="test", scope="environment", attr="test", state="absent")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_add_host_attribute(self, add_host, host, run_ansible_module):
		# Add the attribute
		result = run_ansible_module("stacki_attribute", name="backend-0-0", scope="host", attr="test", value="foo")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that it is there now
		result = host.run("stack list host attr backend-0-0 attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"host": "backend-0-0",
			"scope": "host",
			"type": "var",
			"value": "foo"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", name="backend-0-0", scope="host", attr="test", value="foo")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_modify_host_attribute(self, add_host, host, run_ansible_module):
		# Add the attribute via the CLI
		result = host.run(f'stack add host attr backend-0-0 attr=test value=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run("stack list host attr backend-0-0 attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"host": "backend-0-0",
			"scope": "host",
			"type": "var",
			"value": "foo"
		}]

		# Now change the value
		result = run_ansible_module("stacki_attribute", name="backend-0-0", scope="host", attr="test", value="bar")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Check that the value changed
		result = host.run("stack list host attr backend-0-0 attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"host": "backend-0-0",
			"scope": "host",
			"type": "var",
			"value": "bar"
		}]

		# Test idempotency by adding again
		result = run_ansible_module("stacki_attribute", name="backend-0-0", scope="host", attr="test", value="bar")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_remove_host_attribute(self, add_host, host, run_ansible_module):
		# Add the attribute via the CLI
		result = host.run(f'stack add host attr backend-0-0 attr=test value=foo')
		assert result.rc == 0

		# Check that it is there now
		result = host.run("stack list host attr backend-0-0 attr=test output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"attr": "test",
			"host": "backend-0-0",
			"scope": "host",
			"type": "var",
			"value": "foo"
		}]

		# Remove the attribute
		result = run_ansible_module("stacki_attribute", name="backend-0-0", scope="host", attr="test", state="absent")
		assert result.status == "CHANGED"
		assert result.data["changed"] == True

		# Make sure it got removed
		result = host.run(f'stack list host attr backend-0-0 attr=test')
		assert result.rc == 0
		assert result.stdout == ''

		# Test idempotency by removing again
		result = run_ansible_module("stacki_attribute", name="backend-0-0", scope="host", attr="test", state="absent")
		assert result.status == "SUCCESS"
		assert result.data["changed"] == False

	def test_bad_attr(self, run_ansible_module):
		result = run_ansible_module("stacki_attribute", attr="Kickstart_*", state="absent")

		assert result.status == "FAILED!"
		assert result.data["changed"] == False

		assert "error" in result.data["msg"]
		assert "more than one attribute matches attr" in result.data["msg"]
