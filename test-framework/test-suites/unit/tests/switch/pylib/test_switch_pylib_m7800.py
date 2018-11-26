import pytest
from unittest.mock import patch

import json

from stack.switch.m7800 import SwitchMellanoxM7800

INPUT_DATA = [
	['m7800_parse_partitions_input.txt', 'm7800_parse_partitions_output.json'],
	['m7800_parse_partitions_with_member_named_all_input.txt', 'm7800_parse_partitions_with_member_named_all_output.json'],
]

class TestSwitchMellanoxM7800:

	@pytest.mark.parametrize('input_file,output_file', INPUT_DATA)
	@patch('stack.switch.m7800.ExpectMore')
	def test_partitions_can_parse_guid_members(self, mock_expectmore, input_file, output_file):
		dirn = '/export/test-files/switch/'
		expected_output = json.load(open(dirn + output_file))
		input_data = open(dirn + input_file).read().splitlines()

		mock_expectmore.return_value.isalive.return_value = True
		mock_expectmore.return_value.ask.return_value = input_data

		s = SwitchMellanoxM7800('fakeip')
		assert(s.partitions == expected_output)
