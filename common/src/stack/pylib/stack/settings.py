import argparse
import json
import os
from pathlib import Path
import sys
import syslog

import yaml

from stack.util import _exec

syslog.openlog('settings', syslog.LOG_PID, syslog.LOG_LOCAL0)

SETTINGS_FILE = '/opt/stack/etc/stacki.yml'

# these are the base default settings.
# stacki.yaml will override these, but if a setting (or even the whole file) is missing
# these will be the fallback.
DEFAULT_YAML = f'''\
---
# This is the stacki settings file.

# This is the most profiles we will serve at one time. Requests beyond this will be told to retry.
# Doubling the number of cpu cores is a reasonable starting point
# NOTE: You will need to restart apache for changes to take effect
max_concurrent_profile_requests: {2 * os.cpu_count()}

# these are used to generate the CA for frontend's ssl cert
# These are used at frontend installation time.
ssl.organization: 'StackIQ'
ssl.locality: 'Solana Beach'
ssl.state: 'California'
ssl.country: 'US'

# these settings control the starting points for discover-nodes (nee insert ethers)
discovery.base.rack: '0'
discovery.base.rank: '0'
'''

def get_settings():
	'''
	get the default values, then update it from SETTINGS_FILE.

	if SETTINGS_FILE is missing or unparsable, log and ignore
	'''
	settings_data = yaml.safe_load(DEFAULT_YAML)

	try:
		with Path(SETTINGS_FILE).open() as fi:
			yaml_data = yaml.safe_load(fi)
		settings_data.update(yaml_data)
	except FileNotFoundError:
		syslog.syslog(syslog.LOG_ERR, f'could not find {SETTINGS_FILE}')
	except yaml.YAMLError as e:
		syslog.syslog(syslog.LOG_ERR, f'invalid yaml settings file:\n' + str(e))
	except Exception as e:
		syslog.syslog(syslog.LOG_ERR, f'unable to parse settings file:\n' + str(e))

	return settings_data

def write_default_settings_file(overwrite=False):
	'''
	write a clean SETTINGS_FILE
	if SETTINGS_FILE does not exist, do not overwrite it unless `overwrite` is True
	'''
	fi = Path(SETTINGS_FILE)
	if fi.exists() and not overwrite:
		syslog.syslog(syslog.LOG_ERR, f'refusing to overwrite existing settings file.')
		raise FileExistsError
	elif fi.exists() and overwrite:
		syslog.syslog(syslog.LOG_ERR, f'attemping to overwrite existing settings file.')
	if not fi.exists():
		# create /opt/stack/etc/stacki.yml if needed
		fi.parent.mkdir(parents=True, exist_ok=True)
		fi.touch(mode=0o744, exist_ok=True)
	fi.write_text(DEFAULT_YAML)

def main(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('--write-default', help=f'Write the default settings file to {SETTINGS_FILE}', action='store_true')
	parser.add_argument('--force-write-default', help='Overwrite the settings file if it exists', action='store_true')
	parser.add_argument('--print-json', help='Print a json representation of the settings - this is the default if no options are passed', action='store_true')
	args = parser.parse_args(args)

	if args.force_write_default or args.write_default:
		try:
			write_default_settings_file(args.force_write_default)
		except FileExistsError:
			sys.exit(f'settings file already exists at: {SETTINGS_FILE}. Remove or rerun with `--force-write-default`')
	if args.print_json or not any([args.write_default, args.force_write_default, args.print_json]):
		print(json.dumps(get_settings(), indent=4))

if __name__ == '__main__':
	main(sys.argv[1:])
