from stack.commands import Command, Implementation, ScopeArgProcessor, DatabaseConnection
from stack.exception import CommandError
from unittest.mock import patch, create_autospec, ANY, MagicMock
from concurrent.futures import Future
from collections import namedtuple
import time
import pytest

class CommandUnderTest(Command):
	"""A subclass of Command that replaces __init__ to remove the database dependency."""

	def __init__(self, *args, **kwargs):
		# needed for implementation running and loading functions
		self.impl_list = {}
		# needed for anything that messes with the DB
		self.db = create_autospec(
			spec = DatabaseConnection,
			instance = True,
		)
		self.db.database = MagicMock()
		self.level = 0

class TestCommand:

	@patch.object(Command, 'loadImplementation', autospec = True)
	@patch('stack.commands.ThreadPoolExecutor', autospec = True)
	def test_run_implementations_parallel(self, mock_executor, mock_loadImplementation):
		"""Test the normal case where all implementations are loadable and run to completion."""
		def load_impl(self, name):
			"""Side effect for mock_loadImplementation to set the impl_list"""
			self.impl_list[name] = "_"

		test_command = CommandUnderTest()
		# set the side effect of loadImplementation to set impl list so that one is loaded.
		# The value won't actually be used because we mock the ThreadPoolExecutor.
		mock_loadImplementation.side_effect = load_impl
		# create mock futures specced off of the actual Future class.
		mock_future1 = create_autospec(spec = Future, spec_set = True, instance = True)
		mock_future1.exception.return_value = None
		mock_future1.result.return_value = "Look ma, I'm threading!"
		mock_future2 = create_autospec(spec = Future, spec_set = True)
		mock_future2.exception.return_value = Exception("And that's when Jimmy burst into flames.")
		mock_future2.result.return_value = None
		# Since the ThreadPoolExecutor is used as a context manager, we need this long chain to
		# set the return value of the submit call.
		mock_executor.return_value.__enter__.return_value.submit.side_effect = (mock_future1, mock_future2)

		test_implementation_mapping = {"foo": "bar", "baz": "bog"}
		result = test_command.run_implementations_parallel(
			implementation_mapping = test_implementation_mapping
		)
		assert result == {
			"foo": namedtuple("_", ("result", "exception"))(
				result = mock_future1.result(),
				exception = mock_future1.exception(),
			),
			"baz": namedtuple("_", ("result", "exception"))(
				result = mock_future2.result(),
				exception = mock_future2.exception(),
			)
		}
		for key, value in test_implementation_mapping.items():
			mock_loadImplementation.assert_any_call(test_command, name = key)
			mock_executor.return_value.__enter__.return_value.submit.assert_any_call(
				ANY,
				name = key,
				args = value,
			)

	@patch.object(Command, 'loadImplementation', autospec = True)
	def test_run_implementations_parallel_real_threads(self, mock_loadImplementation):
		"""Test the normal case with real threads, but mocking the implementation run function.

		This is used to ensure the callable submitted is actually going to run the implementation.
		"""
		def load_impl(self, name):
			"""Side effect for mock_loadImplementation to set the impl_list"""
			mock_imp = create_autospec(spec = Implementation, spec_set = True, instance = True)
			mock_imp.run.return_value = "Look ma, I'm threading!"
			self.impl_list[name] = mock_imp

		test_command = CommandUnderTest()
		# set the side effect of loadImplementation to set impl list so that one is loaded.
		# The value won't actually be used because we mock the ThreadPoolExecutor.
		mock_loadImplementation.side_effect = load_impl

		test_implementation_mapping = {"foo": "bar", "baz": "bog"}
		result = test_command.run_implementations_parallel(
			implementation_mapping = test_implementation_mapping
		)
		assert result == {
			key: namedtuple("_", ("result", "exception"))(
				result = "Look ma, I'm threading!",
				exception = None,
			)
			for key in test_implementation_mapping
		}

	@patch.object(Command, 'loadImplementation', autospec = True)
	def test_run_implementations_parallel_real_threads_real_errors(self, mock_loadImplementation):
		"""Test the normal case with real threads, but mocking the implementation run function.

		This is used to ensure the callable submitted is actually going to run the implementation.
		"""
		def load_impl(self, name):
			"""Side effect for mock_loadImplementation to set the impl_list"""
			mock_imp = create_autospec(spec = Implementation, spec_set = True, instance = True)
			mock_imp.run.side_effect = Exception("And that's when Jimmy burst into flames.")
			self.impl_list[name] = mock_imp

		test_command = CommandUnderTest()
		# set the side effect of loadImplementation to set impl list so that one is loaded.
		# The value won't actually be used because we mock the ThreadPoolExecutor.
		mock_loadImplementation.side_effect = load_impl

		test_implementation_mapping = {"foo": "bar", "baz": "bog"}
		result = test_command.run_implementations_parallel(
			implementation_mapping = test_implementation_mapping
		)
		# exception class equality doesn't work the way we want here :(
		assert all(key in result for key in ("foo", "baz"))
		test_exception = Exception("And that's when Jimmy burst into flames.")
		for value in result.values():
			assert value.result is None
			assert type(value.exception) is type(test_exception)
			assert value.exception.args == test_exception.args

	@patch.object(Command, 'loadImplementation', autospec = True)
	@patch('stack.commands.ThreadPoolExecutor', autospec = True)
	def test_run_implementations_parallel_empty_args(self, mock_executor, mock_loadImplementation):
		"""Test that passing a empty implementation mapping causes no actions to occur."""
		test_command = CommandUnderTest()
		result = test_command.run_implementations_parallel(implementation_mapping = {})
		assert result == {}
		mock_executor.return_value.__enter__.return_value.assert_not_called()
		mock_loadImplementation.assert_not_called()

	@patch.object(Command, 'loadImplementation', autospec = True)
	@patch('stack.commands.ThreadPoolExecutor', autospec = True)
	def test_run_implementations_parallel_not_loadable(self, mock_executor, mock_loadImplementation):
		"""Test that when an implementation is not loadable, the result is None for that imp name."""
		test_command = CommandUnderTest()
		test_implementation_mapping = {"foo": "bar", "baz": "bog"}
		result = test_command.run_implementations_parallel(implementation_mapping = test_implementation_mapping)

		assert result == {key: None for key in test_implementation_mapping}
		mock_executor.return_value.__enter__.return_value.assert_not_called()

	@patch.object(Command, 'loadImplementation', autospec = True)
	@patch('stack.commands.ThreadPoolExecutor', autospec = True)
	def test_run_implementations_parallel_partial_loadable(self, mock_executor, mock_loadImplementation):
		"""Test being able to load some implementations but not all."""
		def load_impl(self, name):
			if name == "baz":
				self.impl_list = {name: "_"}

		test_command = CommandUnderTest()
		# set the side effect of loadImplementation to set impl list so that one is loaded.
		# The value won't actually be used because we mock the ThreadPoolExecutor.
		mock_loadImplementation.side_effect = load_impl
		# create a mock future specced off of the actual Future class.
		mock_future = create_autospec(spec = Future, spec_set = True)
		mock_future.exception.return_value = None
		mock_future.result.return_value = None
		# Since the ThreadPoolExecutor is used as a context manager, we need this long chain to
		# set the return value of the submit call.
		mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future
		test_implementation_mapping = {"foo": "bar", "baz": "bog"}
		result = test_command.run_implementations_parallel(
			implementation_mapping = test_implementation_mapping
		)

		assert result == {
			"foo": None,
			"baz": namedtuple("_", ("result", "exception"))(
				result = None,
				exception = None,
			)
		}
		# should only be one implementation submitted
		mock_executor.return_value.__enter__.return_value.submit.assert_called_once_with(
			ANY,
			name = "baz",
			args = "bog",
		)

	@patch.object(Command, 'loadImplementation', autospec = True)
	@patch('stack.commands.ThreadPoolExecutor', autospec = True)
	def test_run_implementations_parallel_already_loaded(self, mock_executor, mock_loadImplementation):
		"""Tests that the already loaded implementations are used."""
		test_implementation_mapping = {"foo": "bar", "baz": "bog"}
		test_command = CommandUnderTest()
		test_command.impl_list = {key: "_" for key in test_implementation_mapping}
		# create a mock future specced off of the actual Future class.
		mock_future = create_autospec(spec = Future, spec_set = True)
		mock_future.exception.return_value = None
		mock_future.result.return_value = None
		# Since the ThreadPoolExecutor is used as a context manager, we need this long chain to
		# set the return value of the submit call.
		mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future

		result = test_command.run_implementations_parallel(
			implementation_mapping = test_implementation_mapping
		)

		assert result == {
			key: namedtuple("_", ("result", "exception"))(
				result = mock_future.result(),
				exception = mock_future.exception(),
			)
			for key in test_implementation_mapping
		}
		# should not try to load any implementations
		mock_loadImplementation.assert_not_called()

	@patch.object(Command, 'loadImplementation', autospec = True)
	@patch('stack.commands.ThreadPoolExecutor', autospec = True)
	def test_run_implementations_parallel_output_enabled_fast_implementations(self, mock_executor, mock_loadImplementation):
		"""Coverage case for the display_progress option where the future finishes before the timer ends."""
		test_implementation_mapping = {"foo": "bar", "baz": "bog"}
		test_command = CommandUnderTest()
		test_command.impl_list = {key: "_" for key in test_implementation_mapping}
		# create a mock future specced off of the actual Future class.
		mock_future = create_autospec(spec = Future, spec_set = True)
		mock_future.exception.return_value = None
		mock_future.result.return_value = None
		mock_future.done.return_value = True
		# Since the ThreadPoolExecutor is used as a context manager, we need this long chain to
		# set the return value of the submit call.
		mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future

		result = test_command.run_implementations_parallel(
			implementation_mapping = test_implementation_mapping,
			display_progress = True
		)

		assert result == {
			key: namedtuple("_", ("result", "exception"))(
				result = mock_future.result(),
				exception = mock_future.exception(),
			)
			for key in test_implementation_mapping
		}

	@patch.object(Command, 'loadImplementation', autospec = True)
	def test_run_implementations_parallel_output_enabled_slow_implementations(self, mock_loadImplementation):
		"""Coverage case for the display_progress option where the future is still not done after the timer expires."""
		test_implementation_mapping = {"foo": "bar", "baz": "bog"}
		test_command = CommandUnderTest()
		# create dummy imps where the side_effect of calling run is to sleep.
		mock_imp1 = create_autospec(spec = Implementation, spec_set = True, instance = True)
		mock_imp1.run.side_effect = lambda args: time.sleep(4)
		mock_imp2 = create_autospec(spec = Implementation, spec_set = True, instance = True)
		mock_imp2.run.side_effect = lambda args: time.sleep(5)
		gen = (impl for impl in (mock_imp1, mock_imp2))
		test_command.impl_list = {
			key: next(gen) for key in test_implementation_mapping
		}

		result = test_command.run_implementations_parallel(
			implementation_mapping = test_implementation_mapping,
			display_progress = True
		)

		assert result == {
			key: namedtuple("_", ("result", "exception"))(
				result = None,
				exception = None,
			)
			for key in test_implementation_mapping
		}

	# To get this to work we're essentially overriding the global __import__ and eval functions
	# in the stack.commands module with mock objects. Mocking the builtins directly doesn't seem
	# to work for eval.
	@patch(target = "stack.commands.__import__", create = True)
	@patch(target = "stack.commands.eval", create = True)
	def test_command_command_error_exception_handling(self, mock_eval, mock__import__):
		"""Test that the CommandError raised contains the command run and the lower tier exception information."""
		# Set the mock's side effect for when runWrapper is called to raise a CommandError.
		mock_eval.return_value.Command.return_value.runWrapper.side_effect = CommandError(
			cmd = create_autospec(spec = Command, instance = True),
			msg = "test error",
		)

		test_command = CommandUnderTest()

		with pytest.raises(CommandError) as exception_info:
			test_command.command(command = "foo.bar.baz", args = ["a", "b=c"])

		# make sure the command is listed as well as its arguments
		assert "foo bar baz a b=c" in exception_info.value.message()
		# make sure the CommandError's message is passed along as well
		assert "test error" in exception_info.value.message()

	# To get this to work we're essentially overriding the global __import__ and eval functions
	# in the stack.commands module with mock objects. Mocking the builtins directly doesn't seem
	# to work for eval.
	@patch(target = "stack.commands.__import__", create = True)
	@patch(target = "stack.commands.eval", create = True)
	def test_command_command_error_exception_handling_verbose_off(self, mock_eval, mock__import__):
		"""Test that the CommandError raised does not contain the command run when verbose errors are turned off."""
		# Set the mock's side effect for when runWrapper is called to raise a CommandError.
		mock_eval.return_value.Command.return_value.runWrapper.side_effect = CommandError(
			cmd = create_autospec(spec = Command, instance = True),
			msg = "test error",
		)

		test_command = CommandUnderTest()

		with pytest.raises(CommandError) as exception_info:
			test_command.command(command = "foo.bar.baz", args = ["a", "b=c"], verbose_errors = False)

		# make sure the command is not listed
		assert "foo bar baz a b=c" not in exception_info.value.message()
		# make sure the CommandError's message is passed along as well
		assert "test error" in exception_info.value.message()

	@pytest.mark.parametrize("verbose_errors", (True, False))
	# To get this to work we're essentially overriding the global __import__ and eval functions
	# in the stack.commands module with mock objects. Mocking the builtins directly doesn't seem
	# to work for eval.
	@patch(target = "stack.commands.__import__", create = True)
	@patch(target = "stack.commands.eval", create = True)
	def test_command_exception_handling(self, mock_eval, mock__import__, verbose_errors):
		"""Test that non-CommandErrors cause a RuntimeError to be raised that contains the command run.

		This should happen regardless of whether verbose_errors were turned off or not.
		"""
		# The getattr is used to return the Command class in the eval'd module and
		# construct the Command instance. Return a mock instead
		mock_eval.return_value.Command = MagicMock()
		# Set the mock's side effect for when runWrapper is called to raise a CommandError.
		mock_eval.return_value.Command.return_value.runWrapper.side_effect = ValueError(
			"test error",
		)

		test_command = CommandUnderTest()

		with pytest.raises(RuntimeError) as exception_info:
			test_command.command(command = "foo.bar.baz", args = ["a", "b=c"], verbose_errors = verbose_errors)

		# make sure the command is listed as well as its arguments
		assert "foo bar baz a b=c" in str(exception_info.value)

class TestScopeArgProcessor:
	"""Test case for the ScopeArgProcessor"""

	def test_getScopeMappings_global_scope(self):
		"""Test that getting the scope mappings works as expected for the global scope."""
		test_scope = "global"
		result = ScopeArgProcessor().getScopeMappings(scope = test_scope)
		assert [(test_scope, None, None, None, None)] == result

	def test_getScopeMappings_global_scope_with_args(self):
		"""Test that getting the scope mappings for the global scope fails when additional args are passed."""
		test_scope = "global"
		test_args = ["foo", "bar"]

		with pytest.raises(CommandError):
			ScopeArgProcessor().getScopeMappings(args = test_args, scope = test_scope)
