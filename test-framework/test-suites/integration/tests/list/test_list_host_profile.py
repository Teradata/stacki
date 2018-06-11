import pytest
import xml.etree.ElementTree as ET

@pytest.mark.usefixtures("add_host")
def test_list_host_profile(host):
	result = host.run('stack list host profile backend-0-0')
	assert result.rc == 0
	# Check if this is an actual XML output that can be parsed
	root = ET.fromstring(result.stdout)
	# Check for a few expected tags and attributes
	# This could be more and more variable as we go deeper, so I don't check a lot.
	assert root.tag == "profile"
	assert root.attrib == {'type': 'native'}
	for child in root:
		assert child.tag == "chapter"
		for grandchild in child:
			assert grandchild.tag == "section"

