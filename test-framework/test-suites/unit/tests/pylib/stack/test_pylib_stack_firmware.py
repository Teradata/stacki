from unittest.mock import patch, call
import hashlib
import pytest
import stack.download
import stack.firmware

class TestSupportedSchemes:
	"""A test case for the schemes enum logic."""

	def test_pretty_string(self):
		"""Ensure pretty_string works as expected."""
		assert ", ".join(
			stack.firmware.SUPPORTED_SCHEMES.__members__.keys()
		) == stack.firmware.SUPPORTED_SCHEMES.pretty_string()

	@pytest.mark.parametrize("scheme", stack.firmware.SUPPORTED_SCHEMES)
	def test__str__(self, scheme):
		"""Ensure the __str__ for each enum instance works as expected."""
		assert scheme.name == str(scheme)

class TestFirmware:
	"""A test case to hold the tests for the firmware utilities."""

	@pytest.mark.parametrize("hash_alg", stack.firmware.SUPPORTED_HASH_ALGS)
	@patch(target = "stack.firmware.Path", autospec = True)
	def test_calculate_hash(self, mock_path, hash_alg):
		"""Test that calculate_hash works for all supported hash types."""
		mock_path.return_value.read_bytes.return_value = b"bar"

		try:
			expected_hash = hashlib.new(
				name = hash_alg,
				data = mock_path.return_value.read_bytes.return_value
			).hexdigest()
		except TypeError:
			# Need to handle shake_128 and shake_256 case where a digest length is required.
			expected_hash = hashlib.new(
				name = hash_alg,
				data = mock_path.return_value.read_bytes.return_value
			).hexdigest(256)

		# Call providing the expected hash
		mock_file = "foo"
		assert expected_hash == stack.firmware.calculate_hash(
			file_path = mock_file,
			hash_alg = hash_alg,
			hash_value = expected_hash,
		)
		# Expect the path to be used to read the file
		mock_path.assert_called_once_with(mock_file)
		mock_path.return_value.read_bytes.assert_called_once_with()

		# Reset mocks for the next set of assertions
		mock_path.reset_mock()
		# Call without providing the expected hash
		assert expected_hash == stack.firmware.calculate_hash(
			file_path = mock_file,
			hash_alg = hash_alg,
		)
		# Expect the path to be used to read the file
		mock_path.assert_called_once_with(mock_file)
		mock_path.return_value.read_bytes.assert_called_once_with()

	@pytest.mark.parametrize("hash_alg", stack.firmware.SUPPORTED_HASH_ALGS)
	@patch(target = "stack.firmware.Path", autospec = True)
	def test_calculate_hash_mismatched_provided_hash(self, mock_path, hash_alg):
		"""Test that calculate_hash fails if the provided hash doesn't match the calculated one."""
		mock_path.return_value.read_bytes.return_value = b"bar"

		with pytest.raises(stack.firmware.FirmwareError):
			stack.firmware.calculate_hash(
				file_path = "foo",
				hash_alg = hash_alg,
				hash_value = "foo",
			)

	@patch(target = "stack.firmware.Path", autospec = True)
	def test_calculate_hash_unsupported_hash(self, mock_path):
		"""Test that calculate_hash fails if the provided hash_alg isn't supported."""
		mock_path.return_value.read_bytes.return_value = b"bar"

		with pytest.raises(stack.firmware.FirmwareError):
			stack.firmware.calculate_hash(
				file_path = "foo",
				hash_alg = "foo",
			)

	@pytest.mark.parametrize("scheme", stack.firmware.SUPPORTED_SCHEMES)
	@patch(target = "uuid.uuid4", autospec = True)
	@patch(target = "stack.firmware.Path", autospec = True)
	@patch(target = "stack.firmware.BASE_PATH", autospec = True)
	@patch(target = "stack.download.fetch", autospec = True)
	def test_fetch_firmware(self, mock_fetch, mock_base_path, mock_path, mock_uuid4, scheme):
		"""Test that fetch_firmware works as expected for each supported scheme."""
		mock_url = f"{scheme}://localhost/foo/bar"
		mock_make = "foo"
		mock_model = "bar"
		mock_username = "baz"

		result = stack.firmware.fetch_firmware(
			source = mock_url,
			make = mock_make,
			model = mock_model,
			username = mock_username,
		)

		# Make sure base_dir is used to properly build the target directory
		chained_calls = call.__truediv__(mock_make).__truediv__(mock_model).resolve().mkdir(parents = True, exist_ok = True)
		call_list = chained_calls.call_list()
		call_list.append(call.__truediv__().__truediv__().resolve().__truediv__(mock_uuid4.return_value.hex))
		assert all(mock_call in mock_base_path.mock_calls for mock_call in call_list)
		# Make sure the final file is built using the hex uuid4
		mock_base_path.__truediv__.return_value.__truediv__.return_value.resolve.return_value.__truediv__.assert_called_once_with(
			mock_uuid4.return_value.hex
		)
		mock_final_file = mock_base_path.__truediv__.return_value.__truediv__.return_value.resolve.return_value.__truediv__.return_value
		# Make sure the returned file is the final file
		assert mock_final_file == result

		# We make assertions based on the scheme in use.
		if scheme == stack.firmware.SUPPORTED_SCHEMES.file:
			# Ensure the file was constructed using the url path
			mock_path.assert_called_once_with("/foo/bar")
			mock_path.return_value.resolve.assert_called_once_with(strict = True)
			# Make sure the final file is written
			mock_final_file.write_bytes.assert_called_once_with(
				mock_path.return_value.resolve.return_value.read_bytes.return_value
			)

		elif scheme in (stack.firmware.SUPPORTED_SCHEMES.http, stack.firmware.SUPPORTED_SCHEMES.https):
			# Ensure the source was downloaded
			mock_fetch.assert_called_once_with(
				url = mock_url,
				file_path = mock_final_file,
				verbose = True,
				username = mock_username,
			)

	@pytest.mark.parametrize("scheme", stack.firmware.SUPPORTED_SCHEMES)
	@patch(target = "uuid.uuid4", autospec = True)
	@patch(target = "stack.firmware.Path", autospec = True)
	@patch(target = "stack.firmware.BASE_PATH", autospec = True)
	@patch(target = "stack.download.fetch", autospec = True)
	def test_fetch_firmware_errors(self, mock_fetch, mock_base_path, mock_path, mock_uuid4, scheme):
		"""Test that fetch_firmware fails as expected for each supported scheme when fetching from the source fails."""
		mock_url = f"{scheme}://localhost/foo/bar"
		mock_make = "foo"
		mock_model = "bar"

		# Set up exceptions
		mock_path.return_value.resolve.side_effect = FileNotFoundError("Test error")
		mock_fetch.side_effect = stack.download.FetchError("Test error")

		with pytest.raises(stack.firmware.FirmwareError):
			stack.firmware.fetch_firmware(
				source = mock_url,
				make = mock_make,
				model = mock_model,
			)

	@patch(target = "uuid.uuid4", autospec = True)
	@patch(target = "stack.firmware.Path", autospec = True)
	@patch(target = "stack.firmware.BASE_PATH", autospec = True)
	@patch(target = "stack.download.fetch", autospec = True)
	def test_fetch_firmware_unsupoorted_scheme(self, mock_fetch, mock_base_path, mock_path, mock_uuid4):
		"""Test that fetch_firmware fails when given an unsupported scheme."""
		mock_url = f"baz://localhost/foo/bar"
		mock_make = "foo"
		mock_model = "bar"

		with pytest.raises(stack.firmware.FirmwareError):
			stack.firmware.fetch_firmware(
				source = mock_url,
				make = mock_make,
				model = mock_model,
			)

	@patch(target = "stack.firmware.SUPPORTED_SCHEMES")
	@patch(target = "uuid.uuid4", autospec = True)
	@patch(target = "stack.firmware.Path", autospec = True)
	@patch(target = "stack.firmware.BASE_PATH", autospec = True)
	@patch(target = "stack.download.fetch", autospec = True)
	def test_fetch_firmware_forgotten_scheme(self, mock_fetch, mock_base_path, mock_path, mock_uuid4, mock_schemes):
		"""Test that fetch_firmware fails when a case is not added to handle a supported scheme."""
		mock_url = f"baz://localhost/foo/bar"
		mock_make = "foo"
		mock_model = "bar"
		mock_schemes.__getitem__.return_value = "baz"

		with pytest.raises(RuntimeError):
			stack.firmware.fetch_firmware(
				source = mock_url,
				make = mock_make,
				model = mock_model,
			)
