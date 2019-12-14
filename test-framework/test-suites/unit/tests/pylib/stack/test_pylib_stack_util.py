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
