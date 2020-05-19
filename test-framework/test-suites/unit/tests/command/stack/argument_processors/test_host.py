from unittest.mock import create_autospec
import pytest

from stack.argument_processors.host import HostArgProcessor
from stack.commands import DatabaseConnection

class TestHostArgumentProcessor:
	@pytest.fixture
	def argument_processor(self):
		test_arg_processor = HostArgProcessor()
		test_arg_processor.db = create_autospec(DatabaseConnection, instance=True)
		return test_arg_processor

	def test_get_hostnames_host_filter_returns_list(self, argument_processor):
		''' test that when calling getHostnames(args, host_filter=callable) the result is a list and not a filter_object '''
		argument_processor.db.select.side_effect = [
			(('frontend-0-0',),),
			(('fake-array', '1', '3'), ('fakehost-0-0', '1', '2')),
		]

		argument_processor.db.getHostname.side_effect = ['fake-array', 'fake-array']
		argument_processor.db.getHostAppliance.return_value = 'netapp_array'
		# host_filter verifying getHostAppliance is a common check
		assert ['fake-array'] == argument_processor.getHostnames(
			['fake-array'],
			host_filter=lambda self, host: self.db.getHostAppliance(host) == 'netapp_array'
		)
