from pathlib import Path

import pytest
import stack.api

# Everything in "fixures" gets loaded as a plugin
pytest_plugins = [
	f"stack.commands.report.system.fixtures.{path.stem}" for path in Path(__file__).parent.glob("fixtures/*.py")
	if path.stem != "__init__"
]

_SUMMARY_LOG = []
def pytest_terminal_summary(terminalreporter):
	terminalreporter.write("\n")
	terminalreporter.section("Cluster Data")
	for title, output in _SUMMARY_LOG:
		terminalreporter.write("\n")
		terminalreporter.section(title, "-")
		terminalreporter.write("\n")
		terminalreporter.write(output)
	terminalreporter.write("\n")

@pytest.fixture
def report_output():
	def _inner(title, output):
		_SUMMARY_LOG.append((title, output))

	return _inner

@pytest.fixture(scope="session")
def backend_ips():
	"""
	Returns a dictionary where the key is the backend hostname and
	the value is a set of IPs assigned to the backend.
	"""

	results = {}
	for hostname in [host["host"] for host in stack.api.Call("list host", args=["a:backend"])]:
		results[hostname] = set([
			interface["ip"]
			for interface in stack.api.Call(f"list host interface", args=[hostname])
			if interface["ip"]
		])

	return results
