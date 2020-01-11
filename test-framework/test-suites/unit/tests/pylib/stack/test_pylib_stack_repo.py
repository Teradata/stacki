import pytest

import stack.repo

FAKE_REPO_FILE = '''[fakealias]
name=fakename
baseurl=url:///
type=rpm-md
gpgcheck=0'''

FAKE_REPO_DATA = {
	'name': 'fakename',
	'alias': 'fakealias',
	'url': 'url:///',
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

class TestRepo:

	def test_build_repo_files(self):
		repo_stanzas = stack.repo.build_repo_files(
			{'fakebox': {'fakename': FAKE_REPO_DATA}},
			stack.repo.yum_repo_template
		)

		assert '\n'.join(repo_stanzas) == FAKE_REPO_FILE

