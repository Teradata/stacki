import pytest

import stack.roll

class TestRollParser:
	def test_rolls_parsing(self, test_file):
		g = stack.roll.Generator()
		g.parse(test_file('pylib/rolls.xml'))
		assert g.rolls == [
			('stacki', '05.02.06.09', 'sles12', 'x86_64', 'http://127.0.0.1/mnt/cdrom/', 'stacki - Disk 1'),
		]

		# note that running parse multiple times resets Generator.rolls
		g.parse(test_file('pylib/multiple-rolls.xml'))
		assert g.rolls == [
			('stacki', '05.02.06.09', 'sles12', 'x86_64', 'http://127.0.0.1/mnt/cdrom/', 'stacki - Disk 1'),
			('tdc-infrastructure', '01.05.00.01', 'sles12sp3', 'x86_64', 'http://127.0.0.1/mnt/cdrom/', 'tdc-infrastructure - Disk 1')
		]
