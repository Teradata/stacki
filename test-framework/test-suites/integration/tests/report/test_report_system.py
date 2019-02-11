class TestReportSystem:
	def test_report_system(self, exclusive_lock, host):
		result = host.run('stack report system pretty=false')
		assert result.rc == 0
