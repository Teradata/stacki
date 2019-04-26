from pathlib import Path

import pytest


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
