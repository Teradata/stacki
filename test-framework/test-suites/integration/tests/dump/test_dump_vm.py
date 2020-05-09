import pytest
import json
from pathlib import Path

class TestDumpVM:

	"""
	Test that dumping the host data works properly by adding some host information
	then dumping it and checking that it is valid
	"""


	def test_dump_vm(self, add_hypervisor, add_vm_multiple, host, test_file):

		# Dump our vm information
		results = host.run('stack dump vm')
		assert results.rc == 0
		dumped_data = json.loads(results.stdout)
		expect_file = Path(test_file('dump/vm.json')).read_text()
		expect_data = json.loads(expect_file)

		# Check the output of dump vm is what we expected
		assert dumped_data == expect_data
