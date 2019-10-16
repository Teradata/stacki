import pytest

import stack.bool

TRUTHY_STRINGS = [
	'yes',
	'y',
	'1',
	'true',
	'on',
]

FALSEY_STRINGS = [
	'literally anything else',
	't',
	'no',
	'f',
	'false',
	'off',
	'tiger'
	'foo',
	'0',
	'',
]

class TestBool:
	@pytest.mark.parametrize('input_str', TRUTHY_STRINGS)
	def test_str2bool_truthy_strings(self, input_str):
		''' test different strings expected to be True '''
		assert stack.bool.str2bool(input_str) is True
		assert stack.bool.str2bool(input_str.upper()) is True

	@pytest.mark.parametrize('input_str', FALSEY_STRINGS)
	def test_str2bool_falsey_strings(self, input_str):
		''' test different strings expected to be False'''
		assert stack.bool.str2bool(input_str) is False
		assert stack.bool.str2bool(input_str.upper()) is False

	def test_str2bool_of_bool(self):
		''' test that str2bool is a passthrough for already boolean values '''
		assert stack.bool.str2bool(True) is True
		assert stack.bool.str2bool(False) is False

	def test_str2bool_of_falsey_values(self):
		''' test that str2bool is a passthrough for already boolean values '''
		assert stack.bool.str2bool(0) is False
		assert stack.bool.str2bool(None) is False
		assert stack.bool.str2bool([]) is False

	def test_str2bool_of_bad_data(self):
		''' str2bool makes no attempts at datatypes that aren't bool or don't have .upper() '''
		with pytest.raises(AttributeError):
			stack.bool.str2bool(1)
		with pytest.raises(AttributeError):
			stack.bool.str2bool([False])

	def test_bool2str(self):
		''' bool2str only operates on ints and bools '''
		assert stack.bool.bool2str(True) == 'yes'
		assert stack.bool.bool2str(1) == 'yes'
		assert stack.bool.bool2str(False) == 'no'
		assert stack.bool.bool2str(0) == 'no'

		# bool2str(x > 1) is also 'yes'
		assert stack.bool.bool2str(2) == 'yes'

		# bool2str of any other datatype is None
		assert stack.bool.bool2str('Foo') is None
		assert stack.bool.bool2str('True') is None
		assert stack.bool.bool2str('1') is None

	def test_bool2str_of_str2bool(self):
		''' hey it happens '''
		assert stack.bool.bool2str(stack.bool.str2bool('True')) == 'yes'
		assert stack.bool.bool2str(stack.bool.str2bool('False')) == 'no'
