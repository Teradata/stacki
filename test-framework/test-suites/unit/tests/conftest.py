import os.path

import pytest


@pytest.fixture(scope="session")
def test_file():
	def _inner(path):
		return os.path.join("/export/test-suites/unit/files", path)

	return _inner
