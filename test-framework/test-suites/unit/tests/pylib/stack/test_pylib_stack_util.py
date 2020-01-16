import pytest
import stack.util
import subprocess
from unittest.mock import create_autospec, patch, call
from pathlib import Path

class TestUtil:
	def test_exec_wrapper(self):
		_exec = stack.util._exec

		# by default, we get stdout decoded as a string
		results = _exec('whoami')
		assert results.returncode == 0
		assert results.stdout.strip() == 'root'
		assert results.stderr == ''

		# but we can disable it
		results = _exec('whoami', stdout=None)
		assert results.returncode == 0
		assert results.stdout == None
		assert results.stderr == ''

		# we can disable the encoding
		results = _exec('whoami', encoding=None)
		assert results.returncode == 0
		assert results.stdout.strip() == b'root'
		assert results.stderr == b''

		# and we have stderr
		results = _exec(['whoami', '-???'])
		assert results.returncode != 0
		assert results.stdout == ''
		assert results.stderr != ''

		# and optional shlex-based string splitting
		results = _exec('whoami -???', shlexsplit=True)
		assert results.returncode != 0
		assert results.stdout == ''
		assert results.stderr != ''

		# we can use shell=True
		results = _exec('echo $USER', shell=True)
		assert results.returncode == 0
		assert results.stdout.strip() == 'root'
		assert results.stderr == ''

		# and shell features
		results = _exec('echo $USER | rev && date', shell=True)
		assert results.returncode == 0
		assert results.stdout.strip().startswith('toor')
		assert results.stderr == ''

		# we can pass in text to SDTIN
		results = _exec('cat', input='a string')
		assert results.returncode == 0
		assert results.stdout.strip() == 'a string'
		assert results.stderr == ''

		# and you can change directories
		results = _exec('echo $PWD', shell=True, cwd='/export')
		assert results.returncode == 0
		assert results.stdout.strip() == '/export'
		assert results.stderr == ''

		# or redirect stderr to stdout
		results = _exec('whoami -???', shlexsplit=True, stderr=subprocess.STDOUT)
		assert results.returncode != 0
		assert results.stdout.strip() != ''
		assert results.stderr == None

		# or redirect to /dev/null
		results = _exec('whoami -???', shlexsplit=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
		assert results.returncode != 0
		assert results.stdout == None
		assert results.stderr == None

		# unknown commands still error
		with pytest.raises(FileNotFoundError):
			_exec('whodis')

	@pytest.mark.parametrize(
		"key, test_input, expected",
		(
			(None, ("a", "a", "b", "a", "c"), ("a", "b", "c")),
			(None, ("b", "a", "a", "a", "c"), ("b", "a", "c")),
			(None, ("b", "c", "a", "a", "a"), ("b", "c", "a")),
			(str.lower, ("a", "A", "b", "A", "c"), ("a", "b", "c")),
			(str.lower, ("b", "a", "A", "A", "c"), ("b", "a", "c")),
			(str.lower, ("b", "c", "a", "A", "a"), ("b", "c", "a")),
		)
	)
	def test_unique_everseen(self, key, test_input, expected):
		"""Test that duplicates are removed and order is preserved."""
		assert expected == tuple(stack.util.unique_everseen(test_input, key = key))

	def test_lowered(self):
		"""Expect lowered to lowercase all strings in an interable."""
		assert ["foo", "bar", "baz"] == list(stack.util.lowered(["FOO", "BAR", "BAZ"]))

	def test_is_valid_hostname(self):
		assert stack.util.is_valid_hostname("backend-0-0")
		assert stack.util.is_valid_hostname("a")
		assert not stack.util.is_valid_hostname("")

		assert not stack.util.is_valid_hostname("-no-leading-minus")
		assert not stack.util.is_valid_hostname("no-trailing-minus-")
		assert not stack.util.is_valid_hostname("no.other_chars")

		max_len_name = "a" * 63
		assert stack.util.is_valid_hostname(max_len_name)
		longer_name = "a" * 64
		assert not stack.util.is_valid_hostname(longer_name)

	def exec_return_code(self, mock_completed_process, mock_calls, *args, **kwargs):
		"""
		Helper function for giving different
		return codes for _exec based on the input args
		"""
		mock_completed_process.returncode = 1

		# Return a successful return code if the input
		# dict specifies it for the call to _exec
		for arg_text, success in mock_calls.items():
			if arg_text in args[0]:
				if success:
					mock_completed_process.returncode = 0
		return mock_completed_process

	# Test various scenarios of transferring files:
	# 1. Transfer a tar gz archive
	# 2. Transfer a tar bz2 archive
	# 3. Transfer a tar gz archive that is already
	#	 present on the remote host, which
	#    shouldn't be overwritten
	# 4. Transfer a gzipped file
	# 5. Transfer an uncompressed file
	COPY_FILE_VALUES = [
	('foo.tar.gz',
		{
			'ssh baz "mkdir -p bar"': True,
			'ssh baz "ls bar/qux"': False,
			'scp foo.tar.gz baz:bar': True,
			'ssh baz "tar -xvf bar/foo.tar.gz -C bar && rm bar/foo.tar.gz"': True
		}
	),
	('foo.tar.bz2',
		{
			'ssh baz "mkdir -p bar"': True,
			'ssh baz "ls bar/qux"': False,
			'scp foo.tar.bz2 baz:bar': True,
			'ssh baz "tar -xvf bar/foo.tar.bz2 -C bar && rm bar/foo.tar.bz2"': True
		}
	),
	('foo.tar.gz',
		{
			'ssh baz "mkdir -p bar"': True,
			'ssh baz "ls bar/qux"': True
		}
	),
	('foo.gz',
		{
			'ssh baz "mkdir -p bar"': True,
			'ssh baz "ls bar/qux"': False,
			'scp foo.gz baz:bar': True,
			'ssh baz "gunzip bar/foo.gz"': True
		}
	),
	('foo.qcow2',
		{
			'ssh baz "mkdir -p bar"': True,
			'ssh baz "ls bar/qux"': False,
			'scp foo.qcow2 baz:bar': True
		}
	)
	]
	@patch('pathlib.Path.is_file', autospec=True)
	@patch('tarfile.is_tarfile', autospec=True)
	@patch('stack.util._exec', autospec=True)
	@patch('subprocess.CompletedProcess', autospec=True)
	@pytest.mark.parametrize('file_name, exec_args', COPY_FILE_VALUES)
	@pytest.mark.parametrize('uncompress', [True, False])
	def test_remote_copy_image(
		self,
		mock_completed_process,
		mock_exec,
		mock_is_tarfile,
		mock_is_file,
		file_name,
		exec_args,
		uncompress
	):
		mock_is_file.return_value = True
		mock_completed_process.stderr = 'Error!'
		if 'tar' in file_name:
			mock_is_tarfile.return_value = True
		else:
			mock_is_tarfile.return_value = False

		# Call a helper function to assign the desired
		# return code values for each arg to _exec
		mock_exec.side_effect = lambda *args, **kwargs: self.exec_return_code(mock_completed_process, exec_args, *args, **kwargs)
		stack.util.copy_remote_file(file_name, 'bar', 'baz', uncompress_file_name = 'qux')

		# Only if we have at least 3 calls to _exec
		# will tarfile.is_tarfile be called, so only
		# assert it has been called then
		if len(exec_args) >= 3:
			mock_is_tarfile.assert_called_once_with(Path(f'bar/{file_name}'))

		mock_is_file.assert_called_once_with(Path(file_name))

		if uncompress:
			expected_calls = [call(c, shlexsplit=True) for c in exec_args.keys()]

		# No calls to gzip or tar should be in _exec's args
		# since uncompress is False
		else:
			expected_calls = [call(c, shlexsplit=True) for c in exec_args.keys() if 'gzip' not in c or 'tar' not in c]
		assert expected_calls == mock_exec.call_args_list

	# Test copy_remote_file raises exceptions when:
	# 1. The destination folder could not be created
	# 2. Could not copy over a file
	# 3. Failing to unpack a tar archive
	# 4. Failing to unpack a gzip archive
	COPY_FILE_EXCEPTIONS = [
	('foo.tar.gz',
		{
			'ssh baz "mkdir -p bar"': False,
		},
	'Could not create file folder bar on baz:\nError!'
	),
	('foo.tar.gz',
		{
			'ssh baz "mkdir -p bar"': True,
			'ssh baz "ls bar/qux"': False,
			'scp foo.tar.gz baz:bar': False
		},
		'Failed to transfer file foo.tar.gz to baz at bar/foo.tar.gz:\nError!'
	),
	('foo.tar.gz',
		{
			'ssh baz "mkdir -p bar"': True,
			'ssh baz "ls bar/qux"': False,
			'scp foo.tar.gz baz:bar': True,
			'ssh baz "tar -xvf bar/foo.tar.gz -C bar && rm bar/foo.tar.gz"': False
		},
		'Failed to unpack file archive foo.tar.gz on baz:\nError!'
	),
	('foo.gz',
		{
			'ssh baz "mkdir -p bar"': True,
			'ssh baz "ls bar/qux"': False,
			'scp foo.gz baz:bar': True,
			'ssh baz "gunzip bar/foo.gz"': False
		},
		'Failed to unpack file foo.gz on baz:\nError!'
	)
	]

	@patch('pathlib.Path.is_file', autospec=True)
	@patch('tarfile.is_tarfile', autospec=True)
	@patch('stack.util._exec', autospec=True)
	@patch('subprocess.CompletedProcess', autospec=True)
	@pytest.mark.parametrize('file_name, exec_args, except_msg', COPY_FILE_EXCEPTIONS)
	@pytest.mark.parametrize('is_file', [True, False])
	def test_remote_copy_image_exception(
		self,
		mock_completed_process,
		mock_exec,
		mock_is_tarfile,
		mock_is_file,
		file_name,
		exec_args,
		except_msg,
		is_file
	):
		mock_is_file.return_value = is_file
		mock_completed_process.stderr = 'Error!'

		if 'tar' in file_name:
			mock_is_tarfile.return_value = True
		else:
			mock_is_tarfile.return_value = False

		# Call a helper function to assign the desired
		# return code values for each arg to _exec
		mock_exec.side_effect = lambda *args, **kwargs: self.exec_return_code(mock_completed_process, exec_args, *args, **kwargs)

		# Check less functions were called
		# when we fail if the input file
		# doesn't exist on the file system
		if is_file:
			with pytest.raises(OSError, match = except_msg):
				stack.util.copy_remote_file(file_name, 'bar', 'baz', uncompress_file_name = 'qux')
				mock_is_tarfile.assert_called_once_with(Path(f'bar/{file_name}'))
				mock_is_file.assert_called_once_with(file_name)

				# Check calls match
				expected_calls = [call(c, shlexsplit=True) for c in exec_args.keys()]
				assert expected_calls == mock_exec.call_args_list
		else:
			with pytest.raises(OSError, match = f'File {file_name} not found to transfer'):
				stack.util.copy_remote_file(file_name, 'bar', 'baz', uncompress_file_name = 'qux')
				mock_is_file.assert_called_once_with(file_name)

	@patch('stack.util._exec', autospec=True)
	@patch('subprocess.CompletedProcess', autospec=True)
	def test_remote_remove_file(self, mock_completed_process, mock_exec):
		mock_completed_process.returncode = 0
		mock_completed_process.stderr = 'Error!'
		mock_exec.return_value = mock_completed_process

		stack.util.remove_remote_file('foo', 'bar')

		expected_calls = [
			call('ssh bar "ls foo"', shlexsplit=True),
			call('ssh bar "rm foo"', shlexsplit=True)
		]

		# Check all the calls to _exec match
		assert expected_calls == mock_exec.call_args_list

	# Test exceptions are raised for removing remote files when:
	# 1. The file doesn't exist on the remote host
	# 2. Removing the file fails
	REMOVE_FILE_EXCEPT_INPUT = [
		(
			{
				'ssh bar "ls foo"': False,
			},
			'Could not find file foo on bar'
		),
		(
			{
				'ssh bar "ls foo"': True,
				'ssh bar "rm foo"': False
			},
			'Failed to remove file foo:Error!'
		)
	]
	@patch('stack.util._exec', autospec=True)
	@patch('subprocess.CompletedProcess', autospec=True)
	@pytest.mark.parametrize('exec_args, except_msg', REMOVE_FILE_EXCEPT_INPUT)
	def test_remote_remove_file_exeception(
		self,
		mock_completed_process,
		mock_exec,
		exec_args,
		except_msg
	):

		# Call a helper function to assign the desired
		# return code values for each arg to _exec
		mock_exec.side_effect = lambda *args, **kwargs: self.exec_return_code(mock_completed_process, exec_args, *args, **kwargs)
		mock_completed_process.stderr = 'Error!'

		with pytest.raises(OSError, match = except_msg):
			stack.util.remove_remote_file('foo', 'bar')

			# The calls should match what we expect
			expected_calls = [call(c, shlexsplit=True) for c in exec_args.keys()]
			assert expected_calls == mock_exec.call_args_list
