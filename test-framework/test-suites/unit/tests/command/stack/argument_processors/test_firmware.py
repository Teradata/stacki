from unittest.mock import MagicMock, ANY, patch, call
import pytest
from stack.exception import CommandError
import stack.commands
from stack.argument_processors.firmware import FirmwareArgumentProcessor

class TestFirmwareArgumentProcessor:
	"""A test case for the firmware argument processor."""

	@pytest.fixture
	def argument_processor(self):
		test_argument_processor = FirmwareArgumentProcessor()
		test_argument_processor.db = MagicMock(spec_set = ["select", "count"])
		return test_argument_processor

	def test_get_make_id(self, argument_processor):
		"""Test that get make ID works as expected in the normal case."""
		argument_processor.db.select.return_value = [[1]]
		mock_make = "foo"

		# Expect our result to be returned.
		assert argument_processor.db.select.return_value[0][0] == argument_processor.get_make_id(
			make = mock_make,
		)
		# Ensure that select was called appropriately.
		argument_processor.db.select.assert_called_once_with(ANY, mock_make)

	def test_get_make_id_error(self, argument_processor):
		"""Test that get make ID fails if no make exists in the DB with that name."""
		argument_processor.db.select.return_value = []

		with pytest.raises(CommandError):
			argument_processor.get_make_id(make = "foo")

	@pytest.mark.parametrize("return_value", (0, 1))
	def test_make_exists(self, argument_processor, return_value):
		"""Test that make exists returns the correct results."""
		argument_processor.db.count.return_value = return_value

		assert return_value == argument_processor.make_exists(make = "foo")
		argument_processor.db.count.assert_called_once_with(ANY, "foo")

	@patch.object(target = FirmwareArgumentProcessor, attribute = "make_exists", autospec = True)
	def test_ensure_make_exists(self, mock_make_exists, argument_processor):
		"""Test that ensure make exists works when the input is valid and the make exists in the database."""
		mock_make_exists.return_value = True
		mock_make = "foo"

		argument_processor.ensure_make_exists(make = mock_make)

		mock_make_exists.assert_called_once_with(argument_processor, make = mock_make)

	@pytest.mark.parametrize("test_input, return_value", (("", True), ("foo", False)))
	@patch.object(target = FirmwareArgumentProcessor, attribute = "make_exists", autospec = True)
	def test_ensure_make_exists_errors(self, mock_make_exists, test_input, return_value, argument_processor):
		"""Test that ensure make exists fails when the input is bad or the make doesn't exist in the database."""
		mock_make_exists.return_value = return_value

		with pytest.raises(CommandError):
			argument_processor.ensure_make_exists(make = test_input)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "make_exists", autospec = True)
	def test_ensure_unique_makes(self, mock_make_exists, argument_processor):
		"""Test that ensure_unique_makes works as expected in the case where the makes don't already exist."""
		mock_make_exists.return_value = False
		mock_makes = ("foo", "bar", "baz")

		argument_processor.ensure_unique_makes(makes = mock_makes)

		assert [call(argument_processor, mock_make) for mock_make in mock_makes] == mock_make_exists.mock_calls

	@pytest.mark.parametrize("test_input, return_value", (([], False), (["", "", ""], False), (["foo", "bar", "baz"], True)))
	@patch.object(target = FirmwareArgumentProcessor, attribute = "make_exists", autospec = True)
	def test_ensure_unique_makes_error(self, mock_make_exists, test_input, return_value, argument_processor):
		"""Test that ensure_unique_makes raises an error if the input is invalid or the makes already exist."""
		mock_make_exists.return_value = return_value

		with pytest.raises(CommandError):
			argument_processor.ensure_unique_makes(makes = test_input)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "make_exists", autospec = True)
	def test_ensure_makes_exist(self, mock_make_exists, argument_processor):
		"""Test that ensure_makes_exist works as expected in the case where the makes already exist."""
		mock_make_exists.return_value = True
		mock_makes = ("foo", "bar", "baz")

		argument_processor.ensure_makes_exist(makes = mock_makes)

		assert [call(argument_processor, mock_make) for mock_make in mock_makes] == mock_make_exists.mock_calls

	@pytest.mark.parametrize("test_input, return_value", (([], True), (["", "", ""], True), (["foo", "bar", "baz"], False)))
	@patch.object(target = FirmwareArgumentProcessor, attribute = "make_exists", autospec = True)
	def test_ensure_makes_exist_error(self, mock_make_exists, test_input, return_value, argument_processor):
		"""Test that ensure_makes_exist raises an error if the input is invalid or one or more makes don't already exist."""
		mock_make_exists.return_value = return_value

		with pytest.raises(CommandError):
			argument_processor.ensure_makes_exist(makes = test_input)

	def test_get_model_id(self, argument_processor):
		"""Test that get model ID works as expected when the make + model exist in the database."""
		argument_processor.db.select.return_value = [[1]]
		mock_make = "foo"
		mock_model = "bar"

		assert argument_processor.db.select.return_value[0][0] == argument_processor.get_model_id(
			make = mock_make,
			model = mock_model,
		)
		argument_processor.db.select.assert_called_once_with(ANY, (mock_make, mock_model))

	def test_get_model_id_error(self, argument_processor):
		"""Test that get model ID fails as expected when the make + model do not exist in the database."""
		argument_processor.db.select.return_value = []
		mock_make = "foo"
		mock_model = "bar"

		with pytest.raises(CommandError):
			argument_processor.get_model_id(make = mock_make, model = mock_model)

	@pytest.mark.parametrize("return_value", (0, 1))
	def test_model_exists(self, return_value, argument_processor):
		"""Test that model exists returns the correct results."""
		mock_make = "foo"
		mock_model = "bar"
		argument_processor.db.count.return_value = return_value

		assert return_value == argument_processor.model_exists(make = mock_make, model = mock_model)
		argument_processor.db.count.assert_called_once_with(ANY, (mock_make, mock_model))

	@patch.object(target = FirmwareArgumentProcessor, attribute = "model_exists", autospec = True)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "ensure_make_exists", autospec = True)
	def test_ensure_model_exists(self, mock_ensure_make_exists, mock_model_exists, argument_processor):
		"""Test that ensure_model_exists works when the make + model both exist."""
		mock_make = "bar"
		mock_model = "foo"

		argument_processor.ensure_model_exists(model = mock_model, make = mock_make)

		mock_ensure_make_exists.assert_called_once_with(argument_processor, make = mock_make)
		mock_model_exists.assert_called_once_with(argument_processor, make = mock_make, model = mock_model)

	@pytest.mark.parametrize(
		"mock_model, side_effect, return_value",
		(
			("", None, True),
			("foo", CommandError(cmd = None, msg = "Test error"), True),
			("foo", None, False),
		)
	)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "model_exists", autospec = True)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "ensure_make_exists", autospec = True)
	def test_ensure_model_exists_errors(
		self,
		mock_ensure_make_exists,
		mock_model_exists,
		mock_model,
		side_effect,
		return_value,
		argument_processor,
	):
		"""Test that ensure_model_exists fails if the input is invalid or when the make + model don't both exist."""
		mock_make = "bar"
		mock_ensure_make_exists.side_effect = side_effect
		mock_model_exists.return_value = return_value

		with pytest.raises(CommandError):
			argument_processor.ensure_model_exists(model = mock_model, make = mock_make)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "model_exists", autospec = True)
	def test_ensure_unique_models(self, mock_model_exists, argument_processor):
		"""Test that ensure_unique_models works as expected when the make + model combinations do not already exist."""
		mock_model_exists.return_value = False
		mock_make = "foo"
		mock_models = ("bar", "baz", "bag")

		argument_processor.ensure_unique_models(make = mock_make, models = mock_models)

		assert [
			call(argument_processor, mock_make, mock_model)
			for mock_model in mock_models
		] == mock_model_exists.mock_calls

	@pytest.mark.parametrize("test_input, return_value", (([], False), (["", "", ""], False), (["foo", "bar", "baz"], True)))
	@patch.object(target = FirmwareArgumentProcessor, attribute = "model_exists", autospec = True)
	def test_ensure_unique_models_error(self, mock_model_exists, test_input, return_value, argument_processor):
		"""Test that ensure_unique_models fails as expected when the inputs are invalid or the make + model combinations already exist."""
		mock_model_exists.return_value = return_value
		mock_make = "foo"

		with pytest.raises(CommandError):
			argument_processor.ensure_unique_models(make = mock_make, models = test_input)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "model_exists", autospec = True)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "ensure_make_exists", autospec = True)
	def test_ensure_models_exist(self, mock_ensure_make_exists, mock_model_exists, argument_processor):
		"""Test that ensure_models_exist works as expected when the make + model combinations already exist."""
		mock_model_exists.return_value = True
		mock_make = "foo"
		mock_models = ("bar", "baz", "bag")

		argument_processor.ensure_models_exist(make = mock_make, models = mock_models)

		mock_ensure_make_exists.assert_called_once_with(argument_processor, make = mock_make)
		assert [
			call(argument_processor, mock_make, mock_model)
			for mock_model in mock_models
		] == mock_model_exists.mock_calls

	@pytest.mark.parametrize(
		"mock_models, side_effect, return_value",
		(
			([], None, True),
			(["", "", ""], None, True),
			(["bar", "baz", "bag"], CommandError(cmd = None, msg = "Test error"), True),
			(["bar", "baz", "bag"], None, False),
		)
	)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "model_exists", autospec = True)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "ensure_make_exists", autospec = True)
	def test_ensure_models_exist_error(
		self,
		mock_ensure_make_exists,
		mock_model_exists,
		mock_models,
		side_effect,
		return_value,
		argument_processor,
	):
		"""Test that ensure_models_exist fails as expected when the make + model combinations do not already exist."""
		mock_ensure_make_exists.side_effect = side_effect
		mock_model_exists.return_value = return_value
		mock_make = "foo"

		with pytest.raises(CommandError):
			argument_processor.ensure_models_exist(make = mock_make, models = mock_models)

	@pytest.mark.parametrize("return_value", (0, 1))
	def test_firmware_exists(self, return_value, argument_processor):
		"""Test that firmware exists returns the correct results."""
		mock_make = "foo"
		mock_model = "bar"
		mock_version = "baz"
		argument_processor.db.count.return_value = return_value

		assert return_value == argument_processor.firmware_exists(
			make = mock_make,
			model = mock_model,
			version = mock_version,
		)
		argument_processor.db.count.assert_called_once_with(ANY, (mock_make, mock_model, mock_version))

	@patch.object(target = FirmwareArgumentProcessor, attribute = "firmware_exists", autospec = True)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "ensure_model_exists", autospec = True)
	def test_ensure_firmware_exists(self, mock_ensure_model_exists, mock_firmware_exists, argument_processor):
		"""Test that ensure_firmware_exists works when the firmware + make + model all exist in the database."""
		mock_firmware_exists.return_value = True
		mock_make = "foo"
		mock_model = "bar"
		mock_version = "baz"

		argument_processor.ensure_firmware_exists(make = mock_make, model = mock_model, version = mock_version)

		mock_ensure_model_exists.assert_called_once_with(
			argument_processor,
			make = mock_make,
			model = mock_model,
		)
		mock_firmware_exists.assert_called_once_with(
			argument_processor,
			make = mock_make,
			model = mock_model,
			version = mock_version,
		)

	@pytest.mark.parametrize(
		"mock_version, side_effect, return_value",
		(
			("", None, True),
			("foo", CommandError(cmd = None, msg = "Test message"), True),
			("foo", None, False),
		)
	)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "firmware_exists", autospec = True)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "ensure_model_exists", autospec = True)
	def test_ensure_firmware_exists_errors(
		self,
		mock_ensure_model_exists,
		mock_firmware_exists,
		mock_version,
		side_effect,
		return_value,
		argument_processor,
	):
		"""Test that ensure_firmware_exists fails when given invalid input or the firmware + make + model do not all exist in the database."""
		mock_firmware_exists.return_value = True
		mock_make = "foo"
		mock_model = "bar"
		mock_ensure_model_exists.side_effect = side_effect
		mock_firmware_exists.return_value = return_value

		with pytest.raises(CommandError):
			argument_processor.ensure_firmware_exists(make = mock_make, model = mock_model, version = mock_version)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "firmware_exists", autospec = True)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "ensure_model_exists", autospec = True)
	def test_ensure_firmwares_exist(self, mock_ensure_model_exists, mock_firmware_exists, argument_processor):
		"""Test that ensure_firmwares_exist works as expected when the firmware files exist for the given make + model."""
		mock_firmware_exists.return_value = True
		mock_make = "foo"
		mock_model = "bar"
		mock_versions = ("baz", "bag", "boo")

		argument_processor.ensure_firmwares_exist(
			make = mock_make,
			model = mock_model,
			versions = mock_versions,
		)

		mock_ensure_model_exists.assert_called_once_with(argument_processor, make = mock_make, model = mock_model)
		assert [
			call(argument_processor, mock_make, mock_model, mock_version)
			for mock_version in mock_versions
		] == mock_firmware_exists.mock_calls

	@pytest.mark.parametrize(
		"mock_versions, side_effect, return_value",
		(
			([], None, True),
			(["", "", ""], None, True),
			(["bar", "baz", "bag"], CommandError(cmd = None, msg = "Test error"), True),
			(["bar", "baz", "bag"], None, False),
		)
	)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "firmware_exists", autospec = True)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "ensure_model_exists", autospec = True)
	def test_ensure_firmwares_exist_errors(
		self,
		mock_ensure_model_exists,
		mock_firmware_exists,
		mock_versions,
		side_effect,
		return_value,
		argument_processor,
	):
		"""Test that ensure_firmwares_exist fails as expected when the firmware files don't exist for the given make + model."""
		mock_ensure_model_exists.side_effect = side_effect
		mock_firmware_exists.return_value = return_value
		mock_make = "foo"
		mock_model = "bar"

		with pytest.raises(CommandError):
			argument_processor.ensure_firmwares_exist(
				make = mock_make,
				model = mock_model,
				versions = mock_versions,
			)

	def test_get_firmware_id(self, argument_processor):
		"""Test that get_firmware_id works as expected when the firmware exists."""
		argument_processor.db.select.return_value = [[1]]
		mock_make = "foo"
		mock_model = "bar"
		mock_version = "baz"

		assert argument_processor.db.select.return_value[0][0] == argument_processor.get_firmware_id(
			make = mock_make,
			model = mock_model,
			version = mock_version,
		)
		argument_processor.db.select.assert_called_once_with(ANY, (mock_make, mock_model, mock_version))

	def test_get_firmware_id_error(self, argument_processor):
		"""Test that get_firmware_id works as expected."""
		argument_processor.db.select.return_value = []
		mock_make = "foo"
		mock_model = "bar"
		mock_version = "baz"

		with pytest.raises(CommandError):
			argument_processor.get_firmware_id(
				make = mock_make,
				model = mock_model,
				version = mock_version,
			)

	# Use create = True here because the self.call method comes from the Command class,
	# which the class under test is expected to be mixed in with.
	@patch.object(target = FirmwareArgumentProcessor, attribute = "call", create = True)
	def test_get_common_frontend_ip(self, mock_call, argument_processor):
		"""Test that get_common_frontend_ip gets the expected common frontend IP when the frontend and the target host share a network."""
		mock_hostname = "sd-stacki-mock-backend"
		# Set up the call("list.host.interface") returns, ensuring each separate return value contains one shared network.
		mock_call_return_values = (
			# Mock front end interfaces
			[{"network": "foo", "ip": "1.2.3.4"}, {"network": "bar", "ip": "2.3.4.5"}],
			# Mock other host interfaces
			[{"network": "baz", "ip": "3.4.5.6"}, {"network": "foo", "ip": "1.2.3.10"}],
		)
		mock_call.side_effect = mock_call_return_values

		result = argument_processor.get_common_frontend_ip(hostname = mock_hostname)

		# Make sure the right IP was returned
		assert mock_call_return_values[0][0]["ip"] == result
		# Make sure the list host interface calls happened
		assert mock_call.mock_calls == [
			call(command = "list.host.interface", args = ["a:frontend"]),
			call(command = "list.host.interface", args = [mock_hostname]),
		]

	# Use create = True here because the self.call method comes from the Command class,
	# which the class under test is expected to be mixed in with.
	@patch.object(target = FirmwareArgumentProcessor, attribute = "call", create = True)
	def test_get_common_frontend_ip_no_common_network(self, mock_call, argument_processor):
		"""Test that get_common_frontend_ip fails when there is no common network."""
		mock_hostname = "sd-stacki-mock-backend"
		# Set up the call("list.host.interface") returns, ensuring each separate return value contains no shared networks.
		mock_call_return_values = (
			# Mock front end interfaces
			[{"network": "foo", "ip": "1.2.3.4"}, {"network": "bar", "ip": "2.3.4.5"}],
			# Mock other host interfaces
			[{"network": "baz", "ip": "3.4.5.6"}, {"network": "bag", "ip": "1.2.3.10"}],
		)
		mock_call.side_effect = mock_call_return_values

		with pytest.raises(CommandError):
			argument_processor.get_common_frontend_ip(hostname = mock_hostname)

	# Use create = True here because the self.call method comes from the Command class,
	# which the class under test is expected to be mixed in with.
	@patch.object(target = FirmwareArgumentProcessor, attribute = "call", create = True)
	def test_get_common_frontend_ip_no_interface_ip(self, mock_call, argument_processor):
		"""Test that get_common_frontend_ip fails when there is no IP on the interface on the common network."""
		mock_hostname = "sd-stacki-mock-backend"
		# Set up the call("list.host.interface") returns, ensuring each separate return value contains one shared network.
		mock_call_return_values = (
			# Mock front end interfaces
			[{"network": "foo", "ip": ""}, {"network": "bar", "ip": "2.3.4.5"}],
			# Mock other host interfaces
			[{"network": "baz", "ip": "3.4.5.6"}, {"network": "foo", "ip": "1.2.3.10"}],
		)
		mock_call.side_effect = mock_call_return_values

		with pytest.raises(CommandError):
			argument_processor.get_common_frontend_ip(hostname = mock_hostname)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "get_common_frontend_ip", autospec = True)
	@patch(target = "stack.argument_processors.firmware.Path", autospec = True)
	def test_get_firmware_url(self, mock_path, mock_get_common_frontend_ip, argument_processor):
		"""Test that get_firmware_url returns the correct URL."""
		mock_get_common_frontend_ip.return_value = "1.2.3.4"
		# need to mock out Path.parts.
		mock_path_parts = (
			"/",
			"export",
			"stack",
			"firmware",
			"make",
			"model",
			"file",
		)
		mock_path.return_value.resolve.return_value.parts = mock_path_parts
		expected_path_parts = mock_path_parts[3:]
		expected_path = "/".join(expected_path_parts)
		mock_path.return_value.joinpath.return_value.__str__.return_value = expected_path
		expected_url = f"http://{mock_get_common_frontend_ip.return_value}/install/{expected_path}"
		mock_firmware_file = "foo"
		mock_hostname = "bar"

		result = argument_processor.get_firmware_url(
			hostname = mock_hostname,
			firmware_file = mock_firmware_file,
		)

		# Make sure the returned URL is correct.
		assert expected_url == result
		# Check that the path was resolved.
		assert all(
			call in mock_path.mock_calls
			for call in call(mock_firmware_file).resolve(strict = True).call_list()
		)
		# Make sure the IP was retrieved
		mock_get_common_frontend_ip.assert_called_once_with(argument_processor, hostname = mock_hostname)
		# Make sure the path was rebuilt excluding the right elements
		mock_path.return_value.joinpath.assert_called_once_with(*expected_path_parts)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "get_common_frontend_ip", autospec = True)
	@patch(target = "stack.argument_processors.firmware.Path", autospec = True)
	def test_get_firmware_url_file_does_not_exist(self, mock_path, mock_get_common_frontend_ip, argument_processor):
		"""Test that get_firmware_url raises a CommandError if the firmware file does not exist."""
		mock_path.return_value.resolve.side_effect = FileNotFoundError("Test error")

		with pytest.raises(CommandError):
			argument_processor.get_firmware_url(
				hostname = "foo",
				firmware_file = "bar",
			)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "get_common_frontend_ip", autospec = True)
	@patch(target = "stack.argument_processors.firmware.Path", autospec = True)
	def test_get_firmware_url_no_common_ip(self, mock_path, mock_get_common_frontend_ip, argument_processor):
		"""Test that get_firmware_url passes through the CommandError if get_common_frontend_ip fails."""
		mock_get_common_frontend_ip.side_effect = CommandError(cmd = "", msg = "Test error")

		with pytest.raises(CommandError):
			argument_processor.get_firmware_url(
				hostname = "foo",
				firmware_file = "bar",
			)

	@pytest.mark.parametrize("return_value", (0, 1))
	def test_imp_exists(self, return_value, argument_processor):
		"""Test that imp_exists works as expected."""
		mock_imp = "foo"
		argument_processor.db.count.return_value = return_value

		assert return_value == argument_processor.imp_exists(imp = mock_imp)
		argument_processor.db.count.assert_called_once_with(ANY, mock_imp)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "imp_exists", autospec = True)
	def test_ensure_imp_exists(self, mock_imp_exists, argument_processor):
		"""Test that ensure_imp_exists works when the input is valid and the imp exists in the database."""
		mock_imp = "foo"
		mock_imp_exists.return_value = True

		argument_processor.ensure_imp_exists(imp = mock_imp)

		mock_imp_exists.assert_called_once_with(argument_processor, imp = mock_imp)

	@pytest.mark.parametrize("mock_imp, return_value", (("", True), ("foo", False)))
	@patch.object(target = FirmwareArgumentProcessor, attribute = "imp_exists", autospec = True)
	def test_ensure_imp_exists_errors(self, mock_imp_exists, mock_imp, return_value, argument_processor):
		"""Test that ensure_imp_exists fails when the input is invalid or the imp does not exist in the database."""
		mock_imp_exists.return_value = return_value

		with pytest.raises(CommandError):
			argument_processor.ensure_imp_exists(imp = mock_imp)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "imp_exists", autospec = True)
	def test_ensure_imps_exist(self, mock_imp_exists, argument_processor):
		"""Test that ensure_imps_exist works as expected when all implementations exist in the database."""
		mock_imp_exists.return_value = True
		mock_imps = ("foo", "bar", "baz")

		argument_processor.ensure_imps_exist(imps = mock_imps)

		assert [call(argument_processor, mock_imp) for mock_imp in mock_imps] == mock_imp_exists.mock_calls

	@pytest.mark.parametrize(
		"mock_imps, return_value",
		(
			([], True),
			(["", "", ""], True),
			(["bar", "baz", "bag"], False),
		)
	)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "imp_exists", autospec = True)
	def test_ensure_imps_exist_error(
		self,
		mock_imp_exists,
		mock_imps,
		return_value,
		argument_processor,
	):
		"""Test that ensure_imps_exist fails when at least one implementation doesn't exist in the database."""
		mock_imp_exists.return_value = return_value

		with pytest.raises(CommandError):
			argument_processor.ensure_imps_exist(imps = mock_imps)

	def test_get_imp_id(self, argument_processor):
		"""Test that get_imp_id works as expected when the implementation exists in the database."""
		argument_processor.db.select.return_value = [[1]]
		mock_imp = "foo"

		assert argument_processor.db.select.return_value[0][0] == argument_processor.get_imp_id(
			imp = mock_imp,
		)
		argument_processor.db.select.assert_called_once_with(ANY, mock_imp)

	def test_get_imp_id_error(self, argument_processor):
		"""Test that get_imp_id fails as expected when the implementation does not exist in the database."""
		argument_processor.db.select.return_value = []
		mock_imp = "foo"

		with pytest.raises(CommandError):
			argument_processor.get_imp_id(imp = mock_imp)

	@pytest.mark.parametrize("return_value", (0, 1))
	def test_version_regex_exists(self, return_value, argument_processor):
		"""Test that version_regex_exists works as expected."""
		argument_processor.db.count.return_value = return_value
		mock_name = "foo"

		assert return_value == argument_processor.version_regex_exists(name = mock_name)
		argument_processor.db.count.assert_called_once_with(ANY, mock_name)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "version_regex_exists", autospec = True)
	def test_ensure_version_regex_exists(self, mock_version_regex_exists, argument_processor):
		"""Test that ensure_version_regex_exists works in the case where the input is valid and the version regex exists in the database."""
		mock_version_regex_exists.return_value = True
		mock_name = "foo"

		argument_processor.ensure_version_regex_exists(name = mock_name)

		mock_version_regex_exists.assert_called_once_with(argument_processor, name = mock_name)

	@pytest.mark.parametrize("mock_name, return_value", (("", True), ("foo", False)))
	@patch.object(target = FirmwareArgumentProcessor, attribute = "version_regex_exists", autospec = True)
	def test_ensure_version_regex_exists_errors(self, mock_version_regex_exists, mock_name, return_value, argument_processor):
		"""Test that ensure_version_regex_exists works in the case where the input is valid and the version regex exists in the database."""
		mock_version_regex_exists.return_value = return_value

		with pytest.raises(CommandError):
			argument_processor.ensure_version_regex_exists(name = mock_name)

	@patch.object(target = FirmwareArgumentProcessor, attribute = "version_regex_exists", autospec = True)
	def test_ensure_version_regexes_exist(self, mock_version_regex_exists, argument_processor):
		"""Test that ensure_version_regexes_exist works in the case where all the version regexes exist in the database."""
		mock_version_regex_exists.return_value = True
		mock_names = ("foo", "bar", "baz")

		argument_processor.ensure_version_regexes_exist(names = mock_names)

		assert [call(argument_processor, mock_name) for mock_name in mock_names] == mock_version_regex_exists.mock_calls

	@pytest.mark.parametrize(
		"mock_names, return_value",
		(
			([], True),
			(["", "", ""], True),
			(["bar", "baz", "bag"], False),
		)
	)
	@patch.object(target = FirmwareArgumentProcessor, attribute = "version_regex_exists", autospec = True)
	def test_ensure_version_regexes_exist_error(self, mock_version_regex_exists, mock_names, return_value, argument_processor):
		"""Test that ensure_version_regexes_exist fails in the case where at least one of the version regexes does not exist in the database."""
		mock_version_regex_exists.return_value = return_value

		with pytest.raises(CommandError):
			argument_processor.ensure_version_regexes_exist(names = mock_names)

	def test_get_version_regex_id(self, argument_processor):
		"""Test that get_version_regex_id works as expected when the version_regex exists in the database."""
		argument_processor.db.select.return_value = [[1]]
		mock_name = "foo"

		assert argument_processor.db.select.return_value[0][0] == argument_processor.get_version_regex_id(
			name = mock_name,
		)
		argument_processor.db.select.assert_called_once_with(ANY, mock_name)

	def test_get_version_regex_id_error(self, argument_processor):
		"""Test that get_version_regex_id fails as expected when the version_regex does not exist in the database."""
		argument_processor.db.select.return_value = []
		mock_name = "foo"

		with pytest.raises(CommandError):
			argument_processor.get_version_regex_id(name = mock_name)

	@pytest.mark.parametrize(
		"test_input, expected",
		(
			(
				[[None, None, None, "mock_model_regex", "mock_model_regex_name", "mock_model_regex_description"]],
				("mock_model_regex", "mock_model_regex_name", "mock_model_regex_description"),
			),
			(
				[["mock_make_regex", "mock_make_regex_name", "mock_make_regex_description", None, None, None,]],
				("mock_make_regex", "mock_make_regex_name", "mock_make_regex_description"),
			),
			(
				[["mock_make_regex", "mock_make_regex_name", "mock_make_regex_description", "mock_model_regex", "mock_model_regex_name", "mock_model_regex_description"]],
				("mock_model_regex", "mock_model_regex_name", "mock_model_regex_description"),
			),
			([], None),
		)
	)
	def test_try_get_version_regex(self, test_input, expected, argument_processor):
		"""Test that try_get_version_regex works as expected, preferring a model regex over a make one."""
		argument_processor.db.select.return_value = test_input
		mock_make = "foo"
		mock_model = "bar"

		# Make sure the expected result is returned.
		assert expected == argument_processor.try_get_version_regex(
			make = mock_make,
			model = mock_model,
		)
		argument_processor.db.select.assert_called_once_with(ANY, (mock_make, mock_model))
