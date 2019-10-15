import json


class TestRemoveOSAttr:
	def test_add_and_remove(self, host, host_os):
		# Add a test attr
		result = host.run(f'stack set os attr {host_os} attr=test value=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run(f'stack list os attr {host_os} attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'os': host_os,
			'scope': 'os',
			'type': 'var',
			'value': 'True'
		}]

		# Now remove it
		result = host.run(f'stack remove os attr {host_os} attr=test')
		assert result.rc == 0

		# Make sure it got removed
		result = host.run(f'stack list os attr {host_os} attr=test')
		assert result.rc == 0
		assert result.stdout == ''
