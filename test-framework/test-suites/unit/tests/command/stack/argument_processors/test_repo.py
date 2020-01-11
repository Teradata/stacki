from unittest.mock import create_autospec, ANY
import pytest

from operator import itemgetter

from stack.argument_processors.repo import RepoArgProcessor
from stack.commands import DatabaseConnection
from stack.exception import ArgError

FAKE_REPO_DATA = {
	'name': 'fakename',
	'alias': 'fakealias',
	'url': 'uri:///',
	'autorefresh': 0,
	'assumeyes': 0,
	'type': 'rpm-md',
	'is_mirrorlist': 0,
	'gpgcheck': 0,
	'gpgkey': '',
	'os': 'sles',
	'pallet_id': None,
	'is_enabled': 1
}

REPO_NON_REQUIRED_ARGS = [
	{'is_mirrorlist': 1},
	{'EXTRA_IGNORED': 'KWARG'},
	{'is_mirrorlist': 1, 'EXTRA_IGNORED': 'KWARG'},
	{'autorefresh': '1'},
	{'type': 'yast'},
]

class TestRepoArgumentProcessor:
	@pytest.fixture
	def argument_processor(self):
		test_arg_processor = RepoArgProcessor()
		test_arg_processor.db = create_autospec(DatabaseConnection, instance=True)
		return test_arg_processor

	def test_repo_not_found(self, argument_processor):
		argument_processor.db.select.return_value = ()
		assert argument_processor.get_repo_id('no_such_repo') == None

	def test_get_repos_by_box(self, argument_processor):
		fakebox_name = 'fakebox'
		fakebox_id = 0
		argument_processor.db.select.side_effect = [
			[[fakebox_id]],
			[list(FAKE_REPO_DATA.values())[0:-1]]
		]
		assert {fakebox_name: {FAKE_REPO_DATA['name']: FAKE_REPO_DATA}} == argument_processor.get_repos_by_box(fakebox_name)
		argument_processor.db.select.assert_called_with(ANY, (fakebox_id,))

	def test_insert_repo(self, argument_processor):
		# setup the id check in the db to be empty
		argument_processor.db.select.return_value = ()

		basic_repo_data = itemgetter('name', 'alias', 'url')(FAKE_REPO_DATA)
		argument_processor.insert_repo(*basic_repo_data)

		# verify db call sequence
		argument_processor.db.select.assert_called_once_with(ANY, (basic_repo_data[0], basic_repo_data[1]))
		argument_processor.db.execute.assert_called_once_with(ANY, basic_repo_data)

	@pytest.mark.parametrize("kwargs", REPO_NON_REQUIRED_ARGS)
	def test_insert_repo_optional_args(self, argument_processor, kwargs):
		''' many columns in the repos table are optional - the arg proc should ignore invalid columns '''
		# setup the id check in the db to be empty
		argument_processor.db.select.return_value = ()

		basic_repo_data = itemgetter('name', 'alias', 'url')(FAKE_REPO_DATA)
		argument_processor.insert_repo(*basic_repo_data, **kwargs)

		expected_vals = []
		for key in argument_processor.OPTIONAL_REPO_COLUMNS:
			if key in kwargs:
				expected_vals.append(kwargs[key])

		# verify db call sequence only has expected key/vals
		argument_processor.db.select.assert_called_once_with(ANY, (basic_repo_data[0], basic_repo_data[1]))
		argument_processor.db.execute.assert_called_with(ANY, basic_repo_data + tuple(expected_vals))

	def test_insert_repo_already_exists(self, argument_processor):
		# setup the id check in the db to be empty
		argument_processor.db.select.return_value = ()

		basic_repo_data = itemgetter('name', 'alias', 'url')(FAKE_REPO_DATA)
		argument_processor.insert_repo(*basic_repo_data)

		argument_processor.db.select.assert_called_once_with(ANY, (basic_repo_data[0], basic_repo_data[1]))
		argument_processor.db.execute.assert_called_once_with(ANY, basic_repo_data)

		# now re-attempt insert which should fail
		# reset test fixture
		argument_processor.db.reset_mock()
		argument_processor.db.select.return_value = ((1,),)

		with pytest.raises(ArgError):
			argument_processor.insert_repo(*basic_repo_data)

		# verify db call sequence
		argument_processor.db.select.assert_called_once_with(ANY, (basic_repo_data[0], basic_repo_data[1]))
		argument_processor.db.execute.assert_not_called()
