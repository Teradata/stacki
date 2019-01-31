import pytest

import os
import tempfile

from jinja2 import Template

versionmk = '''export ROLL = {{ pallet_name }}
export VERSION = {{ version }}
export ROLLVERSION = {{ version }}
export RELEASE = $(shell $(STACKBUILD.ABSOLUTE)/bin/os-release)
ROLLS.OS = {{ os }}
ISOSIZE = 0
'''

CREATE_NEW_PALLET_ARGS = [
	['mypal', '', ''],
	['bob', '2.0', ''],
	['bob', '', 'sles'],
	['bob', '3.14', 'redhat'],
	['bob', '1.0', 'ubuntu'],
]

class TestCreateNewPallet:

	@pytest.mark.parametrize("pallet_name,version,pallet_os", CREATE_NEW_PALLET_ARGS)
	def test_rendered_templates(self, host, host_os, pallet_name, version, pallet_os):
		with tempfile.TemporaryDirectory() as tmp:
			os.chdir(tmp)
			args = {
				'name': pallet_name,
				'version': version,
				'os': pallet_os,
			}

			arg_str = ' '.join(f'{key}={value}' for key, value in args.items() if value)
			result = host.run(f'stack create new pallet {arg_str}')
			assert result.rc == 0

			assert host.file(f'./{pallet_name}').exists
			assert host.file(f'./{pallet_name}').is_directory

			if not pallet_os:
				args['os'] = host_os
			if not version:
				args['version'] = '1.0'
			del args['name']
			args['pallet_name'] = pallet_name

			rendered_fi = Template(versionmk).render(**args)
			# collapse whitespace for the sake of string comparison
			rendered_fi = ' '.join(rendered_fi.split())

			with open(f'./{pallet_name}/version.mk', 'r') as fi:
				assert ' '.join(fi.read().split()) == rendered_fi

	def test_files_created(self, host):
		with tempfile.TemporaryDirectory() as tmp:
			os.chdir(tmp)
			pallet_name = 'mypal'
			result = host.run(f'stack create new pallet name={pallet_name}')
			assert result.rc == 0

			files = [
				'./{0}/graph/{0}.xml',
				'./{0}/nodes/{0}-base.xml',
				'./{0}/nodes/{0}-client.xml',
				'./{0}/nodes/{0}-server.xml',
				'./Makefile',
				'./version.mk',
			]

			for fi in files:
				fi_handle = host.file(fi.format(pallet_name))
				fi_handle.exists
