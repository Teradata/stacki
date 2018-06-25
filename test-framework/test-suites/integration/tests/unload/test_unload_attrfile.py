import pytest


class TestUnloadAttrfile:

	"""
	Test that unload does not fail
	"""

	def test_unload_attrfile(self, host):
		results = host.run(f'stack report attrfile')
		assert results.rc == 0
		attrs = results.stdout

		with open('attrfiletest.csv', 'w+') as file:
			file.write(attrs)

		results = host.run(f'stack unload attrfile file=attrfiletest.csv')
		assert results.rc == 0
