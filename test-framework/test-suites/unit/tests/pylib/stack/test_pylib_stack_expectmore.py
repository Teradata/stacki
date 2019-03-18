from unittest.mock import create_autospec, PropertyMock
import pexpect
import tempfile
import pytest
from contextlib import ExitStack
from stack.expectmore import ExpectMore

class TestExpectMore:
	"""A test case containing tests for the expectmore class."""
	# A list of the names of the buffer properties of the ExpectMore class to test.
	# This will need to be updated should the class definition change.
	EXPECTMORE_BUFFER_PROPERTIES = ["before", "after"]

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
