import textwrap


class TestReportAnsible:
	def test_no_attributes_no_backends(self, host):
		"Test the output with no attribute parameter and no backends"

		result = host.run("stack report ansible")
		assert result.rc == 0
		assert result.stdout == textwrap.dedent("""\
			<stack:file stack:name="/etc/ansible/hosts">
			[frontend]
			frontend-0-0

			[rack0]
			frontend-0-0

			</stack:file>
			"""
		)

	def test_no_attributes_with_backends(self, host, add_host):
		"Test the output with no attribute parameter and one backend"

		result = host.run("stack report ansible")
		assert result.rc == 0
		assert result.stdout == textwrap.dedent("""\
			<stack:file stack:name="/etc/ansible/hosts">
			[backend]
			backend-0-0

			[managed]
			backend-0-0

			[rack0]
			backend-0-0
			frontend-0-0

			[frontend]
			frontend-0-0

			</stack:file>
			"""
		)

	def test_with_attributes(self, host, add_host):
		"Test the output with a few attribute parameters"

		# Create a few more backends
		add_host("backend-0-1", "0", "1", "backend")
		add_host("backend-1-0", "1", "0", "backend")

		# Try only setting an attr on the frontend
		host.run("stack set host attr frontend-0-0 attr='test.1' value=True")

		# Try only setting an attr on a backend and specificly false
		# on the frontend
		host.run("stack set host attr frontend-0-0 attr='test.2' value=False")
		host.run("stack set host attr backend-0-0 attr='test.2' value=True")

		# Try setting an attr on a few hosts, one in a different rack
		host.run("stack set host attr frontend-0-0 attr='test.3' value=True")
		host.run("stack set host attr backend-0-0 attr='test.3' value=True")
		host.run("stack set host attr backend-1-0 attr='test.3' value=True")

		# Now see if ansible outputs the attr groups as expected
		result = host.run("stack report ansible attribute=test.1,test.2,test.3")
		assert result.rc == 0
		assert result.stdout == textwrap.dedent("""\
			<stack:file stack:name="/etc/ansible/hosts">
			[backend]
			backend-0-0
			backend-0-1
			backend-1-0

			[managed]
			backend-0-0
			backend-0-1
			backend-1-0

			[rack0]
			backend-0-0
			backend-0-1
			frontend-0-0
			
			[test.2]
			backend-0-0
			frontend-0-0

			[test.3]
			backend-0-0
			backend-1-0
			frontend-0-0

			[rack1]
			backend-1-0
			
			[frontend]
			frontend-0-0

			[test.1]
			frontend-0-0

			</stack:file>
			"""
		)
