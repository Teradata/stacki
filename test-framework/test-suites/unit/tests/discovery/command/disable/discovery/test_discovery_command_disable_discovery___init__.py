from unittest.mock import patch

from stack.commands.report.discovery import Command


class TestCommand:
	@patch("stack.commands.report.discovery.Discovery")
	def test_run_daemon_running(self, mock_discovery):
		"Test the run method when the discovery daemon is running."

		# Mock out the is_running method of the Discovery class
		mock_discovery.return_value.is_running.return_value = True
		
		# Create our command to test and call the 'run' command
		command = Command(None)

		# NOTE: This is probably a bug in Command, _params should default to
		# {} instead of None
		command._params = {}
		command.run(None, None)

		# Sanity check that the mocked method was called
		assert mock_discovery.return_value.is_running.called

		# Make sure the output is as expected
		assert command.output == [["", "Discovery daemon is running"]]
	
	@patch("stack.commands.report.discovery.Discovery")
	def test_run_daemon_stopped(self, mock_discovery):
		"Test the run method when the discovery daemon is stopped."
		
		# Mock out the is_running method of the Discovery class
		mock_discovery.return_value.is_running.return_value=False
		
		# Create our command to test and call the 'run' command
		command = Command(None)

		# NOTE: This is probably a bug in Command, _params should default to
		# {} instead of None
		command._params = {}
		command.run(None, None)
		
		# Sanity check that the mocked method was called
		assert mock_discovery.return_value.is_running.called
		
		# Make sure the output is as expected
		assert command.output == [["", "Discovery daemon is stopped"]]
