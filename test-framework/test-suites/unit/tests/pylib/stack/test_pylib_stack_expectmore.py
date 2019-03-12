from unittest.mock import create_autospec, PropertyMock
import pexpect
import tempfile
import pytest
from contextlib import ExitStack
from stack.expectmore import ExpectMore

class TestExpectMore:
	"""A test case containing tests for the expectmore class."""
	# A list of the names of the logfile properties of the ExpectMore class to test.
	# This will need to be updated should the class definition change.
	EXPECTMORE_LOGFILE_PROPERTIES = ["logfile", "logfile_read", "logfile_send"]
	# A list of the names of the buffer properties of the ExpectMore class to test.
	# This will need to be updated should the class definition change.
	EXPECTMORE_BUFFER_PROPERTIES = ["before", "after"]

	@pytest.mark.parametrize("property_name", EXPECTMORE_LOGFILE_PROPERTIES)
	def test_logfile(self, property_name):
		"""Test that the logfile properties return the logfile on the spawn object used to manage the child process."""
		mock_pexpect_spawn = create_autospec(
			spec = pexpect.spawn,
			instance = True,
		)
		# need to add the mock spawn instance as the _proc on the expectmore instance.
		test_expectmore = ExpectMore()
		test_expectmore._proc = mock_pexpect_spawn

		# Create a temporary file to set the logfile to
		with tempfile.TemporaryFile() as temp_file:
			# set the file on the mock
			setattr(mock_pexpect_spawn, property_name, temp_file)
			# expect the value to be returned as expected
			assert temp_file == getattr(test_expectmore, property_name)

	@pytest.mark.parametrize("property_name", EXPECTMORE_LOGFILE_PROPERTIES)
	def test_set_logfile(self, property_name):
		"""Test that the logfile properties set the logfile on the spawn object used to manage the child process."""
		mock_pexpect_spawn = create_autospec(
			spec = pexpect.spawn,
			instance = True,
		)
		# need to add the mock spawn instance as the _proc on the expectmore instance.
		test_expectmore = ExpectMore()
		test_expectmore._proc = mock_pexpect_spawn

		# Create a temporary file to set the logfile to
		with tempfile.TemporaryFile() as temp_file:
			# set the file via the property
			setattr(test_expectmore, property_name, temp_file)
			# expect the value to be set on the _proc instance
			assert temp_file == getattr(mock_pexpect_spawn, property_name)

	def test_redirect_to_logfile(self):
		"""Test that the context manager overrides the files while in the context and reverts on exit."""
		mock_pexpect_spawn = create_autospec(
			spec = pexpect.spawn,
			instance = True,
		)
		# Use an exitstack to collect all the tempfile context managers and clean them all up on exit.
		with ExitStack() as cleanup:
			# add temporary files for each logfile property to the mock spawn instance.
			original_files = {property_name: cleanup.enter_context(tempfile.TemporaryFile()) for property_name in self.EXPECTMORE_LOGFILE_PROPERTIES}
			for property_name, temp_file in original_files.items():
				setattr(mock_pexpect_spawn, property_name, temp_file)

			# need to add the mock spawn instance as the _proc on the expectmore instance.
			test_expectmore = ExpectMore()
			test_expectmore._proc = mock_pexpect_spawn

			# Use the context manager function to overwrite to new temporary files.
			new_files = {property_name: cleanup.enter_context(tempfile.TemporaryFile()) for property_name in self.EXPECTMORE_LOGFILE_PROPERTIES}
			with test_expectmore.redirect_to_logfile(**new_files):
				for property_name in self.EXPECTMORE_LOGFILE_PROPERTIES:
					assert getattr(mock_pexpect_spawn, property_name) != original_files[property_name]
					assert getattr(mock_pexpect_spawn, property_name) == new_files[property_name]

			# Ensure the files are reset on exit
			for property_name in self.EXPECTMORE_LOGFILE_PROPERTIES:
				assert getattr(mock_pexpect_spawn, property_name) == original_files[property_name]
				assert getattr(mock_pexpect_spawn, property_name) != new_files[property_name]

	@pytest.mark.parametrize("property_name", EXPECTMORE_BUFFER_PROPERTIES)
	def test_before_after(self, property_name):
		"""Test that the property returns the value of the associated buffer attribute of pexpect.spawn split across lines."""
		mock_pexpect_spawn = create_autospec(
			spec = pexpect.spawn,
			instance = True,
		)
		mock_attribute = PropertyMock(return_value = b"foo\nbar")
		setattr(type(mock_pexpect_spawn), property_name, mock_attribute)
		# Need to add the mock spawn instance as the _proc on the expectmore instance.
		test_expectmore = ExpectMore()
		test_expectmore._proc = mock_pexpect_spawn

		# Read the property
		result = getattr(test_expectmore, property_name)

		# Expect the attribute to be accessed
		mock_attribute.assert_called_once_with()
		# Expect the result to match the expected result
		assert mock_attribute.return_value.decode().splitlines() == result
