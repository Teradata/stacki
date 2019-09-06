from textwrap import dedent

class TestSetHostPower:
	def test_single_host(self, host):
		result = host.run('stack set host power backend-0-0 command="status"')
		assert result.rc == 0
		assert result.stdout.strip() == 'Chassis Power is on'

	def test_multiple_hosts(self, host):
		result = host.run('stack set host power backend-0-0 backend-0-1 command="status"')
		assert result.rc == 0
		power_count = 0
		for line in result.stdout.splitlines():
			if "Chassis Power is on" in line:
				power_count += 1
		assert power_count == 2

	def test_invalid_command(self, host):
		result = host.run('stack set host power backend-0-0 command="invalid_command"')
		assert result.rc == 255

	def test_invalid_host(self, host):
		result = host.run('stack set host power invalid_host command="status"')
		assert result.rc == 255
		assert result.stderr.strip() == 'error - cannot resolve host "invalid_host"'

	def test_invalid_method(self, host):
		result = host.run('stack set host power backend-0-0 command="status" method=invalid_method')
		assert result.rc == 255

	def test_invalid_ipmi(self, host):
		result = host.run('stack set host power backend-0-0 command="status" debug=y method=ipmi')
		assert result.rc == 0
		assert result.stdout == dedent('''\
		Failed to set power via ipmi: "backend-0-0 missing ipmi interface"
		Could not set power cmd status on host backend-0-0
		''')
