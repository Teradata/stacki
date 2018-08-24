import pytest

@pytest.mark.usefixtures('revert_database')
class TestReportSystem:
	def test_report_system(self, host):
		result = host.run('stack report system')
		assert result.rc == 0
