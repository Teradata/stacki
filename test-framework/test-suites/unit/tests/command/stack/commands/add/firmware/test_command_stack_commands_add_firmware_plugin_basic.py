from unittest.mock import create_autospec, patch, ANY, call
from collections import namedtuple
from contextlib import ExitStack
from pathlib import Path
import re
import pytest
from stack.commands import DatabaseConnection
from stack.commands.add.firmware import Command
from stack.commands.add.firmware.plugin_basic import Plugin
from stack.exception import CommandError, ArgError, ParamRequired, ParamError
import stack.firmware

class TestAddFirmwareBasicPlugin:
	"""A test case for the add firmware basic plugin."""

	@pytest.fixture
	def basic_plugin(self):
		"""A fixture that returns the plugin instance for use in tests.

		This sets up the required mocks needed to construct the plugin class.
		"""
		mock_command = create_autospec(
			spec = Command,
			instance = True,
		)
		mock_command.db = create_autospec(
			spec = DatabaseConnection,
			spec_set = True,
			instance = True,
		)
		return Plugin(command = mock_command)

	def test_provides(self, basic_plugin):
		"""Ensure the plugin returns the correct provides information."""
		assert basic_plugin.provides() == "basic"

	def test_validate_args(self, basic_plugin):
		"""Test that validate args works when only one argument is passed."""
		basic_plugin.validate_args(args = ["foo"])

	@pytest.mark.parametrize("args", (["foo", "bar"], []))
	def test_validate_args_errors(self, args, basic_plugin):
		"""Test that validate args fails when invalid arguments are passed."""
		with pytest.raises(ArgError):
			basic_plugin.validate_args(args = args)

	def test_validate_required_params(self, basic_plugin):
		"""Test that validate_required_params works if all required params are provided."""
		basic_plugin.validate_required_params(make = "foo", model = "bar", source = "baz")

	@pytest.mark.parametrize(
		"make, model, source",
		(
			("foo", "bar", ""),
			("foo", "", "baz"),
			("", "bar", "baz"),
		)
	)
	def test_validate_required_params_errors(self, make, model, source, basic_plugin):
		"""Test that validate_required_params fails when required params are missing."""
		with pytest.raises(ParamRequired):
			basic_plugin.validate_required_params(make = make, model = model, source = source)

	@pytest.mark.parametrize(
		"imp, model_exists_return, call_return",
		(
			("", True, [{"implementation": ""}]),
			("foo", False, [{"implementation": ""}]),
			("foo", True, [{"implementation": "foo"}]),
		)
	)
	def test_validate_imp(self, imp, model_exists_return, call_return, basic_plugin):
		"""Test that validate_imp works with the expected valid combinations of parameters."""
		mock_make = "fizz"
		mock_model = "buzz"
		basic_plugin.owner.model_exists.return_value = model_exists_return
		basic_plugin.owner.call.return_value = call_return

		basic_plugin.validate_imp(make = mock_make, model = mock_model, imp = imp)

		# Ensure the expected calls were made when checking if the parameters were valid.
		basic_plugin.owner.model_exists.assert_any_call(make = mock_make, model = mock_model)
		if call_return[0]["implementation"]:
			basic_plugin.owner.call.assert_called_once_with(
				command = "list.firmware.model",
				args = [mock_model, f"make={mock_make}"]
			)

	@pytest.mark.parametrize(
		"imp, model_exists_return, call_return",
		(
			("", False, [{"make": "blah", "model": "blah"}]),
			("foo", True, [{"implementation": "bar"}]),
		)
	)
	def test_validate_imp_errors(self, imp, model_exists_return, call_return, basic_plugin):
		"""Test that validate_imp fails with the invalid combinations of parameters."""
		mock_make = "fizz"
		mock_model = "buzz"
		basic_plugin.owner.model_exists.return_value = model_exists_return
		basic_plugin.owner.call.return_value = call_return

		with pytest.raises(ParamError):
			basic_plugin.validate_imp(make = mock_make, model = mock_model, imp = imp)

	@patch(target = "stack.firmware.ensure_hash_alg_supported", autospec = True)
	def test_validate_hash_alg_supported(self, mock_ensure_hash_alg_supported, basic_plugin):
		"""Test that validate_hash_alg_supported works when the algorithm is supported."""
		mock_alg = "md5"

		basic_plugin.validate_hash_alg_supported(hash_alg = mock_alg)

		# Make sure it was validated
		mock_ensure_hash_alg_supported.assert_called_once_with(hash_alg = mock_alg)

	@patch(target = "stack.firmware.ensure_hash_alg_supported", autospec = True)
	def test_validate_hash_alg_supported_error(self, mock_ensure_hash_alg_supported, basic_plugin):
		"""Test that validate_hash_alg_supported fails and re-raises the right exception when ensure_hash_alg_supported fails."""
		mock_alg = "md5"
		mock_ensure_hash_alg_supported.side_effect = stack.firmware.FirmwareError("Test error")

		with pytest.raises(ParamError):
			basic_plugin.validate_hash_alg_supported(hash_alg = mock_alg)

	MockRegexReturn = namedtuple("MockRegexReturn", ("name", "regex", "description"))

	@pytest.mark.parametrize(
		"regex",
		(tuple(), MockRegexReturn(name = "test", regex = "foo", description = "test"))
	)
	@patch(target = "re.search", autospec = True)
	def test_validate_version(self, mock_search, regex, basic_plugin):
		"""Test that validate version regex works as expected when the version is valid."""
		mock_version = "fizz"
		mock_make = "buzz"
		mock_model = "bam!"
		basic_plugin.owner.try_get_version_regex.return_value = regex
		basic_plugin.owner.firmware_exists.return_value = False
		mock_search.return_value = True

		basic_plugin.validate_version(version = mock_version, make = mock_make, model = mock_model)

		# Make sure the version was validated
		basic_plugin.owner.firmware_exists.assert_called_once_with(
			version = mock_version,
			make = mock_make,
			model = mock_model,
		)
		basic_plugin.owner.try_get_version_regex.assert_called_once_with(
			make = mock_make,
			model = mock_model,
		)
		if regex:
			mock_search.assert_called_once_with(
				pattern = regex.regex,
				string = mock_version,
				flags = re.IGNORECASE,
			)

	@pytest.mark.parametrize(
		"regex, search_return, firmware_return",
		(
			(MockRegexReturn(name = "test", regex = "foo", description = "test"), False, False),
			(MockRegexReturn(name = "test", regex = "foo", description = "test"), False, True),
			(tuple(), False, True),
		)
	)
	@patch(target = "re.search", autospec = True)
	def test_validate_version_errors(self, mock_search, regex, search_return, firmware_return, basic_plugin):
		"""Test that validate version regex works as expected when the version is valid."""
		mock_version = "fizz"
		mock_make = "buzz"
		mock_model = "bam!"
		basic_plugin.owner.try_get_version_regex.return_value = regex
		basic_plugin.owner.firmware_exists.return_value = firmware_return
		mock_search.return_value = search_return

		with pytest.raises(ArgError):
			basic_plugin.validate_version(version = mock_version, make = mock_make, model = mock_model)

	@patch.object(target = Plugin, attribute = "validate_required_params", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_hash_alg_supported", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_imp", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_version", autospec = True)
	def test_validate_inputs(
		self,
		mock_validate_version,
		mock_validate_imp,
		mock_validate_hash_alg_supported,
		mock_validate_required_params,
		basic_plugin,
	):
		"""Test that validate_inputs invokes the correct validation functions."""
		mock_source = "foo"
		mock_make = "bar"
		mock_model = "baz"
		mock_version = "bag"
		mock_imp = "fizz"
		mock_hash_alg = "md5"

		basic_plugin.validate_inputs(
			source = mock_source,
			make = mock_make,
			model = mock_model,
			version = mock_version,
			imp = mock_imp,
			hash_alg = mock_hash_alg,
		)

		mock_validate_version.assert_called_once_with(
			basic_plugin,
			make = mock_make,
			model = mock_model,
			version = mock_version,
		)
		mock_validate_imp.assert_called_once_with(
			basic_plugin,
			imp = mock_imp,
			make = mock_make,
			model = mock_model,
		)
		mock_validate_hash_alg_supported.assert_called_once_with(
			basic_plugin,
			hash_alg = mock_hash_alg,
		)
		mock_validate_required_params.assert_called_once_with(
			basic_plugin,
			source = mock_source,
			make = mock_make,
			model = mock_model,
		)

	@pytest.mark.parametrize(
		"failure_mock",
		("validate_required_params", "validate_hash_alg_supported", "validate_imp", "validate_version"),
	)
	@patch.object(target = Plugin, attribute = "validate_required_params", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_hash_alg_supported", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_imp", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_version", autospec = True)
	def test_validate_inputs_errors(
		self,
		mock_validate_version,
		mock_validate_imp,
		mock_validate_hash_alg_supported,
		mock_validate_required_params,
		failure_mock,
		basic_plugin,
	):
		"""Test that validate_inputs fails if any of the validation functions fail."""
		mock_source = "foo"
		mock_make = "bar"
		mock_model = "baz"
		mock_version = "bag"
		mock_imp = "fizz"
		mock_hash_alg = "md5"
		mock_validation_functions = {
			"validate_required_params": mock_validate_required_params,
			"validate_hash_alg_supported": mock_validate_hash_alg_supported,
			"validate_imp": mock_validate_imp,
			"validate_version": mock_validate_version,
		}
		mock_validation_functions[failure_mock].side_effect = CommandError(
			cmd = basic_plugin.owner,
			msg = "test error",
		)

		with pytest.raises(CommandError):
			basic_plugin.validate_inputs(
				source = mock_source,
				make = mock_make,
				model = mock_model,
				version = mock_version,
				imp = mock_imp,
				hash_alg = mock_hash_alg,
			)

	def test_create_missing_imp(self, basic_plugin):
		"""Test that create missing imp calls the expected functions when the imp doesn't exist."""
		mock_imp = "foo"
		basic_plugin.owner.imp_exists.return_value = False
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_imp(imp = mock_imp, cleanup = mock_cleanup)

			# Make sure appropriate calls were made
			basic_plugin.owner.call.assert_called_once_with(
				command = "add.firmware.imp",
				args = [mock_imp],
			)
			mock_cleanup.callback.assert_called_once_with(
				basic_plugin.owner.call,
				command = "remove.firmware.imp",
				args = [mock_imp],
			)

	@pytest.mark.parametrize("imp, return_value", (("foo", True), ("", "unused")))
	def test_create_missing_imp_skipped(self, imp, return_value, basic_plugin):
		"""Test that create missing imp skips implementation creation based on provided arguments."""
		mock_imp = imp
		basic_plugin.owner.imp_exists.return_value = return_value
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_imp(imp = mock_imp, cleanup = mock_cleanup)

			# Make sure no implementations were attempted to be created
			basic_plugin.owner.call.assert_not_called()
			mock_cleanup.callback.assert_not_called()

	def test_create_missing_make(self, basic_plugin):
		"""Test that create missing make calls the expected functions when the make doesn't exist."""
		mock_make = "foo"
		basic_plugin.owner.make_exists.return_value = False
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_make(make = mock_make, cleanup = mock_cleanup)

			# Make sure appropriate calls were made
			basic_plugin.owner.call.assert_called_once_with(
				command = "add.firmware.make",
				args = [mock_make],
			)
			mock_cleanup.callback.assert_called_once_with(
				basic_plugin.owner.call,
				command = "remove.firmware.make",
				args = [mock_make],
			)

	def test_create_missing_make_skipped(self, basic_plugin):
		"""Test that create missing make skips implementation creation based on provided arguments."""
		mock_make = "foo"
		basic_plugin.owner.imp_exists.return_value = True
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_make(make = mock_make, cleanup = mock_cleanup)

			# Make sure no makes were attempted to be created
			basic_plugin.owner.call.assert_not_called()
			mock_cleanup.callback.assert_not_called()

	def test_create_missing_model(self, basic_plugin):
		"""Test that create missing model calls the expected functions when the make doesn't exist."""
		mock_make = "foo"
		mock_model = "bar"
		mock_imp = "baz"
		basic_plugin.owner.model_exists.return_value = False
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_model(
				make = mock_make,
				model = mock_model,
				imp = mock_imp,
				cleanup = mock_cleanup,
			)

			# Make sure appropriate calls were made
			basic_plugin.owner.call.assert_called_once_with(
				command = "add.firmware.model",
				args = [mock_model, f"make={mock_make}", f"imp={mock_imp}"],
			)
			mock_cleanup.callback.assert_called_once_with(
				basic_plugin.owner.call,
				command = "remove.firmware.model",
				args = [mock_model, f"make={mock_make}"],
			)

	def test_create_missing_model_skipped(self, basic_plugin):
		"""Test that create missing model skips implementation creation based on provided arguments."""
		mock_make = "foo"
		mock_model = "bar"
		mock_imp = "baz"
		basic_plugin.owner.model_exists.return_value = True
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_model(
				make = mock_make,
				model = mock_model,
				imp = mock_imp,
				cleanup = mock_cleanup,
			)

			# Make sure no makes were attempted to be created
			basic_plugin.owner.call.assert_not_called()
			mock_cleanup.callback.assert_not_called()

	@patch.object(target = Plugin, attribute = "create_missing_imp", autospec = True)
	@patch.object(target = Plugin, attribute = "create_missing_make", autospec = True)
	@patch.object(target = Plugin, attribute = "create_missing_model", autospec = True)
	def test_create_missing_related_entries(
		self,
		mock_create_missing_model,
		mock_create_missing_make,
		mock_create_missing_imp,
		basic_plugin,
	):
		"""Test that all missing related entries are attempted to be created."""
		mock_make = "foo"
		mock_model = "bar"
		mock_imp = "baz"
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_related_entries(
				make = mock_make,
				model = mock_model,
				imp = mock_imp,
				cleanup = mock_cleanup,
			)

			mock_create_missing_model.assert_called_once_with(
				basic_plugin,
				make = mock_make,
				model = mock_model,
				imp = mock_imp,
				cleanup = mock_cleanup,
			)
			mock_create_missing_make.assert_called_once_with(
				basic_plugin,
				make = mock_make,
				cleanup = mock_cleanup,
			)
			mock_create_missing_imp.assert_called_once_with(
				basic_plugin,
				imp = mock_imp,
				cleanup = mock_cleanup,
			)

	@pytest.mark.parametrize("failure_mock", ("create_missing_imp", "create_missing_make", "create_missing_model"))
	@patch.object(target = Plugin, attribute = "create_missing_imp", autospec = True)
	@patch.object(target = Plugin, attribute = "create_missing_make", autospec = True)
	@patch.object(target = Plugin, attribute = "create_missing_model", autospec = True)
	def test_create_missing_related_entries_errors(
		self,
		mock_create_missing_model,
		mock_create_missing_make,
		mock_create_missing_imp,
		failure_mock,
		basic_plugin,
	):
		"""Test that create_missing_related_entries fails when adding any related entry fails."""
		mock_make = "foo"
		mock_model = "bar"
		mock_imp = "baz"
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)
		mock_creation_functions = {
			"create_missing_imp": mock_create_missing_imp,
			"create_missing_make": mock_create_missing_make,
			"create_missing_model": mock_create_missing_model,
		}
		mock_creation_functions[failure_mock].side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test error")

		with mock_exit_stack() as mock_cleanup:
			with pytest.raises(CommandError):
				basic_plugin.create_missing_related_entries(
					make = mock_make,
					model = mock_model,
					imp = mock_imp,
					cleanup = mock_cleanup,
				)

	def test_file_cleanup(self, basic_plugin):
		"""Test that file path works as expected when the file still exists."""
		mock_path = create_autospec(spec = Path, spec_set = True, instance = True)
		mock_path.exists.return_value = True

		basic_plugin.file_cleanup(file_path = mock_path)

		mock_path.exists.assert_called_once_with()
		mock_path.unlink.assert_called_once_with()

	def test_file_cleanup_skip(self, basic_plugin):
		"""Test that file path skips unlinking when the file doesn't exist."""
		mock_path = create_autospec(spec = Path, spec_set = True, instance = True)
		mock_path.exists.return_value = False

		basic_plugin.file_cleanup(file_path = mock_path)

		mock_path.exists.assert_called_once_with()
		mock_path.unlink.assert_not_called()

	@patch(target = "stack.firmware.fetch_firmware", autospec = True)
	@patch.object(target = Plugin, attribute = "file_cleanup", autospec = True)
	def test_fetch_firmware(self, mock_file_cleanup, mock_fetch_firmware, basic_plugin):
		"""Test that fetch_firmware works as expected when the firmware can be fetched from the source."""
		mock_source = "/foo/bar"
		mock_make = "foo"
		mock_model = "bar"
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)

		with mock_exit_stack() as mock_cleanup:
			result = basic_plugin.fetch_firmware(
				source = mock_source,
				make = mock_make,
				model = mock_model,
				cleanup = mock_cleanup,
			)

			mock_fetch_firmware.assert_called_once_with(
				source = mock_source,
				make = mock_make,
				model = mock_model,
			)
			mock_cleanup.callback.assert_called_once_with(
				basic_plugin.file_cleanup,
				file_path = mock_fetch_firmware.return_value,
			)
			assert mock_fetch_firmware.return_value == result

	@patch(target = "stack.firmware.fetch_firmware", autospec = True)
	@patch.object(target = Plugin, attribute = "file_cleanup", autospec = True)
	def test_fetch_firmware_error(self, mock_file_cleanup, mock_fetch_firmware, basic_plugin):
		"""Test that fetch_firmware raises the correct exception type when stack.firmware.fetch_firmware fails."""
		mock_source = "/foo/bar"
		mock_make = "foo"
		mock_model = "bar"
		mock_fetch_firmware.side_effect = stack.firmware.FirmwareError("test error")
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)

		with mock_exit_stack() as mock_cleanup:
			with pytest.raises(ParamError):
				basic_plugin.fetch_firmware(
					source = mock_source,
					make = mock_make,
					model = mock_model,
					cleanup = mock_cleanup,
				)

			mock_fetch_firmware.assert_called_once_with(
				source = mock_source,
				make = mock_make,
				model = mock_model,
			)
			mock_cleanup.callback.assert_not_called()

	@patch(target = "stack.firmware.calculate_hash", autospec = True)
	def test_calculate_hash(self, mock_calculate_hash, basic_plugin):
		"""Test that calculate hash works as expected when the hash is valid."""
		mock_file_path = "/foo"
		mock_hash_alg = "md5"
		mock_hash_value = "bar"

		result = basic_plugin.calculate_hash(
			file_path = mock_file_path,
			hash_alg = mock_hash_alg,
			hash_value = mock_hash_value,
		)

		assert mock_calculate_hash.return_value == result
		mock_calculate_hash.assert_called_once_with(
			file_path = mock_file_path,
			hash_alg = mock_hash_alg,
			hash_value = mock_hash_value,
		)

	@patch(target = "stack.firmware.calculate_hash", autospec = True)
	def test_calculate_hash_error(self, mock_calculate_hash, basic_plugin):
		"""Test that calculate hash raises the correct exception type on a failure."""
		mock_file_path = "/foo"
		mock_hash_alg = "md5"
		mock_hash_value = "bar"
		mock_calculate_hash.side_effect = stack.firmware.FirmwareError("Test error")

		with pytest.raises(ParamError):
			basic_plugin.calculate_hash(
				file_path = mock_file_path,
				hash_alg = mock_hash_alg,
				hash_value = mock_hash_value,
			)

	@patch.object(target = Plugin, attribute = "create_missing_related_entries", autospec = True)
	@patch.object(target = Plugin, attribute = "calculate_hash", autospec = True)
	@patch.object(target = Plugin, attribute = "fetch_firmware", autospec = True)
	def test_add_firmware(
		self,
		mock_fetch_firmware,
		mock_calculate_hash,
		mock_create_missing_related_entries,
		basic_plugin,
	):
		"""Test that adding firmware performs the expected actions."""
		mock_source = "foo"
		mock_make = "bar"
		mock_model = "baz"
		mock_version = "bag"
		mock_imp = "fizz"
		mock_hash_value = "buzz"
		mock_hash_alg = "md5"
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.add_firmware(
				source = mock_source,
				make = mock_make,
				model = mock_model,
				version = mock_version,
				imp = mock_imp,
				hash_value = mock_hash_value,
				hash_alg = mock_hash_alg,
				cleanup = mock_cleanup,
			)

			mock_fetch_firmware.assert_called_once_with(
				basic_plugin,
				source = mock_source,
				make = mock_make,
				model = mock_model,
				cleanup = mock_cleanup,
			)
			mock_calculate_hash.assert_called_once_with(
				basic_plugin,
				file_path = mock_fetch_firmware.return_value,
				hash_value = mock_hash_value,
				hash_alg = mock_hash_alg,
			)
			mock_create_missing_related_entries.assert_called_once_with(
				basic_plugin,
				make = mock_make,
				model = mock_model,
				imp = mock_imp,
				cleanup = mock_cleanup,
			)
			basic_plugin.owner.get_model_id.assert_called_once_with(
				make = mock_make,
				model = mock_model,
			)
			basic_plugin.owner.db.execute.assert_called_once_with(
				ANY,
				(
					basic_plugin.owner.get_model_id.return_value,
					mock_source,
					mock_version,
					mock_hash_alg,
					mock_calculate_hash.return_value,
					str(mock_fetch_firmware.return_value),
				)
			)
			mock_cleanup.callback.assert_called_once_with(
				basic_plugin.owner.call,
				command = "remove.firmware",
				args = [mock_version, f"make={mock_make}", f"model={mock_model}"],
			)

	@pytest.mark.parametrize(
		"failure_mock",
		("create_missing_related_entries", "calculate_hash", "fetch_firmware"),
	)
	@patch.object(target = Plugin, attribute = "create_missing_related_entries", autospec = True)
	@patch.object(target = Plugin, attribute = "calculate_hash", autospec = True)
	@patch.object(target = Plugin, attribute = "fetch_firmware", autospec = True)
	def test_add_firmware_errors(
		self,
		mock_fetch_firmware,
		mock_calculate_hash,
		mock_create_missing_related_entries,
		failure_mock,
		basic_plugin,
	):
		"""Test that adding firmware fails when performing related actions fails."""
		mock_source = "foo"
		mock_make = "bar"
		mock_model = "baz"
		mock_version = "bag"
		mock_imp = "fizz"
		mock_hash_value = "buzz"
		mock_hash_alg = "md5"
		mock_exit_stack = create_autospec(spec = ExitStack, spec_set = True)
		mock_functions = {
			"create_missing_related_entries": mock_create_missing_related_entries,
			"calculate_hash": mock_calculate_hash,
			"fetch_firmware": mock_fetch_firmware,
		}
		mock_functions[failure_mock].side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test error")

		with mock_exit_stack() as mock_cleanup:
			with pytest.raises(CommandError):
				basic_plugin.add_firmware(
					source = mock_source,
					make = mock_make,
					model = mock_model,
					version = mock_version,
					imp = mock_imp,
					hash_value = mock_hash_value,
					hash_alg = mock_hash_alg,
					cleanup = mock_cleanup,
				)

			basic_plugin.owner.db.execute.assert_not_called()

	@patch.object(target = Plugin, attribute = "add_firmware", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_inputs", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	@patch(target = "stack.commands.add.firmware.plugin_basic.ExitStack", autospec = True)
	@patch(target = "stack.commands.add.firmware.plugin_basic.unique_everseen", autospec = True)
	@patch(target = "stack.commands.add.firmware.plugin_basic.lowered", autospec = True)
	def test_run(
		self,
		mock_lowered,
		mock_unique_everseen,
		mock_exit_stack,
		mock_validate_args,
		mock_validate_inputs,
		mock_add_firmware,
		basic_plugin,
	):
		"""Test that run performs all expected operations when all params and args are valid."""
		mock_params = {
			"make": "foo",
			"model": "bar",
			"imp": "baz",
			"hosts": "herp, derp, ferp",
			"hash_alg": "md5",
			"hash": "1234",
			"source": "/fizz/buzz",
		}
		mock_args = ["MOCK_VERSION"]
		expected_version = mock_args[0].lower()
		expected_hosts = tuple(host.strip() for host in mock_params["hosts"].split(",") if host.strip())
		expected_lower_params = list(mock_params.values())[:5]
		basic_plugin.owner.fillParams.return_value = mock_params.values()
		mock_lowered.return_value = expected_lower_params
		mock_unique_everseen.return_value = expected_hosts
		basic_plugin.owner.getHosts.return_value = expected_hosts

		basic_plugin.run(args = (mock_params, mock_args))

		mock_validate_args.assert_called_once_with(basic_plugin, args = mock_args)
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [
				("make", ""),
				("model", ""),
				("imp", ""),
				("hosts", ""),
				("hash_alg", "md5"),
				("hash", ""),
				("source", ""),
			],
			params = mock_params,
		)
		mock_lowered.assert_called_once_with(expected_lower_params)
		mock_validate_inputs.assert_called_once_with(
			basic_plugin,
			source = mock_params["source"],
			make = mock_params["make"],
			model = mock_params["model"],
			version = expected_version,
			imp = mock_params["imp"],
			hash_alg = mock_params["hash_alg"],
		)
		mock_unique_everseen.assert_called_once()
		args = mock_unique_everseen.call_args[0]
		assert expected_hosts == tuple(args[0])
		basic_plugin.owner.getHosts.assert_called_once_with(args = expected_hosts)
		mock_add_firmware.assert_called_once_with(
			basic_plugin,
			source = mock_params["source"],
			make = mock_params["make"],
			model = mock_params["model"],
			version = expected_version,
			imp = mock_params["imp"],
			hash_value = mock_params["hash"],
			hash_alg = mock_params["hash_alg"],
			cleanup = mock_exit_stack.return_value.__enter__.return_value,
		)
		basic_plugin.owner.call.assert_called_once_with(
			command = "add.host.firmware.mapping",
			args = [
				*expected_hosts,
				f"version={expected_version}",
				f"make={mock_params['make']}",
				f"model={mock_params['model']}",
			],
		)
		mock_exit_stack.return_value.__enter__.return_value.pop_all.assert_called_once_with()

	@patch.object(target = Plugin, attribute = "add_firmware", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_inputs", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	@patch(target = "stack.commands.add.firmware.plugin_basic.ExitStack", autospec = True)
	@patch(target = "stack.commands.add.firmware.plugin_basic.unique_everseen", autospec = True)
	@patch(target = "stack.commands.add.firmware.plugin_basic.lowered", autospec = True)
	def test_run_no_hosts(
		self,
		mock_lowered,
		mock_unique_everseen,
		mock_exit_stack,
		mock_validate_args,
		mock_validate_inputs,
		mock_add_firmware,
		basic_plugin,
	):
		"""Test that run performs all expected operations when all params and args are valid and no hosts are provided."""
		mock_params = {
			"make": "foo",
			"model": "bar",
			"imp": "baz",
			"hosts": "",
			"hash_alg": "md5",
			"hash": "1234",
			"source": "/fizz/buzz",
		}
		mock_args = ["MOCK_VERSION"]
		expected_version = mock_args[0].lower()
		expected_lower_params = list(mock_params.values())[:5]
		basic_plugin.owner.fillParams.return_value = mock_params.values()
		mock_lowered.return_value = expected_lower_params

		basic_plugin.run(args = (mock_params, mock_args))

		mock_validate_args.assert_called_once_with(basic_plugin, args = mock_args)
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [
				("make", ""),
				("model", ""),
				("imp", ""),
				("hosts", ""),
				("hash_alg", "md5"),
				("hash", ""),
				("source", ""),
			],
			params = mock_params,
		)
		mock_lowered.assert_called_once_with(expected_lower_params)
		mock_validate_inputs.assert_called_once_with(
			basic_plugin,
			source = mock_params["source"],
			make = mock_params["make"],
			model = mock_params["model"],
			version = expected_version,
			imp = mock_params["imp"],
			hash_alg = mock_params["hash_alg"],
		)
		mock_unique_everseen.assert_not_called()
		basic_plugin.owner.getHosts.assert_not_called()
		mock_add_firmware.assert_called_once_with(
			basic_plugin,
			source = mock_params["source"],
			make = mock_params["make"],
			model = mock_params["model"],
			version = expected_version,
			imp = mock_params["imp"],
			hash_value = mock_params["hash"],
			hash_alg = mock_params["hash_alg"],
			cleanup = mock_exit_stack.return_value.__enter__.return_value,
		)
		basic_plugin.owner.call.assert_not_called()
		mock_exit_stack.return_value.__enter__.return_value.pop_all.assert_called_once_with()
