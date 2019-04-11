from unittest.mock import create_autospec, ANY, patch, call
import pytest
from stack.commands import DatabaseConnection
from stack.commands.remove.host.firmware.mapping import Command
from stack.exception import CommandError
from stack.commands.remove.host.firmware.mapping.plugin_basic import Plugin

class TestRemoveHostFirmwareMappingBasicPlugin:
	"""A test case for the remove host firmware mapping basic plugin."""

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
		"""Ensure that provides returns 'basic'."""
		assert basic_plugin.provides() == "basic"

	def test_validate_make(self, basic_plugin):
		"""Ensure the make is validated if it exists."""
		mock_make = "foo"

		basic_plugin.validate_make(make = mock_make)

		basic_plugin.owner.ensure_make_exists.assert_called_once_with(
			make = mock_make,
		)

	def test_validate_make_not_provided(self, basic_plugin):
		"""Ensure the make is not validated if not provided."""
		mock_make = ""

		basic_plugin.validate_make(make = mock_make)

		basic_plugin.owner.ensure_make_exists.assert_not_called()

	def test_validate_make_error(self, basic_plugin):
		"""Ensure that validation fails when the make is invalid."""
		mock_make = "foo"
		basic_plugin.owner.ensure_make_exists.side_effect = CommandError(
			cmd = basic_plugin.owner,
			msg = "Test error",
		)

		with pytest.raises(CommandError):
			basic_plugin.validate_make(make = mock_make)

	def test_validate_model(self, basic_plugin):
		"""Ensure the model is validated if it exists."""
		mock_make = "foo"
		mock_model = "bar"

		basic_plugin.validate_model(make = mock_make, model = mock_model)

		basic_plugin.owner.ensure_model_exists.assert_called_once_with(
			make = mock_make,
			model = mock_model,
		)

	def test_validate_model_not_provided(self, basic_plugin):
		"""Ensure the model is not validated if not provided."""
		mock_make = "foo"
		mock_model = ""

		basic_plugin.validate_model(make = mock_make, model = mock_model)

		basic_plugin.owner.ensure_model_exists.assert_not_called()

	def test_validate_model_error(self, basic_plugin):
		"""Ensure that validation fails when the model is invalid."""
		mock_make = "foo"
		mock_model = "bar"
		basic_plugin.owner.ensure_model_exists.side_effect = CommandError(
			cmd = basic_plugin.owner,
			msg = "Test error",
		)

		with pytest.raises(CommandError):
			basic_plugin.validate_model(make = mock_make, model = mock_model)

	@pytest.mark.parametrize(
		"hosts, versions, make, model",
		(
			(["foo"], ["bar"], "baz", "bag"),
			(["foo"], [], "baz", "bag"),
			(["foo"], [], "baz", ""),
			(["foo"], [], "", ""),
			([], ["bar"], "baz", "bag"),
			([], [], "baz", "bag"),
			([], [], "baz", ""),
			([], [], "", ""),
		)
	)
	def test_get_firmware_mappings_to_remove(self, hosts, versions, make, model, basic_plugin):
		"""Test that get_firmware_mappings_to_remove works as expected for every valid argument combination."""
		test_inputs = {
			"hosts": hosts,
			"versions": versions,
			"make": make,
			"model": model,
		}
		basic_plugin.owner.db.select.return_value = [["1"]]
		expected_query_params = list(value for value in test_inputs.values() if value)

		assert [basic_plugin.owner.db.select.return_value[0][0]] == basic_plugin.get_firmware_mappings_to_remove(**test_inputs)
		basic_plugin.owner.db.select.assert_called_once_with(ANY, expected_query_params)

	@patch.object(target = Plugin, attribute = "get_firmware_mappings_to_remove", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_model", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_make", autospec = True)
	@patch(target = "stack.commands.remove.host.firmware.mapping.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.host.firmware.mapping.plugin_basic.unique_everseen", autospec = True)
	def test_run(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_validate_make,
		mock_validate_model,
		mock_get_firmware_mappings_to_remove,
		basic_plugin,
	):
		"""Test that run works as expected when all params and args are provided and valid."""
		mock_args = ["foo", "bar"]
		expected_hosts = tuple(mock_args)
		mock_params = {"make": "fizz", "model": "buzz", "versions": "bazz, bang"}
		expected_versions = tuple(version.strip() for version in mock_params["versions"].split(",") if version.strip())
		mock_lowered.return_value = mock_params.values()
		mock_unique_everseen.side_effect = (
			mock_args,
			expected_versions,
		)
		basic_plugin.owner.getHosts.return_value = expected_hosts
		mock_get_firmware_mappings_to_remove.return_value = ["1", "2"]

		basic_plugin.run(args = (mock_params, mock_args))

		assert [call(mock_args), call(basic_plugin.owner.fillParams.return_value)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_any_call(mock_lowered.return_value)
		# Check the generator expression passed to the second call of unique_everseen
		assert tuple(mock_unique_everseen.call_args_list[1][0][0]) == expected_versions
		basic_plugin.owner.getHosts.assert_called_once_with(args = expected_hosts)
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [
				("make", ""),
				("model", ""),
				("versions", ""),
			],
			params = mock_params,
		)
		mock_validate_make.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
		)
		mock_validate_model.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			model = mock_params["model"],
		)
		basic_plugin.owner.ensure_firmwares_exist.assert_called_once_with(
			make = mock_params["make"],
			model = mock_params["model"],
			versions = expected_versions,
		)
		mock_get_firmware_mappings_to_remove.assert_called_once_with(
			basic_plugin,
			hosts = expected_hosts,
			make = mock_params["make"],
			model = mock_params["model"],
			versions = expected_versions,
		)
		basic_plugin.owner.db.execute.assert_called_once_with(
			ANY,
			(mock_get_firmware_mappings_to_remove.return_value,),
		)

	@patch.object(target = Plugin, attribute = "get_firmware_mappings_to_remove", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_model", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_make", autospec = True)
	@patch(target = "stack.commands.remove.host.firmware.mapping.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.host.firmware.mapping.plugin_basic.unique_everseen", autospec = True)
	def test_run_no_hosts_or_versions(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_validate_make,
		mock_validate_model,
		mock_get_firmware_mappings_to_remove,
		basic_plugin,
	):
		"""Test that run works as expected when hosts and versions are not provided."""
		mock_args = []
		expected_hosts = tuple(mock_args)
		mock_params = {"make": "fizz", "model": "buzz", "versions": ""}
		mock_lowered.return_value = mock_params.values()
		mock_unique_everseen.return_value = mock_args
		mock_get_firmware_mappings_to_remove.return_value = ["1", "2"]

		basic_plugin.run(args = (mock_params, mock_args))

		assert [call(mock_args), call(basic_plugin.owner.fillParams.return_value)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		basic_plugin.owner.getHosts.assert_not_called()
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [
				("make", ""),
				("model", ""),
				("versions", ""),
			],
			params = mock_params,
		)
		mock_validate_make.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
		)
		mock_validate_model.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			model = mock_params["model"],
		)
		basic_plugin.owner.ensure_firmwares_exist.assert_not_called()
		mock_get_firmware_mappings_to_remove.assert_called_once_with(
			basic_plugin,
			hosts = expected_hosts,
			make = mock_params["make"],
			model = mock_params["model"],
			versions = mock_params["versions"],
		)
		basic_plugin.owner.db.execute.assert_called_once_with(
			ANY,
			(mock_get_firmware_mappings_to_remove.return_value,),
		)

	@patch.object(target = Plugin, attribute = "get_firmware_mappings_to_remove", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_model", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_make", autospec = True)
	@patch(target = "stack.commands.remove.host.firmware.mapping.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.host.firmware.mapping.plugin_basic.unique_everseen", autospec = True)
	def test_run_no_mappings_to_remove(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_validate_make,
		mock_validate_model,
		mock_get_firmware_mappings_to_remove,
		basic_plugin,
	):
		"""Test that run works as expected when there are no mappings to remove."""
		mock_args = ["foo", "bar"]
		expected_hosts = tuple(mock_args)
		mock_params = {"make": "fizz", "model": "buzz", "versions": "bazz, bang"}
		expected_versions = tuple(version.strip() for version in mock_params["versions"].split(",") if version.strip())
		mock_lowered.return_value = mock_params.values()
		mock_unique_everseen.side_effect = (
			mock_args,
			expected_versions,
		)
		basic_plugin.owner.getHosts.return_value = expected_hosts
		mock_get_firmware_mappings_to_remove.return_value = []

		basic_plugin.run(args = (mock_params, mock_args))

		assert [call(mock_args), call(basic_plugin.owner.fillParams.return_value)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_any_call(mock_lowered.return_value)
		# Check the generator expression passed to the second call of unique_everseen
		assert tuple(mock_unique_everseen.call_args_list[1][0][0]) == expected_versions
		basic_plugin.owner.getHosts.assert_called_once_with(args = expected_hosts)
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [
				("make", ""),
				("model", ""),
				("versions", ""),
			],
			params = mock_params,
		)
		mock_validate_make.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
		)
		mock_validate_model.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			model = mock_params["model"],
		)
		basic_plugin.owner.ensure_firmwares_exist.assert_called_once_with(
			make = mock_params["make"],
			model = mock_params["model"],
			versions = expected_versions,
		)
		mock_get_firmware_mappings_to_remove.assert_called_once_with(
			basic_plugin,
			hosts = expected_hosts,
			make = mock_params["make"],
			model = mock_params["model"],
			versions = expected_versions,
		)
		basic_plugin.owner.db.execute.assert_not_called()

	@pytest.mark.parametrize("failure_mock", ("validate_make", "validate_model", "ensure_firmwares_exist"))
	@patch.object(target = Plugin, attribute = "get_firmware_mappings_to_remove", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_model", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_make", autospec = True)
	@patch(target = "stack.commands.remove.host.firmware.mapping.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.host.firmware.mapping.plugin_basic.unique_everseen", autospec = True)
	def test_run_errors(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_validate_make,
		mock_validate_model,
		mock_get_firmware_mappings_to_remove,
		failure_mock,
		basic_plugin,
	):
		"""Test that run fails when the params or args are invalid."""
		mock_args = ["foo", "bar"]
		expected_hosts = tuple(mock_args)
		mock_params = {"make": "fizz", "model": "buzz", "versions": "bazz, bang"}
		expected_versions = tuple(version.strip() for version in mock_params["versions"].split(",") if version.strip())
		mock_lowered.return_value = mock_params.values()
		mock_unique_everseen.side_effect = (
			mock_args,
			expected_versions,
		)
		basic_plugin.owner.getHosts.return_value = expected_hosts
		mock_validation_functions = {
			"validate_make": mock_validate_make,
			"validate_model": mock_validate_model,
			"ensure_firmwares_exist": basic_plugin.owner.ensure_firmwares_exist,
		}
		mock_validation_functions[failure_mock].side_effect = CommandError(
			cmd = basic_plugin.owner,
			msg = "test error",
		)

		with pytest.raises(CommandError):
			basic_plugin.run(args = (mock_params, mock_args))

		basic_plugin.owner.db.execute.assert_not_called()
