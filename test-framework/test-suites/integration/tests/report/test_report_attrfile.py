import pytest


class TestReportAttrfile:

	"""
	Test that the report function reports a csv that both loadable and consistent
	consistent meaning that report -> load -> report should yield the same result
	"""

	def test_report_attrfile(self, host):
		results = host.run(f'stack report attrfile')
		assert results.rc == 0
		output1 = results.stdout

		with open ('attrfiletest.csv', 'w+') as file:
			file.write(output1)

		results = host.run(f'stack load attrfile file=attrfiletest.csv')
		assert results.rc == 0

		results = host.run(f'stack report attrfile')
		assert results.rc == 0
		output2 = results.stdout

		assert output1 == output2
