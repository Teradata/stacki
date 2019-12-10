import json
import tempfile
import textwrap


class TestReportNetworkfile:
	def test_report_networkfile(self, host):
		"Test that we can report the network file CSV and load it back in"

		# Grab the network info from CLI
		result = host.run("stack list network output-format=json")
		assert result.rc == 0
		network = json.loads(result.stdout)

		# Run the report command and make sure it matches what we expect
		result = host.run("stack report networkfile")
		assert result.rc == 0
		assert result.stdout == textwrap.dedent(f"""\
			NETWORK,ADDRESS,MASK,GATEWAY,MTU,ZONE,DNS,PXE\r
			private,{network[0]['address']},255.255.255.0,{network[0]['gateway']},,,False,True
			"""
		)

		# Write it to a temp file for the round trip
		with tempfile.NamedTemporaryFile('w') as f:
			f.write(result.stdout)

			# Load the network file
			result = host.run(f"stack load networkfile file={f.name}")
			assert result.rc == 0

		# Confirm nothing has changed
		result = host.run("stack list network output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == network
