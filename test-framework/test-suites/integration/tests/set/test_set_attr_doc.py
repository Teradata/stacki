import json


class TestSetAttrDoc:
	def test_not_existing(self, host):
		# Set the doc for a non-existing attr
		result = host.run('stack set attr doc attr=test doc=foo')
		assert result.rc == 255
		assert result.stderr == "error - Cannot set documentation for a non-existant attribute\n"

	def test_set_and_update(self, host):
		# Add a test attr
		result = host.run('stack set attr attr=test value=True')
		assert result.rc == 0

		# Set the doc for it
		result = host.run('stack set attr doc attr=test doc=foo')
		assert result.rc == 0

		# Make sure it there
		result = host.run('stack list attr doc attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'doc': 'foo'
		}]

		# Now change the doc
		result = host.run('stack set attr doc attr=test doc=bar')
		assert result.rc == 0

		# Make sure it got updated
		result = host.run('stack list attr doc attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'doc': 'bar'
		}]

	def test_set_and_delete(self, host):
		# Add a test attr
		result = host.run('stack set attr attr=test value=True')
		assert result.rc == 0

		# Set the doc for it
		result = host.run('stack set attr doc attr=test doc=foo')
		assert result.rc == 0

		# Make sure it there
		result = host.run('stack list attr doc attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'doc': 'foo'
		}]

		# Now delete the doc
		result = host.run('stack set attr doc attr=test doc=')
		assert result.rc == 0

		# Make sure it got removed
		result = host.run('stack list attr doc attr=test output-format=json')
		assert result.rc == 0
		assert result.stdout == ""
