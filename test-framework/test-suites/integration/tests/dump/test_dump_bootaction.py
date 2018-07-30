import pytest
import json

class TestDumpBootaction:

	"""
	Test that dumping the bootaction data works properly by adding a bootaction
	then dumping it and checking that it is valid
	"""

	def test_dump_bootaction(self, host):

		# first lets add some data so we have something to check for
		results = host.run('stack add bootaction test args="test arg" kernel="test kernel" os=redhat ramdisk="test ramdisk" type=os')
		assert results.rc == 0

		# dump our bootaction information
		results = host.run('stack dump bootaction')
		assert results.rc == 0
		dumped_data = json.loads(results.stdout)

		# check to make sure that the information we just added is in the dump data
		for profile in dumped_data['bootaction']:
			if profile['name'] == 'test':
				assert profile['kernel'] == 'test kernel'
				assert profile['ramdisk'] == 'test ramdisk'
				assert profile['type'] == 'os'
				assert profile['args'] == ['test', 'arg']
				assert profile['os'] == 'redhat'
