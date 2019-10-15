import json


class TestListAttrDoc:
	def test_list_all(self, host):
		# Add a test attr
		result = host.run('stack set attr attr=test value=True')
		assert result.rc == 0

		# Set the doc for it
		result = host.run('stack set attr doc attr=test doc=foo')
		assert result.rc == 0

		# Make sure it there
		result = host.run('stack list attr doc output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'doc': 'foo'
		}]

	def test_list_with_blob(self, host):
		# Add a test attr
		result = host.run('stack set attr attr=test value=True')
		assert result.rc == 0

		# Set the doc for it
		result = host.run('stack set attr doc attr=test doc=foo')
		assert result.rc == 0

		# Make sure it there
		result = host.run('stack list attr doc attr="t*" output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'doc': 'foo'
		}]
