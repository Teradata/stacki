from collections import defaultdict
import os.path
import re

import pytest
import stack.api


class TestBackendInstalls:
	@pytest.fixture(scope="session")
	def checklist_statuses(self):
		statuses = defaultdict(str)

		# Parse the checklist.log file, gathering the last status for each IP
		if os.path.exists("/var/log/checklist.log"):
			last_ip = None
			with open("/var/log/checklist.log", 'r') as log:
				for line in log:
					# Are we the start of a new status block?
					match = re.search(
						r"Installation Status Messages for ([\d.]+)", line
					)
					if match:
						last_ip = match.group(1)
						statuses[last_ip] = line
						continue

					# Are we the end of the status block?
					match = re.match(r"#+$", line)
					if match:
						last_ip = None
						continue

					# Else, we are in a status block
					statuses[last_ip] += line

		return statuses

	@pytest.mark.parametrize("backend", sorted([
		host["host"] for host in stack.api.Call("list host", args=["a:backend"])
	]))
	def test_backend(self, backend, backend_ips, checklist_statuses, report_output):
		# There *should* only be a single checlist status for each backend, but
		# just in case we run through all IPs on the backend and first one wins
		status = ""
		for ip in backend_ips[backend]:
			if checklist_statuses[ip]:
				status = checklist_statuses[ip]
				break

		if status:
			try:
				# Make sure the install didn't stall
				assert "State.Installation_Stalled" not in status, "Install stalled"

				# Make sure we got to the Reboot_Okay state
				assert "State.Reboot_Okay" in status, "Install never finished"
			except AssertionError:
				# If we failed, add the latest system checklist status to the report output
				report_output(f"system checklist - {backend}", status)

				raise
