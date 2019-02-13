import sys
import requests
from unittest.mock import patch
sys.path.append('/opt/stack/bin')

import ludicrous_client

class TestLudicrousClient:
	def test_tracker(self):
		assert ludicrous_client.tracker() == ':80'

	@patch("requests.get")
	def test_lookup_file(self, mock_requests):
		ludicrous_client.lookup_file('asdf')
		mock_requests.assert_called_with('http://:80/ludicrous/lookup/asdf', timeout=(0.1, 5))

	def test_hashit(self):
		assert ludicrous_client.hashit('adsf') == '05c12a287334386c94131ab8aa00d08a'

	@patch("requests.post")
	def test_register_file(self, mock_requests):
		ludicrous_client.register_file('80', '05c12a287334386c94131ab8aa00d08a')
		mock_requests.assert_called_with('http://:80/ludicrous/register/80/05c12a287334386c94131ab8aa00d08a', timeout=(0.1, 5))

	@patch("requests.delete")
	def test_unregister_file(self, mock_requests):
		ludicrous_client.unregister_file('05c12a287334386c94131ab8aa00d08a', {})
		mock_requests.assert_called_with('http://:80/ludicrous/unregister/hashcode/05c12a287334386c94131ab8aa00d08a', params={}, timeout=(0.1, 5))

	@patch("requests.delete")
	def test_unregister_host(self, mock_requests):
		ludicrous_client.unregister_host('10.1.1.1')
		mock_requests.assert_called_with('http://:80/ludicrous/unregister/host/10.1.1.1', timeout=(0.1, 5))
	