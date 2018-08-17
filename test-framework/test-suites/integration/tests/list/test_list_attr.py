import pytest
import json

@pytest.mark.usefixtures('revert_database')
class TestListAttr:

	def test_list_attr_with_shadow(self, host):
		result = host.run('stack list attr output-format=json')
		assert result.rc == 0
		list_attr_output_json = json.loads(result.stdout)

		result = host.run('stack list attr shadow=True output-format=json')
		assert result.rc == 0
		list_attr_shadow_True_output_json = json.loads(result.stdout)

		assert list_attr_output_json == list_attr_shadow_True_output_json


	def test_list_attr_without_shadow(self, host):
		result = host.run('stack list attr shadow=False output-format=json')
		assert result.rc == 0

		list_attr_shadow_False_output_json = json.loads(result.stdout)
		assert self.validate_attr_list(list_attr_shadow_False_output_json)

		result = host.run('stack list attr shadow=True output-format=json')
		assert result.rc == 0

		list_attr_shadow_True_output_json = json.loads(result.stdout)
		assert list_attr_shadow_False_output_json != list_attr_shadow_True_output_json


	# Checks if any attr in the attr list is of the type shadow and it's corresponding value is Null or None
	def validate_attr_list(self, attr_json_file):
		for attr in attr_json_file:
			if attr['type']=='shadow' :
				if attr['value'] is not None:
					return False
		return True

