from stack.password import Password

from unittest.mock import patch

class TestPassword:
	@patch("os.getrandom")
	@patch("time.time")
	def test_get_rand_blocking_io(self, mock_time, mock_getrandom):
		mock_getrandom.side_effect = BlockingIOError

		assert len(Password().get_rand(16)) == 16
		assert mock_time.call_count == 16
