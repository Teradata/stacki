from unittest.mock import patch, create_autospec, MagicMock, PropertyMock, call
import pytest
import itertools
from collections import namedtuple
from pathlib import Path
from stack.expectmore import ExpectMore, ExpectMoreException
from stack.switch import SwitchException, Switch
from stack.switch.x1052 import SwitchDellX1052, _requires_regular_console, _requires_configure_console

def powerset(iterable):
	"""powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)

	Blatantly stolen from itertools recipes.
	"""
	combinations_list = list(iterable)
	return itertools.chain.from_iterable(
		itertools.combinations(combinations_list, item) for item in range(len(combinations_list)+1)
	)


Input = namedtuple("TestInput", ("input", "result"))

class Testx1052Decorators:
	"""A test case to hold all tests for the x1052 decorator functions."""
	@pytest.fixture
	def decorator_test_setup(self):
		"""A factory method to return the mocks required for testing the decorator functions."""
		def _setup(**match_index_kwargs):
			"""Set up and return all the mock objects needed for testing the decorators."""
			# Create mocks to test the decorator with
			mock_method_standin = MagicMock()
			# Pass a mocked instance of SwitchDellX1052 as "self"
			mock_self = create_autospec(
				spec = SwitchDellX1052,
				instance = True,
			)
			mock_self.CONSOLE_PROMPT = SwitchDellX1052.CONSOLE_PROMPT
			mock_self.CONFIGURE_CONSOLE_PROMPT = SwitchDellX1052.CONFIGURE_CONSOLE_PROMPT
			mock_self.CONSOLE_PROMPTS = SwitchDellX1052.CONSOLE_PROMPTS
			# Add required attributes and return values to the mock_self instance
			mock_self.proc = create_autospec(
				spec = ExpectMore,
				instance = True,
			)
			# Set up match_index based on passed in kwargs.
			type(mock_self.proc).match_index = PropertyMock(**match_index_kwargs)
			# Make sure to set the switch name in case an exception is attempted to be raised
			mock_self.switchname = "Test switch"

			return (mock_method_standin, mock_self)

		return _setup

	def test__requires_regular_console(self, decorator_test_setup):
		"""Test that the requires regular console decorator works as expected in the normal case."""
		# Create mocks to test the decorator with.
		# Set up match_index to first return that we are in the configure console, and then return that we
		# are in the regular console.
		mock_method_standin, mock_self = decorator_test_setup(
			side_effect = (
				SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONFIGURE_CONSOLE_PROMPT),
				SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT),
			)
		)

		@_requires_regular_console
		def mock_method_to_decorate(self, *args, **kwargs):
			mock_method_standin(self, *args, **kwargs)

		# call the mock decorated method
		mock_method_to_decorate(mock_self, "foo", bar = "bar")

		# Expect it to quit out of any paged prompts
		mock_self.proc.say.assert_any_call(cmd = "q")
		# Expect it to exit to the regular console
		mock_self.proc.say.assert_any_call(cmd = "exit")
		# Expect the mocked method to be called with the arguments
		mock_method_standin.assert_called_once_with(mock_self, "foo", bar = "bar")

	def test__requires_regular_console_at_correct_prompt(self, decorator_test_setup):
		"""Test that the requires regular console decorator works as expected in the case where we are already at the right console."""
		# Create mocks to test the decorator with.
		# Set up match_index to return that we are in the regular console.
		mock_method_standin, mock_self = decorator_test_setup(
			return_value = SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT),
		)

		@_requires_regular_console
		def mock_method_to_decorate(self, *args, **kwargs):
			mock_method_standin(self, *args, **kwargs)

		# call the mock decorated method
		mock_method_to_decorate(mock_self, "foo", bar = "bar")

		# Expect it to quit out of any paged prompts and to not exit to the regular console
		mock_self.proc.say.assert_called_once_with(cmd = "q")
		# Expect the mocked method to be called with the arguments
		mock_method_standin.assert_called_once_with(mock_self, "foo", bar = "bar")

	def test__requires_regular_console_fails_to_get_to_correct_prompt(self, decorator_test_setup):
		"""Test that the requires regular console decorator fails in the case where we can't get to right console."""
		# Create mocks to test the decorator with.
		# Set up match_index to return that we are in the configure console always.
		mock_method_standin, mock_self = decorator_test_setup(
			return_value = SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONFIGURE_CONSOLE_PROMPT),
		)

		@_requires_regular_console
		def mock_method_to_decorate(self, *args, **kwargs):
			mock_method_standin(self, *args, **kwargs)

		# call the mock decorated method
		with pytest.raises(SwitchException):
			mock_method_to_decorate(mock_self, "foo", bar = "bar")

	def test__requires_configure_console(self, decorator_test_setup):
		"""Test that the requires configure console decorator works as expected in the normal case."""
		# Create mocks to test the decorator with.
		# Set up match_index to first return that we are in the regular console, and then return that we
		# are in the configure console.
		mock_method_standin, mock_self = decorator_test_setup(
			side_effect = (
				SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT),
				SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONFIGURE_CONSOLE_PROMPT),
			)
		)

		@_requires_configure_console
		def mock_method_to_decorate(self, *args, **kwargs):
			mock_method_standin(self, *args, **kwargs)

		# call the mock decorated method
		mock_method_to_decorate(mock_self, "foo", bar = "bar")

		# Expect it to quit out of any paged prompts
		mock_self.proc.say.assert_any_call(cmd = "q")
		# Expect it to enter the configure console
		mock_self.proc.say.assert_any_call(cmd = "configure")
		# Expect the mocked method to be called with the arguments
		mock_method_standin.assert_called_once_with(mock_self, "foo", bar = "bar")

	def test__requires_configure_console_at_correct_prompt(self, decorator_test_setup):
		"""Test that the requires configure console decorator works as expected in the case where we are already at the right console."""
		# Create mocks to test the decorator with.
		# Set up match_index to return that we are in the configure console.
		mock_method_standin, mock_self = decorator_test_setup(
			return_value = SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONFIGURE_CONSOLE_PROMPT),
		)

		@_requires_configure_console
		def mock_method_to_decorate(self, *args, **kwargs):
			mock_method_standin(self, *args, **kwargs)

		# call the mock decorated method
		mock_method_to_decorate(mock_self, "foo", bar = "bar")

		# Expect it to quit out of any paged prompts and to not exit to the regular console
		mock_self.proc.say.assert_called_once_with(cmd = "q")
		# Expect the mocked method to be called with the arguments
		mock_method_standin.assert_called_once_with(mock_self, "foo", bar = "bar")

	def test__requires_configure_console_fails_to_get_to_correct_prompt(self, decorator_test_setup):
		"""Test that the requires configure console decorator fails in the case where we can't get to right console."""
		# Create mocks to test the decorator with.
		# Set up match_index to return that we are in the regular console always.
		mock_method_standin, mock_self = decorator_test_setup(
			return_value = SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT),
		)

		@_requires_configure_console
		def mock_method_to_decorate(self, *args, **kwargs):
			mock_method_standin(self, *args, **kwargs)

		# call the mock decorated method
		with pytest.raises(SwitchException):
			mock_method_to_decorate(mock_self, "foo", bar = "bar")

class TestSwitchDellX1052:
	"""A test case to hold all tests for the x1052 switch class."""
	class SwitchDellX1052UnderTest(SwitchDellX1052):
		"""Derived class to test SwitchDellX1052 that sets up required mocks in __init__."""
		def __init__(self, match_index_kwargs = {}, after_kwargs = {}):
			self.proc = create_autospec(spec = ExpectMore, instance = True)
			# Set up match_index based on passed in kwargs.
			type(self.proc).match_index = PropertyMock(**match_index_kwargs)
			# Set up after based on passed in kwargs.
			type(self.proc).after = PropertyMock(**after_kwargs)
			# set up required attributes
			self.switchname = "Test switch"
			self.username = "test_user"
			self.password = "test_password"
			self.switch_ip_address = "10.25.250.1"
			self.current_config = "current_config"
			self.new_config = "new_config"
			self.tftpdir = "/some_dir/some_other_dir/"
			self.stacki_server_ip = "10.25.250.2"

	@patch(target = "stack.switch.x1052.ExpectMore", autospec = True)
	@patch.object(target = Switch, attribute = "__init__")
	def test__init__(self, mock_super__init__, mock_expectmore):
		"""Test that __init__ performs the expected initialization."""
		# Instantiate the switch
		test_switch = SwitchDellX1052("foo", bar = "bar")

		# Expect the args and kwargs to be passed through to the superclass __init__
		mock_super__init__.assert_called_once_with("foo", bar = "bar")
		# Expect the ExpectMore instance to be instantiated.
		mock_expectmore.assert_called_once_with(prompts = SwitchDellX1052.CONSOLE_PROMPTS)
		# Expect the ExpectMore instance to be set
		assert hasattr(test_switch, "proc")

	def test_supported(self):
		"""Test that supported() returns the expected values."""
		test_switch = self.SwitchDellX1052UnderTest()

		assert [('Dell', 'x1052'),] == test_switch.supported()

	def test_connect(self):
		"""Test that connect works as expected in the normal case."""
		# Set isalive() to return False
		test_switch = self.SwitchDellX1052UnderTest()
		test_switch.proc.isalive.return_value = False

		# Call the function
		test_switch.connect()

		# Expect that the connection was checked if it was already alive.
		test_switch.proc.isalive.assert_called_once_with()
		# Expect that the process was started.
		test_switch.proc.start.assert_called_once_with(
			cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -tt {test_switch.switch_ip_address}"
		)
		# Expect that the switch tries to login and get to the prompt.
		test_switch.proc.conversation.assert_called_once_with(
			response_pairs = [
				("User Name:", test_switch.username),
				("Password:", test_switch.password),
				(test_switch.CONSOLE_PROMPTS, None),
			]
		)

	def test_connect_already_connected(self):
		"""Test that connect early exits in the case where we are already connected to the switch."""
		# Set isalive() to return True
		test_switch = self.SwitchDellX1052UnderTest()
		test_switch.proc.isalive.return_value = True

		# Call the function
		test_switch.connect()

		# Expect that the connection was checked if it was already alive.
		test_switch.proc.isalive.assert_called_once_with()
		# Expect that the process was not started.
		test_switch.proc.start.assert_not_called()
		# Expect that the switch does not try to login.
		test_switch.proc.conversation.assert_not_called()

	def test_connect_failure_to_start(self):
		"""Test that when start fails, that a SwitchException is raised."""
		# Set isalive() to return False
		test_switch = self.SwitchDellX1052UnderTest()
		test_switch.proc.isalive.return_value = False
		# Make start fail.
		test_switch.proc.start.side_effect = ExpectMoreException("Test exception")

		# Call the function
		with pytest.raises(SwitchException):
			test_switch.connect()

	def test_connect_failure_to_converse(self):
		"""Test that when conversation fails, that a SwitchException is raised."""
		# Set isalive() to return False
		test_switch = self.SwitchDellX1052UnderTest()
		test_switch.proc.isalive.return_value = False
		# Make connect fail.
		test_switch.proc.conversation.side_effect = ExpectMoreException("Test exception")

		# Call the function
		with pytest.raises(SwitchException):
			test_switch.connect()

	def test_disconnect(self):
		"""Test that disconnect works as expected in the normal case."""
		# Set isalive() to return True and the prompt to be the correct one.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)
		test_switch.proc.isalive.return_value = True

		# Call the function
		test_switch.disconnect()

		# Expect end to be called
		test_switch.proc.end.assert_called_once_with(quit_cmd = "exit")

	def test_disconnect_already_disconnected(self):
		"""Test that disconnect early exits in the case where the process has already ended."""
		# Set isalive() to return False and the prompt to be the correct one.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)
		test_switch.proc.isalive.return_value = False

		# Call the function
		test_switch.disconnect()

		# Expect end to not be called
		test_switch.proc.end.assert_not_called()

	@patch.object(target = SwitchDellX1052, attribute = "_read_paged_output")
	def test_get_mac_address_table(self, mock__read_paged_output):
		"""Test that get_mac_address_table works as expected in the normal case."""
		# Set the prompt to be the correct one.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)
		# Switch data to mock MAC address table
		mock__read_paged_output.return_value = """
			show mac address-table
				show mac address-table
			Flags: I - Internal usage VLAN
			Aging time is 300 sec

				Vlan          Mac Address         Port       Type
			------------ --------------------- ---------- ----------
				1         00:00:00:00:00:00    gi1/0/10   dynamic
				1         f4:8e:38:44:10:15       0         self

			console#:
		""".splitlines()

		# Call the function
		results = test_switch.get_mac_address_table()

		# Expect it to try to read paged output
		mock__read_paged_output.assert_called_once_with(cmd = "show mac address-table")
		# Expect the results to be parsed correctly.
		assert [["1", "00:00:00:00:00:00", "10", "dynamic"]] == results

	@patch.object(target = SwitchDellX1052, attribute = "_read_paged_output")
	def test_get_interface_status_table(self, mock__read_paged_output):
		"""Test that get_interface_status_table works as expected in the normal case."""
		# Set the prompt to be the correct one.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)
		# Switch data to mock status table
		mock__read_paged_output.return_value = """
														 Flow Link          Back   Mdix
			Port     Type         Duplex  Speed Neg      ctrl State       Pressure Mode
			-------- ------------ ------  ----- -------- ---- ----------- -------- -------
			gi1/0/1  1G-Copper      --      --     --     --  Down           --     --
			gi1/0/2  1G-Copper    Full    1000  Enabled  Off  Up          Disabled Off
			gi1/0/3  1G-Copper    Full    1000  Enabled  Off  Up          Disabled On
			te1/0/1  10G-Fiber      --      --     --     --  Down           --     --

			console#:
		""".splitlines()

		# Call the function
		results = test_switch.get_interface_status_table()

		# Expect it to try to read paged output
		mock__read_paged_output.assert_called_once_with(cmd = "show interfaces status")
		# Expect the results to be parsed correctly.
		assert [
			["1", "1G-Copper", "--", "--", "--", "--", "Down", "--", "--",],
			["2", "1G-Copper", "Full", "1000", "Enabled", "Off", "Up", "Disabled", "Off",],
			["3", "1G-Copper", "Full", "1000", "Enabled", "Off", "Up", "Disabled", "On",],
		] == results

	@patch(target = "stack.switch.x1052.Timer", autospec = True)
	def test__read_paged_output(self, mock_timer):
		"""Test that read paged output works as expected in the normal case."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.PAGING_PROMPT]
		# Set the match_index up so that the first is the paging prompt, and the second is the regular prompt.
		# Also set the after property to return a value.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"side_effect": (
					expected_prompts.index(SwitchDellX1052.PAGING_PROMPT),
					expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT),
				),
			},
			after_kwargs = {
				"return_value": ["More: <return>foo"]
			}
		)
		# Set ask to return an empty list.
		test_switch.proc.ask.return_value = []
		# Make sure timer.is_alive returns True.
		mock_timer.return_value.is_alive.return_value = True

		results = test_switch._read_paged_output(cmd = "bar")

		# Expect ask to be called with the command.
		test_switch.proc.ask.assert_any_call(cmd = "bar", prompt = expected_prompts)
		# Expect ask to be used to page through the output.
		test_switch.proc.ask.assert_any_call(cmd = "\x20", prompt = expected_prompts)
		# Expect the timer to be started
		mock_timer.return_value.start.assert_called_once_with()
		# Expect it to be checked for still being alive.
		mock_timer.return_value.is_alive.assert_any_call()
		# Expect it to be cancelled on success.
		mock_timer.return_value.cancel.assert_called_once_with()
		# Expect the result to have any paging menu prompts captured in the results removed.
		assert ["foo", "foo"] == results

	@patch(target = "stack.switch.x1052.Timer", autospec = True)
	def test__read_paged_output_results_in_before(self, mock_timer):
		"""Test that read paged output works as expected in the case where the results are returned directly from ask."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.PAGING_PROMPT]
		# Set the match_index up so that the first is the paging prompt, and the second is the regular prompt.
		# Also set the after property to return a value.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"side_effect": (
					expected_prompts.index(SwitchDellX1052.PAGING_PROMPT),
					expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT),
				),
			},
		)
		# Set ask to return the results.
		test_switch.proc.ask.return_value = ["More: <return>foo"]
		# Make sure timer.is_alive returns True.
		mock_timer.return_value.is_alive.return_value = True

		results = test_switch._read_paged_output(cmd = "bar")

		# Expect ask to be called with the command.
		test_switch.proc.ask.assert_any_call(cmd = "bar", prompt = expected_prompts)
		# Expect ask to be used to page through the output.
		test_switch.proc.ask.assert_any_call(cmd = "\x20", prompt = expected_prompts)
		# Expect the timer to be started
		mock_timer.return_value.start.assert_called_once_with()
		# Expect it to be checked for still being alive.
		mock_timer.return_value.is_alive.assert_any_call()
		# Expect it to be cancelled on success.
		mock_timer.return_value.cancel.assert_called_once_with()
		# Expect the result to have any paging menu prompts captured in the results removed.
		assert ["foo", "foo"] == results

	@patch(target = "stack.switch.x1052.Timer", autospec = True)
	def test__read_paged_output_no_paging(self, mock_timer):
		"""Test that read paged output works as expected in the case where there is no paging."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.PAGING_PROMPT]
		# Set the match_index up so that the first is the paging prompt, and the second is the regular prompt.
		# Also set the after property to return a value.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)
		# Set ask to return the results.
		test_switch.proc.ask.return_value = ["foo"]
		# Make sure timer.is_alive returns True.
		mock_timer.return_value.is_alive.return_value = True

		results = test_switch._read_paged_output(cmd = "bar")

		# Expect ask to be called with the command and to not be used to page through the output.
		test_switch.proc.ask.assert_called_once_with(cmd = "bar", prompt = expected_prompts)
		# Expect the result to have any paging menu prompts captured in the results removed.
		assert ["foo"] == results

	@patch(target = "stack.switch.x1052.Timer", autospec = True)
	def test__read_paged_output_timeout(self, mock_timer):
		"""Test that read paged output times out when the timer ends."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.PAGING_PROMPT]
		# Set the match_index up so that it returns the paging prompt.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": expected_prompts.index(SwitchDellX1052.PAGING_PROMPT),
			},
		)
		# Set ask to return the results.
		test_switch.proc.ask.return_value = ["More: <return>foo"]
		# Make sure timer.is_alive returns False.
		mock_timer.return_value.is_alive.return_value = False

		with pytest.raises(SwitchException):
			test_switch._read_paged_output(cmd = "bar")

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	@patch(target = "stack.switch.x1052.Path", autospec = True)
	def test_download(self, mock_path, mock__check_success):
		"""Test that download works as expected in the normal case."""
		# Make sure we are at the correct prompt
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)
		# Make sure we return something from ask
		test_switch.proc.ask.return_value = [SwitchDellX1052.COPY_SUCCESS]
		# Make sure _check_success returns True
		mock__check_success.return_value = True

		# Call the function
		test_switch.download()

		# Expect the tftp directory to be resolved and strictly checked for existence.
		mock_path.assert_called_once_with(test_switch.tftpdir)
		mock_path.return_value.resolve.assert_called_once_with(strict = True)
		# Expect the tftp directory to be concatenated with the file name. This ends up being the __truediv__ method.
		mock_path.return_value.resolve.return_value.__truediv__.assert_called_once_with(test_switch.current_config)
		# Expect the file to be touched with exist_ok True so the file already existing is not a problem.
		mock_path.return_value.resolve.return_value.__truediv__.return_value.touch.assert_called_once_with(exist_ok = True)
		# Expect the file to be made accessible by anyone so TFTP can get it.
		mock_path.return_value.resolve.return_value.__truediv__.return_value.chmod.assert_called_once_with(mode = 0o777)
		# Expect the file to be TFTPed to the switch
		test_switch.proc.ask.assert_called_once_with(
			cmd = f"copy running-config tftp://{test_switch.stacki_server_ip}/{test_switch.current_config}",
		)
		# Expect the results to be checked.
		mock__check_success.assert_called_once_with(
			test_switch,
			results = test_switch.proc.ask.return_value,
			success_string = SwitchDellX1052.COPY_SUCCESS,
		)

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	@patch(target = "stack.switch.x1052.Path", autospec = True)
	def test_download_fails(self, mock_path, mock__check_success):
		"""Test that download fails when _check_success returns false."""
		# Make sure we are at the correct prompt
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)
		# Make sure _check_success returns False
		mock__check_success.return_value = False

		# Call the function
		with pytest.raises(SwitchException):
			test_switch.download()

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	def test_upload(self, mock__check_success):
		"""Test that upload works as expected in the normal case."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.OVERWRITE_PROMPT]
		# Make sure we start at the correct prompt and then are prompted to overwrite twice.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"side_effect": (
					expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT),
					expected_prompts.index(SwitchDellX1052.OVERWRITE_PROMPT),
					expected_prompts.index(SwitchDellX1052.OVERWRITE_PROMPT),
				),
			},
		)
		# Make sure we return something from ask. We want it to be different each time so we
		# can check the _check_success calls.
		test_switch.proc.ask.side_effect = (
			["tftp upload"],
			["tftp confirm"],
			["switch local copy"],
			["switch local copy confirm"],
		)
		# Make sure _check_success returns True
		mock__check_success.return_value = True

		# Call the function
		test_switch.upload()

		# Expect the file to be uploaded, the overwite prompt to be accepted, the file to be copied locally, and the second overwrite prompt to be accepted.
		assert test_switch.proc.ask.call_args_list == [
			call(cmd = f"copy tftp://{test_switch.stacki_server_ip}/{test_switch.new_config} temp", prompt = expected_prompts),
			call(cmd = "Y", prompt = SwitchDellX1052.CONSOLE_PROMPTS),
			call(cmd = "copy temp running-config", prompt = expected_prompts, timeout = 30),
			call(cmd = "Y", prompt = SwitchDellX1052.CONSOLE_PROMPTS, timeout = 30),
		]
		# Expect that _check_success was called on the results
		assert mock__check_success.call_args_list == [
			call(test_switch, results = ["tftp confirm"], success_string = SwitchDellX1052.COPY_SUCCESS),
			call(test_switch, results = ["switch local copy confirm"], success_string = SwitchDellX1052.COPY_SUCCESS),
		]

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	def test_upload_no_overwrite_prompts(self, mock__check_success):
		"""Test that upload works as expected in the case where there are no overwrite prompts."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.OVERWRITE_PROMPT]
		# Make sure we always return the console prompt
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)
		# Make sure we return something from ask. We want it to be different each time so we
		# can check the _check_success calls.
		test_switch.proc.ask.side_effect = (
			["tftp upload"],
			["switch local copy"],
		)
		# Make sure _check_success returns True
		mock__check_success.return_value = True

		# Call the function
		test_switch.upload()

		# Expect the file to be uploaded, the overwite prompt to be accepted, the file to be copied locally, and the second overwrite prompt to be accepted.
		assert test_switch.proc.ask.call_args_list == [
			call(cmd = f"copy tftp://{test_switch.stacki_server_ip}/{test_switch.new_config} temp", prompt = expected_prompts),
			call(cmd = "copy temp running-config", prompt = expected_prompts, timeout = 30),
		]
		# Expect that _check_success was called on the results
		assert mock__check_success.call_args_list == [
			call(test_switch, results = ["tftp upload"], success_string = SwitchDellX1052.COPY_SUCCESS),
			call(test_switch, results = ["switch local copy"], success_string = SwitchDellX1052.COPY_SUCCESS),
		]

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	def test_upload_fails(self, mock__check_success):
		"""Test that upload fails when _check_success returns failure on the first check."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.OVERWRITE_PROMPT]
		# Make sure we always return the console prompt
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)
		# Make sure _check_success returns False
		mock__check_success.return_value = False

		# Call the function
		with pytest.raises(SwitchException):
			test_switch.upload()

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	def test_upload_local_copy_fails(self, mock__check_success):
		"""Test that upload fails when _check_success returns failure on the second check."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.OVERWRITE_PROMPT]
		# Make sure we always return the console prompt
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)
		# Make sure _check_success returns True for the first call and False for the second.
		mock__check_success.side_effect = (True, False)

		# Call the function
		with pytest.raises(SwitchException):
			test_switch.upload()

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	def test_apply_configuration(self, mock__check_success):
		"""Test that apply configuration works as expected in the normal case."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.OVERWRITE_PROMPT]
		# Make sure we start at the correct prompt and then are prompted to overwrite once.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"side_effect": (
					expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT),
					expected_prompts.index(SwitchDellX1052.OVERWRITE_PROMPT),
				),
			},
		)
		# Make sure we return something from ask. We want it to be different each time so we
		# can check the _check_success calls.
		test_switch.proc.ask.side_effect = (["apply"], ["apply confirm"])
		# Make sure _check_success returns True
		mock__check_success.return_value = True

		# Call the function
		test_switch.apply_configuration()

		# Expect the file to be applied and the overwite prompt to be accepted.
		assert test_switch.proc.ask.call_args_list == [
			call(cmd = "write", prompt = expected_prompts),
			call(cmd = "Y", prompt = SwitchDellX1052.CONSOLE_PROMPTS),
		]
		# Expect success to be checked
		mock__check_success.assert_called_once_with(
			test_switch,
			results = ["apply confirm"],
			success_string = SwitchDellX1052.COPY_SUCCESS
		)

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	def test_apply_configuration_no_overwrite_prompt(self, mock__check_success):
		"""Test that apply configuration works as expected in the case where there is no overwrite prompt."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.OVERWRITE_PROMPT]
		# Make sure we always return the correct prompt.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT)
			},
		)
		# Make sure we return something from ask.
		test_switch.proc.ask.return_value = ["apply"]
		# Make sure _check_success returns True
		mock__check_success.return_value = True

		# Call the function
		test_switch.apply_configuration()

		# Expect the file to be applied and the overwite prompt to be accepted.
		test_switch.proc.ask.assert_called_once_with(cmd = "write", prompt = expected_prompts)
		# Expect success to be checked
		mock__check_success.assert_called_once_with(
			test_switch,
			results = ["apply"],
			success_string = SwitchDellX1052.COPY_SUCCESS
		)

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	def test_apply_configuration_fails(self, mock__check_success):
		"""Test that apply configuration fails when _check_success returns false."""
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.OVERWRITE_PROMPT]
		# Make sure we always return the correct prompt.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT)
			},
		)
		# Make sure _check_success returns False
		mock__check_success.return_value = False

		# Call the function
		with pytest.raises(SwitchException):
			test_switch.apply_configuration()

	def test_set_tftp_ip(self):
		"""Assert that set tftp ip sets the IP to the value we provide."""
		test_switch = self.SwitchDellX1052UnderTest()
		test_ip = "10.25.250.3"
		test_switch.set_tftp_ip(ip = test_ip)

		# Expect the attribute to be added
		assert hasattr(test_switch, "stacki_server_ip")
		# Expect the value to match what we set
		assert test_ip == test_switch.stacki_server_ip

	def test__check_success(self):
		"""Check that _check_success returns True when the success string is found in the results."""
		mock_success_string = "bar"
		mock_results = ["foozgooz", f"booz{mock_success_string}", "bazbean"]

		test_switch = self.SwitchDellX1052UnderTest()
		assert test_switch._check_success(results = mock_results, success_string = mock_success_string)

	def test__check_success_not_found(self):
		"""Check that _check_success returns False when the success string is not found in the results."""
		mock_success_string = "bag"
		mock_results = ["foozgooz", f"boozbar", "bazbean"]

		test_switch = self.SwitchDellX1052UnderTest()
		assert not test_switch._check_success(results = mock_results, success_string = mock_success_string)

	@pytest.mark.parametrize(
		"test_inputs",
		# Generate every combination of software + boot + hardware result to test against.
		powerset(
			{
				"software": Input(
					input = "SW version    3.0.0.94 ( date  10-Sep-2017 time  22:31:38 )",
					result = ["3.0.0.94 ( date  10-Sep-2017 time  22:31:38 )"]
				),
				"boot": Input(
					input = "Boot version    1.0.0.25 ( date  05-Apr-2017 time  09:55:19 )",
					result = ["1.0.0.25 ( date  05-Apr-2017 time  09:55:19 )"]
				),
				"hardware": Input(
					input = "HW version    00.00.04",
					result = ["00.00.04"]
				),
			}.items()
		)
	)
	def test__parse_versions(self, test_inputs):
		"""Check that parse versions works as expected in all cases."""
		test_inputs = {key: value for key, value in test_inputs}
		mock_results = [value.input for value in test_inputs.values()]
		expected_software = test_inputs.get("software", [])
		if expected_software:
			expected_software = expected_software.result

		expected_boot = test_inputs.get("boot", [])
		if expected_boot:
			expected_boot = expected_boot.result

		expected_hardware = test_inputs.get("hardware", [])
		if expected_hardware:
			expected_hardware = expected_hardware.result

		test_switch = self.SwitchDellX1052UnderTest()
		results = test_switch._parse_versions(results = mock_results)

		# Expect all of the returned versions to match the expected returned versions.
		assert expected_software == results.software
		assert expected_boot == results.boot
		assert expected_hardware == results.hardware

	def test__check_parsed_versions(self):
		"""Test that checking parsed versions doesn't raise an exception in the good case."""
		mock_parsed_versions = namedtuple("MockParsedVersions", ("software", "boot", "hardware"))(
			software = ["3.0.0.94 ( date  10-Sep-2017 time  22:31:38 )"],
			boot = ["1.0.0.25 ( date  05-Apr-2017 time  09:55:19 )"],
			hardware = ["00.00.04"],
		)

		test_switch = self.SwitchDellX1052UnderTest()
		test_switch._check_parsed_versions(parsed_versions = mock_parsed_versions)

	@pytest.mark.parametrize(
		"test_inputs",
		# Generate every combination of bad result to test against. The result will either be missing, or have duplicate entries.
		powerset(
			{
				"software": ["3.0.0.94 ( date  10-Sep-2017 time  22:31:38 )", "3.0.0.94 ( date  10-Sep-2017 time  22:31:38 )"],
				"boot": ["1.0.0.25 ( date  05-Apr-2017 time  09:55:19 )", "1.0.0.25 ( date  05-Apr-2017 time  09:55:19 )"],
				"hardware": ["00.00.04", "00.00.04"],
			}.items()
		)
	)
	def test__check_parsed_versions_errors(self, test_inputs):
		"""Test that checking parsed versions raises an exception in all error cases."""
		test_inputs = {key: value for key, value in test_inputs}
		mock_parsed_versions = namedtuple("MockParsedVersions", ("software", "boot", "hardware"))(
			software = test_inputs.get("software", []),
			boot = test_inputs.get("boot", []),
			hardware = test_inputs.get("hardware", []),
		)

		test_switch = self.SwitchDellX1052UnderTest()
		with pytest.raises(SwitchException):
			test_switch._check_parsed_versions(parsed_versions = mock_parsed_versions)

	@patch.object(target = SwitchDellX1052, attribute = "_check_parsed_versions", autospec = True)
	@patch.object(target = SwitchDellX1052, attribute = "_parse_versions", autospec = True)
	def test_get_versions(self, mock__parse_versions, mock__check_parsed_versions):
		"""Test that get versions works as expected in the good case."""
		# Make sure we always return the correct prompt.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT)
			},
		)
		mock__parse_versions.return_value = namedtuple("MockParsedVersions", ("software", "boot", "hardware"))(
			software = ["3.0.0.94 ( date  10-Sep-2017 time  22:31:38 )"],
			boot = ["1.0.0.25 ( date  05-Apr-2017 time  09:55:19 )"],
			hardware = ["00.00.04"],
		)
		# Set ask to return the mock results
		test_switch.proc.ask.return_value = [
			"SW version    3.0.0.94 ( date  10-Sep-2017 time  22:31:38 )",
			"Boot version    1.0.0.25 ( date  05-Apr-2017 time  09:55:19 )",
			"HW version    00.00.04",
		]

		results = test_switch.get_versions()

		# expect the results to match
		assert mock__parse_versions.return_value.software[0] == results.software
		assert mock__parse_versions.return_value.boot[0] == results.boot
		assert mock__parse_versions.return_value.hardware[0] == results.hardware
		# expect the parsed versions to be validated
		mock__check_parsed_versions.assert_called_once_with(test_switch, parsed_versions = mock__parse_versions.return_value)

	@patch.object(target = SwitchDellX1052, attribute = "_check_parsed_versions", autospec = True)
	@patch.object(target = SwitchDellX1052, attribute = "_parse_versions", autospec = True)
	def test_get_versions_errors(self, mock__parse_versions, mock__check_parsed_versions):
		"""Test that get versions fails if validating the parsed versions fails."""
		# Make sure we always return the correct prompt.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT)
			},
		)
		mock__parse_versions.return_value = namedtuple("MockParsedVersions", ("software", "boot", "hardware"))(
			software = ["3.0.0.94 ( date  10-Sep-2017 time  22:31:38 )"],
			boot = ["1.0.0.25 ( date  05-Apr-2017 time  09:55:19 )"],
			hardware = ["00.00.04"],
		)
		# Set ask to return the mock results
		test_switch.proc.ask.return_value = [
			"SW version    3.0.0.94 ( date  10-Sep-2017 time  22:31:38 )",
			"Boot version    1.0.0.25 ( date  05-Apr-2017 time  09:55:19 )",
			"HW version    00.00.04",
		]
		mock__check_parsed_versions.side_effect = SwitchException("Test error")

		with pytest.raises(SwitchException):
			test_switch.get_versions()

	@patch(target = "tempfile.NamedTemporaryFile", autospec = True)
	@patch(target = "stack.switch.x1052.Path", autospec = True)
	def test__upload_tftp(self, mock_path, mock_named_temporary_file):
		"""Test that upload tftp works as expected in the good case."""
		# Make sure we always return the correct prompt.
		test_switch = self.SwitchDellX1052UnderTest()
		# Set up the first, second, and third calls to Path() to return a different mock each time.
		source_file = create_autospec(spec = Path, spec_set = True, instance = True)
		tftp_dir = create_autospec(spec = Path, spec_set = True, instance = True)
		temp_file = create_autospec(spec = Path, spec_set = True, instance = True)
		mock_path.side_effect = (source_file, tftp_dir, temp_file)
		# Return a mock for the full TFTP directory
		full_tftp_dir = create_autospec(spec = Path, spec_set = True, instance = True)
		tftp_dir.__truediv__.return_value = full_tftp_dir
		mock_timeout = 60
		mock_source = "foo/bar"
		mock_destination = "baz"

		test_switch._upload_tftp(source = mock_source, destination = mock_destination, timeout = mock_timeout)

		# Should use the provided path for the source file
		mock_path.assert_any_call(mock_source)
		# Should use the resolved full TFTP directory to create the temporary file
		mock_named_temporary_file.assert_called_once_with(dir = full_tftp_dir.resolve.return_value)
		# The temporary file should have the resolved source file written to it and then be flushed
		mock_named_temporary_file.return_value.__enter__.return_value.write.assert_called_once_with(
			source_file.resolve.return_value.read_bytes.return_value
		)
		mock_named_temporary_file.return_value.__enter__.return_value.flush.assert_called_once_with()
		# The temporary file should have been chmoded using pathlib
		temp_file.chmod.assert_called_once_with(mode = 0o777)
		# The file should have been TFTPed to the switch
		test_switch.proc.ask.assert_called_once_with(
			cmd = f"copy tftp://{test_switch.stacki_server_ip}/{temp_file.parent.stem}/{temp_file.stem} {mock_destination}",
			timeout = mock_timeout,
		)

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	@patch.object(target = SwitchDellX1052, attribute = "_upload_tftp", autospec = True)
	def test_upload_software(self, mock__upload_tftp, mock__check_success):
		"""Test that upload software works as expected in the good case."""
		# Make sure we always return the correct prompt.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT)
			},
		)
		mock_software_file = "foo/bar"

		test_switch.upload_software(software_file = mock_software_file)

		# Should use the provided path for the software file, send it to the right destination, and set a long timeout
		mock__upload_tftp.assert_called_once_with(
			test_switch,
			source = mock_software_file,
			destination = "image",
			timeout = 600,
		)
		# The success should have been checked.
		mock__check_success.assert_called_once_with(
			test_switch,
			results = mock__upload_tftp.return_value,
			success_string = SwitchDellX1052.COPY_SUCCESS,
		)

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	@patch.object(target = SwitchDellX1052, attribute = "_upload_tftp", autospec = True)
	def test_upload_software_error(self, mock__upload_tftp, mock__check_success):
		"""Test that upload software fails if the success check fails."""
		# Make sure we always return the correct prompt.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT)
			},
		)
		# Make sure _check_success returns False
		mock__check_success.return_value = False

		with pytest.raises(SwitchException):
			test_switch.upload_software(software_file = "foo/bar")

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	@patch.object(target = SwitchDellX1052, attribute = "_upload_tftp", autospec = True)
	def test_upload_boot(self, mock__upload_tftp, mock__check_success):
		"""Test that upload boot works as expected in the good case."""
		# Make sure we always return the correct prompt.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT)
			},
		)
		mock_software_file = "foo/bar"

		test_switch.upload_boot(boot_file = mock_software_file)

		# Should use the provided path for the boot file, send it to the right destination, and set a long timeout
		mock__upload_tftp.assert_called_once_with(
			test_switch,
			source = mock_software_file,
			destination = "boot",
			timeout = 600,
		)
		# The success should have been checked.
		mock__check_success.assert_called_once_with(
			test_switch,
			results = mock__upload_tftp.return_value,
			success_string = SwitchDellX1052.COPY_SUCCESS,
		)

	@patch.object(target = SwitchDellX1052, attribute = "_check_success", autospec = True)
	@patch.object(target = SwitchDellX1052, attribute = "_upload_tftp", autospec = True)
	def test_upload_boot_error(self, mock__upload_tftp, mock__check_success):
		"""Test that upload boot fails if the success check fails."""
		# Make sure we always return the correct prompt.
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT)
			},
		)
		# Make sure _check_success returns False
		mock__check_success.return_value = False

		with pytest.raises(SwitchException):
			test_switch.upload_boot(boot_file = "foo/bar")

	def test_reload(self):
		"""Test that reload works in the good case."""
		# Make sure we first return the console prompt, then the continue prompt.
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.CONTINUE_PROMPT, SwitchDellX1052.SHUTDOWN_PROMPT]
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"side_effect": [
					expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT),
					expected_prompts.index(SwitchDellX1052.CONTINUE_PROMPT),
				]
			},
		)

		test_switch.reload()

		# Expect that reboot was asked for and confirmed
		test_switch.proc.say.assert_any_call(
			cmd = "reload",
			prompt = expected_prompts,
		)
		test_switch.proc.say.assert_any_call(
			cmd = "Y",
			prompt = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.SHUTDOWN_PROMPT],
		)
		# Expect that the process was terminated without any prompts or quit commands
		test_switch.proc.end.assert_called_once_with(quit_cmd = "", prompt = "")

	def test_reload_no_confirm_prompt(self):
		"""Test that reload works in the good case."""
		# Make sure we alway return the console prompt.
		expected_prompts = [*SwitchDellX1052.CONSOLE_PROMPTS, SwitchDellX1052.CONTINUE_PROMPT, SwitchDellX1052.SHUTDOWN_PROMPT]
		test_switch = self.SwitchDellX1052UnderTest(
			match_index_kwargs = {
				"return_value": expected_prompts.index(SwitchDellX1052.CONSOLE_PROMPT),
			},
		)

		test_switch.reload()

		# Expect that reboot was asked for only.
		test_switch.proc.say.assert_any_call(
			cmd = "reload",
			prompt = expected_prompts,
		)
		# Expect that the process was terminated without any prompts or quit commands
		test_switch.proc.end.assert_called_once_with(quit_cmd = "", prompt = "")
