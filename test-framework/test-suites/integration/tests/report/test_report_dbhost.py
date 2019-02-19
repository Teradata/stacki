import textwrap


class TestReportDbhost:
	def test_report_dbhost(self, host):
		result = host.run("stack report dbhost")
		assert result.rc == 0
		assert result.stdout == textwrap.dedent("""\
			<stack:file stack:name="/opt/stack/lib/python3.7/site-packages/stack/__init__.py" stack:mode="append">
			DatabaseHost = "frontend-0-0"
			</stack:file>
			"""
		)
