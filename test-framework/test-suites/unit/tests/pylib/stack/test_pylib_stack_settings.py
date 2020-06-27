import pytest
from unittest.mock import patch, mock_open

import json
import os
from pathlib import Path

import yaml

import stack.settings

DEFAULT_SETTING_KEYS = [
	'max_concurrent_profile_requests',
	'ssl.country',
	'ssl.locality',
	'ssl.organization',
	'ssl.state',
	'discovery.base.rack',
	'discovery.base.rank',
]

CUSTOM_YAML = '''\
max_concurrent_profile_requests: 9001
random_setting: foo
'''

class TestSettings:
	def test_default_string_parses_yaml(self):
		assert yaml.safe_load(stack.settings.DEFAULT_YAML)

	def test_default_settings_has_known_keys(self):
		assert set(DEFAULT_SETTING_KEYS).issubset(stack.settings.get_settings())

	def test_default_settings_sets_cpus(self):
		assert stack.settings.get_settings()['max_concurrent_profile_requests'] == (2 * os.cpu_count())

	def test_read_settings_if_no_file(self):
		''' if there is no settings file, or it's empty, get_settings() should just get the defaults '''
		# mock_open replaces Path's open() with empy string, as if the file was empty
		with patch.object(Path, 'open', mock_open):
			assert stack.settings.get_settings() == yaml.safe_load(stack.settings.DEFAULT_YAML)

	def test_read_settings_if_settings_changed(self):
		'''
		explicitly check what happens if the file is replaced with a subset of the settings
		current design is that it should load in the defaults (in memory), and then replace the settings which do exist
		'''

		# now replace the open file with CUSTOM_YAML
		with patch.object(Path, 'open', mock_open(read_data=CUSTOM_YAML)):
			custom_settings = stack.settings.get_settings()

		# overlay the hard-coded settings with CUSTOM_YAML settings
		# this code should effectively mirror stack.settings.get_settings()
		base_settings = yaml.safe_load(stack.settings.DEFAULT_YAML)

		assert custom_settings != base_settings

		additional_settings = yaml.safe_load(CUSTOM_YAML)
		base_settings.update(additional_settings)

		assert custom_settings == base_settings

# test overwriting file

# test writing file
# test failing to write file

# report system test that semaphore file exists


