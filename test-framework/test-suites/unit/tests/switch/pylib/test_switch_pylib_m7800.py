import pytest
from unittest.mock import patch
from unittest.mock import ANY
from collections import namedtuple

import json

from stack.switch.m7800 import SwitchMellanoxM7800, remove_blank_lines
from stack.switch import SwitchException

INPUT_DATA = [
	['m7800_parse_partitions_input.txt', 'm7800_parse_partitions_output.json'],
	['m7800_parse_partitions_with_member_named_all_input.txt', 'm7800_parse_partitions_with_member_named_all_output.json'],
]

class TestUtil:
	def test_remove_blank_lines(self):
		"""Test that blank lines are removed"""
		assert(remove_blank_lines(['', '      ', '			', 'blorg!']) == ['blorg!'])

@patch('stack.switch.m7800.ExpectMore', autospec = True)
class TestSwitchMellanoxM7800:

	@pytest.mark.parametrize('input_file,output_file', INPUT_DATA)
	def test_partitions_can_parse_guid_members(self, mock_expectmore, input_file, output_file):
		dirn = '/export/test-files/switch/'
		expected_output = json.load(open(dirn + output_file))
		with open(dirn + input_file) as test_file:
			input_data = test_file.read().splitlines()

		mock_expectmore.return_value.isalive.return_value = True
		mock_expectmore.return_value.ask.return_value = input_data

		s = SwitchMellanoxM7800('fakeip')
		assert(s.partitions == expected_output)

	def test_reload(self, mock_expectmore):
		"""Expect this to end the conversation and request a reload."""
		test_switch = SwitchMellanoxM7800('fakeip')
		test_switch.reload()
		mock_expectmore.return_value.end.assert_called_with('reload noconfirm')

	def test_image_boot_next(self, mock_expectmore):
		"""Expect this to set the next image to boot as the new image."""
		test_switch = SwitchMellanoxM7800('fakeip')
		test_switch.image_boot_next()
		mock_expectmore.return_value.ask.assert_called_with('image boot next')

	def test_image_boot_next_error(self, mock_expectmore):
		"""Expect this to raise an error if there is an error response."""
		test_switch = SwitchMellanoxM7800('fakeip')
		error_message = '% strange error'
		mock_expectmore.return_value.ask.return_value = [error_message]
		with pytest.raises(SwitchException) as exception:
			test_switch.image_boot_next()
		assert(error_message in str(exception))

	def test_install_firmware(self, mock_expectmore):
		"""Expect this to try to install the user requested firmware."""
		with open('/export/test-files/switch/m7800_install_image_console.txt') as test_file:
			mock_expectmore.return_value.ask.return_value = test_file.read().splitlines()
		test_switch = SwitchMellanoxM7800('fakeip')
		firmware_name = 'my_amazing_firmware'
		test_switch.install_firmware(image = firmware_name)
		mock_expectmore.return_value.ask.assert_called_with(
			f'image install {firmware_name}',
			timeout=ANY
		)

	def test_install_firmware_no_steps(self, mock_expectmore):
		"""Expect an error because there were no steps that appeared to be performed."""
		test_switch = SwitchMellanoxM7800('fakeip')
		firmware_name = 'my_amazing_firmware'
		mock_expectmore.return_value.ask.return_value = []
		with pytest.raises(SwitchException):
			test_switch.install_firmware(image = firmware_name)

	def test_install_firmware_not_enough_steps(self, mock_expectmore):
		"""Expect an error because there were not enough steps that appeared to be performed."""
		test_switch = SwitchMellanoxM7800('fakeip')
		firmware_name = 'my_amazing_firmware'
		mock_expectmore.return_value.ask.return_value = ['Step 1 of 4: Verify Image', '100.0%', '100.0%', '100.0%',]
		with pytest.raises(SwitchException):
			test_switch.install_firmware(image = firmware_name)

	def test_image_delete(self, mock_expectmore):
		"""Expect this to try to delete the user requested firmware."""
		test_switch = SwitchMellanoxM7800('fakeip')
		firmware_name = 'my_amazing_firmware'
		test_switch.image_delete(image = firmware_name)
		mock_expectmore.return_value.ask.assert_called_with(f'image delete {firmware_name}')

	def test_image_delete_error(self, mock_expectmore):
		"""Expect this to raise an error if there is an error response."""
		test_switch = SwitchMellanoxM7800('fakeip')
		firmware_name = 'my_amazing_firmware'
		error_message = '% file not found'
		mock_expectmore.return_value.ask.return_value = [error_message]

		with pytest.raises(SwitchException) as exception:
			test_switch.image_delete(image = firmware_name)
		assert(error_message in str(exception))

	@pytest.mark.parametrize('protocol', SwitchMellanoxM7800.SUPPORTED_IMAGE_FETCH_PROTOCOLS)
	def test_image_fetch(self, mock_expectmore, protocol):
		"""Expect this to try to fetch the user requested firmware."""
		test_switch = SwitchMellanoxM7800('fakeip')
		firmware_url = f'{protocol}sometrustworthysite.ru'
		# add success condition return value
		mock_expectmore.return_value.ask.return_value = ['100.0%']
		test_switch.image_fetch(url = firmware_url)
		mock_expectmore.return_value.ask.assert_called_with(
			f'image fetch {firmware_url}',
			timeout=ANY
		)

	def test_image_fetch_bad_protocol(self, mock_expectmore):
		"""Expect an error to be raised on an unsupported protocol."""
		test_switch = SwitchMellanoxM7800('fakeip')
		firmware_url = 'git://user@sometrusworthysite.ru/sometrustworthyrepo.git'
		# add success condition return value to ensure the exception is because of the
		# unsupported protocol.
		mock_expectmore.return_value.ask.return_value = ['100.0%']

		with pytest.raises(SwitchException):
			test_switch.image_fetch(url = firmware_url)

	def test_image_fetch_error_with_message(self, mock_expectmore):
		"""Expect an error to be raised due to a missing success indicator and the error message to be captured."""
		test_switch = SwitchMellanoxM7800('fakeip')
		firmware_url = f'{test_switch.SUPPORTED_IMAGE_FETCH_PROTOCOLS[0]}://sometrustworthysite.ru'

		error_message = '% unauthorized'
		mock_expectmore.return_value.ask.return_value = ['other junk', error_message,]
		with pytest.raises(SwitchException) as exception:
			test_switch.image_fetch(url = firmware_url)
		assert(error_message in str(exception))

	def test_image_fetch_error_without_message(self, mock_expectmore):
		"""Expect an error to be raised due to a missing success indicator.

		The error message is not captured because it is missing the beggining % symbol.
		"""
		test_switch = SwitchMellanoxM7800('fakeip')
		firmware_url = f'{test_switch.SUPPORTED_IMAGE_FETCH_PROTOCOLS[0]}://sometrustworthysite.ru'

		irrelevant_output = ['other junk', 'irrelevant',]
		mock_expectmore.return_value.ask.return_value = irrelevant_output
		with pytest.raises(SwitchException) as exception:
			test_switch.image_fetch(url = firmware_url)
		assert(not any((output in str(exception) for output in irrelevant_output)))

	def test_show_images(self, mock_expectmore):
		"""Expect this to try to list the current and available firmware images."""
		test_switch = SwitchMellanoxM7800('fakeip')
		with open('/export/test-files/switch/m7800_show_images_console.txt') as test_file:
			test_console_response = test_file.read().splitlines()

		expected_data = (
			{
				1: 'X86_64 3.6.4006 2017-07-03 16:17:39 x86_64',
				2: 'X86_64 3.6.4006 2017-07-03 16:17:39 x86_64',
			},
			2,
			1,
			[
				('image-X86_64-3.6.2002.img', 'X86_64 3.6.2002 2016-09-28 21:00:15 x86_64'),
				('image-X86_64-3.6.3004.img', 'X86_64 3.6.3004 2017-02-05 17:31:53 x86_64'),
				('image-X86_64-3.6.4006.img', 'X86_64 3.6.4006 2017-07-03 16:17:39 x86_64'),
				('image-X86_64-3.6.5009.img', 'X86_64 3.6.5009 2018-01-02 07:42:21 x86_64'),
				('image-X86_64-3.6.8010.img', 'X86_64 3.6.8010 2018-08-20 18:04:19 x86_64'),
			],
		)
		mock_expectmore.return_value.ask.return_value = test_console_response
		assert(test_switch.show_images() == expected_data)
		mock_expectmore.return_value.ask.assert_called_with('show images')

	def test_show_images_no_data(self, mock_expectmore):
		"""Test that an error is raised when nothing is returned from the switch."""
		mock_expectmore.return_value.ask.return_value = []
		test_switch = SwitchMellanoxM7800('fakeip')
		with pytest.raises(SwitchException):
			test_switch.show_images()

	def test__get_errors(self, mock_expectmore):
		"""Confirm that strings starting with '%' are treated as errors."""
		test_response = ['foobar%%%%%%', 'f%o%b%a%r%', '%foobar%', '%errors!']
		test_switch = SwitchMellanoxM7800('fakeip')
		expected = sorted(['%foobar%', '%errors!'])
		assert(sorted(test_switch._get_errors(command_response = test_response)) == expected)

	def test__get_expected_errors(self, mock_expectmore):
		"""Confirm that strings starting with '%' are treated as errors."""
		test_response = ['foobar%%%%%%', 'f%o%b%a%r%', '%foobar%', '%errors!']
		test_switch = SwitchMellanoxM7800('fakeip')
		expected = sorted(['%foobar%', '%errors!'])
		assert(sorted(test_switch._get_errors(command_response = test_response)) == expected)

	def test__get_expected_errors_no_error_pattern_found(self, mock_expectmore):
		"""Confirm that a string is returned when no error patterns are found"""
		test_response = ['foobar%%%%%%', 'f%o%b%a%r%', 'foobar%', 'errors!']
		test_switch = SwitchMellanoxM7800('fakeip')
		errors = test_switch._get_expected_errors(command_response = test_response)
		assert(isinstance(errors, str))
		assert(errors)

	RelevantResponsesTestData = namedtuple('RelevantResponsesTestData', ['start', 'end', 'test_response', 'expected_output'])

	@pytest.mark.parametrize(
		'test_driver',
		[
			RelevantResponsesTestData('start', 'end', ['start', 'boo', 'bar', 'end'], ['boo', 'bar']),
			# empty list should be found when there's no content inbetween
			RelevantResponsesTestData('start', 'end', ['start', 'end'], []),
			# fuzzy matching should be supported
			RelevantResponsesTestData('start', 'end', ['irrelevant start', 'boo', 'bar', 'irrelevant end'], ['boo', 'bar']),
			RelevantResponsesTestData('start', 'end', ['start irrelevant', 'boo', 'bar', 'end irrelevant'], ['boo', 'bar']),
			RelevantResponsesTestData('start', 'end', [' start ', 'boo', 'bar', ' end '], ['boo', 'bar']),
		]
	)
	def test__get_relevant_responses(self, mock_expectmore, test_driver):
		"""Test that only items between start_marker and end_marker are returned."""
		test_switch = SwitchMellanoxM7800('fakeip')
		result = test_switch._get_relevant_responses(
			command_response = test_driver.test_response,
			start_marker = test_driver.start,
			end_marker = test_driver.end,
		)
		assert(result == test_driver.expected_output)

	@pytest.mark.parametrize(
		'test_driver',
		[
			# out of order start and end
			RelevantResponsesTestData('start', 'end', ['end', 'boo', 'bar', 'start'], None),
			# missing start
			RelevantResponsesTestData('start', 'end', ['boo', 'bar', 'end',], None),
			# missing end
			RelevantResponsesTestData('start', 'end', ['start', 'boo', 'bar',], None),
			# missing both start and end
			RelevantResponsesTestData('start', 'end', ['boo', 'bar',], None),
		]
	)
	def test__get_relevant_responses_errors(self, mock_expectmore, test_driver):
		"""Test that SwitchException is raised on parsing errors."""
		test_switch = SwitchMellanoxM7800('fakeip')
		with pytest.raises(SwitchException):
			test_switch._get_relevant_responses(
				command_response = test_driver.test_response,
				start_marker = test_driver.start,
				end_marker = test_driver.end,
			)

	def test__get_installed_images(self, mock_expectmore):
		"""Test that images are found when present."""
		with open('/export/test-files/switch/m7800_show_images_console.txt') as test_file:
			test_console_response = test_file.read().splitlines()

		expected_data = {
			1: 'X86_64 3.6.4006 2017-07-03 16:17:39 x86_64',
			2: 'X86_64 3.6.4006 2017-07-03 16:17:39 x86_64',
		}
		test_switch = SwitchMellanoxM7800('fakeip')
		assert(test_switch._get_installed_images(command_response = test_console_response) == expected_data)

	@pytest.mark.parametrize(
		'test_response',
		[
			# multiple installed image block start markers
			['Installed images', 'Installed images', 'Partition 1:', 'test1.img', 'Partition 2:', 'test2.img', 'Last boot partition',],
			# no installed image block start markers
			['Partition 1:', 'test1.img', 'Partition 2:', 'test2.img', 'Last boot partition',],
			# multiple installed image block end markers
			['Installed images', 'Partition 1:', 'test1.img', 'Partition 2:', 'test2.img', 'Last boot partition', 'Last boot partition',],
			# no installed image block end markers
			['Installed images', 'Partition 1:', 'test1.img', 'Partition 2:', 'test2.img',],
			# reversed image block start and end markers
			['Last boot partition', 'Partition 1:', 'test1.img', 'Partition 2:', 'test2.img', 'Installed images',],
			# no installed images
			['Installed images', 'Last boot partition',],
			# no image listed for the first partition
			['Installed images', 'Partition 1:', 'Partition 2:', 'test2.img', 'Last boot partition',],
			# no image listed for the first partition
			['Installed images', 'Partition 1:', 'test1.img', 'Partition 2:', 'Last boot partition',],
		]
	)
	def test__get_installed_images_errors(self, mock_expectmore, test_response):
		"""Test that a SwitchException is raised when invalid responses are parsed."""
		test_switch = SwitchMellanoxM7800('fakeip')
		with pytest.raises(SwitchException):
			test_switch._get_installed_images(command_response = test_response)

	def test__get_boot_partitions(self, mock_expectmore):
		"""Test that partitions are found when present."""
		with open('/export/test-files/switch/m7800_show_images_console.txt') as test_file:
			test_console_response = test_file.read().splitlines()

		expected_data = (2, 1)
		test_switch = SwitchMellanoxM7800('fakeip')
		assert(test_switch._get_boot_partitions(command_response = test_console_response) == expected_data)

	@pytest.mark.parametrize(
		'test_response',
		[
			# multiple last boot partitions
			['Last boot partition: 1', 'Last boot partition: 1', 'Next boot partition: 2',],
			# no last boot partition
			['Next boot partition: 2',],
			# multiple next boot partitions
			['Last boot partition: 1', 'Next boot partition: 2', 'Next boot partition: 2',],
			# no next boot partitions
			['Last boot partition: 1',],
			# no boot partitions
			['foobaz', 'bleebblargb',],
		]
	)
	def test__get_boot_partitions_errors(self, mock_expectmore, test_response):
		"""Test that a SwitchException is raised when invalid responses are parsed."""
		test_switch = SwitchMellanoxM7800('fakeip')
		with pytest.raises(SwitchException):
			test_switch._get_boot_partitions(command_response = test_response)

	def test__get_boot_partitions_out_of_order(self, mock_expectmore):
		"""Test that partitions numbers are returned in the correct order (last, next)."""
		test_console_response = ['Next boot partition: 2', 'Last boot partition: 1',]

		expected_data = (1, 2)
		test_switch = SwitchMellanoxM7800('fakeip')
		assert(test_switch._get_boot_partitions(command_response = test_console_response) == expected_data)

	def test__get_available_images(self, mock_expectmore):
		"""Test that the available images are found when present."""
		with open('/export/test-files/switch/m7800_show_images_console.txt') as test_file:
			test_console_response = test_file.read().splitlines()

		expected_data = [
			('image-X86_64-3.6.2002.img', 'X86_64 3.6.2002 2016-09-28 21:00:15 x86_64'),
			('image-X86_64-3.6.3004.img', 'X86_64 3.6.3004 2017-02-05 17:31:53 x86_64'),
			('image-X86_64-3.6.4006.img', 'X86_64 3.6.4006 2017-07-03 16:17:39 x86_64'),
			('image-X86_64-3.6.5009.img', 'X86_64 3.6.5009 2018-01-02 07:42:21 x86_64'),
			('image-X86_64-3.6.8010.img', 'X86_64 3.6.8010 2018-08-20 18:04:19 x86_64'),
		]
		test_switch = SwitchMellanoxM7800('fakeip')
		assert(test_switch._get_available_images(command_response = test_console_response) == expected_data)

	def test__get_available_images_no_images(self, mock_expectmore):
		"""Test that an empty list is returned when no images are available."""
		test_console_response = ['No image files are available to be installed.', 'Serve image files via HTTP/HTTPS: no']
		test_switch = SwitchMellanoxM7800('fakeip')
		assert(test_switch._get_available_images(command_response = test_console_response) == [])

	@pytest.mark.parametrize(
		'test_response',
		[
			# multiple available image block start markers
			['Images available to be installed:', 'Images available to be installed:', 'image-X86_64-3.6.2002.img', 'X86_64 3.6.2002 2016-09-28 21:00:15 x86_64', 'Serve image files via HTTP/HTTPS: no',],
			# no installed image block start markers
			['image-X86_64-3.6.2002.img', 'X86_64 3.6.2002 2016-09-28 21:00:15 x86_64', 'Serve image files via HTTP/HTTPS: no',],
			# multiple installed image block end markers
			['Images available to be installed:', 'image-X86_64-3.6.2002.img', 'X86_64 3.6.2002 2016-09-28 21:00:15 x86_64', 'Serve image files via HTTP/HTTPS: no', 'Serve image files via HTTP/HTTPS: no',],
			# no installed image block end markers
			['Images available to be installed:', 'image-X86_64-3.6.2002.img', 'X86_64 3.6.2002 2016-09-28 21:00:15 x86_64',],
			# reversed image block start and end markers
			['Serve image files via HTTP/HTTPS: no', 'image-X86_64-3.6.2002.img', 'X86_64 3.6.2002 2016-09-28 21:00:15 x86_64', 'Images available to be installed:',],
			# no image version listed
			['Images available to be installed:', 'image-X86_64-3.6.2002.img', 'Serve image files via HTTP/HTTPS: no',],
		]
	)
	def test__get_available_images_errors(self, mock_expectmore, test_response):
		"""Test that an empty list is returned when no images are available."""
		test_console_response = test_response
		test_switch = SwitchMellanoxM7800('fakeip')
		with pytest.raises(SwitchException):
			test_switch._get_available_images(command_response = test_console_response)
