import pytest
import json


@pytest.mark.usefixtures("add_switch")
def test_list_switch(host):
	result = host.run('stack list switch expanded=true output-format=json')
	assert result.rc == 0

	list_switch_data = json.loads(result.stdout)
	assert len(list_switch_data) == 1
	assert 'ib subnet manager' in list_switch_data[0].keys()

	# for non-ib switches this field should be None
	assert list_switch_data[0]['ib subnet manager'] == None
