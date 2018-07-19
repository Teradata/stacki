import pytest

def test_list_switch_support(host):
	result = host.run('stack list switch support')
	assert result.rc == 0
