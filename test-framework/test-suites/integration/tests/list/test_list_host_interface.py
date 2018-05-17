import json
import pytest

def test_list_host_interface(host):
	# check that we have the correct interfaces expected
	result = host.run("stack list host attr localhost attr='Ignore_Nics' output-format=json")
	# If we have an older frontend-install.py we get a blanks string
	if result.stdout == '':
		# It defaults to False, so we will follow that path
		ignore_nics = False
	else:
		# Otherwise utilize the attribute ouptut
		my_json = json.loads(result.stdout)
		ignore_nics = my_json[0]['value'] == 'True'
	result = host.run('stack list host interface')
	local_interface_count = len(result.stdout.splitlines())
	assert result.rc == 0
	if ignore_nics == True:
		# Ignoring Nics only adds the private interface, plus the line for headers
		assert len(result.stdout.splitlines()) == 2
	else:
		# Find all the interfaces on the frontend
		# /sys/class/net/lo gets counted, but that offsets the header anyways
		result = host.run("find /sys/class/net/* -maxdepth 0 | wc -l")
		assert result.rc == 0
		assert local_interface_count == int(result.stdout)

