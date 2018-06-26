import os
import subprocess
import time

import pytest


@pytest.mark.usefixtures("revert_discovery")
class TestDisableDiscovery:
	def test_disable_daemon_not_running(self, host):
		"Test the discovery daemon is not started when not running"

		# Confirm the daemon isn't running
		assert len(host.process.filter(comm="stack")) == 0

		# Run the disable discovery command
		result = host.run("stack disable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has stopped\n"

		# Confirm the daemon still isn't running
		assert len(host.process.filter(comm="stack")) == 0

		# Confirm no log messages got written out
		assert host.file("/var/log/stack-discovery.log").content_string == ""

	def test_disable_daemon_running(self, host):
		"""
		Test the discovery daemon enable command works when the
		daemon is running
		"""

		# Start the daemon
		result = host.run("stack enable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has started\n"

		# Confirm a single daemon is running
		assert len(host.process.filter(comm="stack")) == 1
		
		# Run the disable discovery command
		result = host.run("stack disable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has stopped\n"

		# Give the OS a second to fully teardown the process
		time.sleep(1)

		# Confirm the daemon isn't running
		assert len(host.process.filter(comm="stack")) == 0

		# Confirm the log messages got written out
		log_file = host.file("/var/log/stack-discovery.log")
		assert log_file.exists

		lines = log_file.content_string.strip().split('\n')
		assert len(lines) == 2
		assert "INFO: discovery daemon started" in lines[0]
		assert "INFO: discovery daemon stopped" in lines[1]
