import os
import subprocess

import pytest


@pytest.mark.usefixtures("revert_discovery")
class TestReportDiscovery:
	def test_report_daemon_not_running(self, host):
		"Test the output when the discovery daemon is not running"

		# Make sure discovery isn't running
		result = host.run("stack disable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has stopped\n"

		# See what reports says
		result = host.run("stack report discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon is stopped\n"

	def test_report_daemon_running(self, host):
		"Test the output when the discovery daemon is running"

		# We gotta start discovery
		result = host.run("stack enable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has started\n"

		# See what report says
		result = host.run("stack report discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon is running\n"
