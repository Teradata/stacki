import pytest
import json
from operator import itemgetter

import stack.settings

@pytest.mark.parametrize("command", ["box", "pallet", "cart", "network", "host", "host interface"])
def test_stack_list(command, host, report_output):
	'''
	prepare a report for several key database objects
	'''
	result = host.run(f"stack list {command}")
	assert result.rc == 0
	report_output(f"list {command}", result.stdout)

def test_stacki_pallets_sane(host):
	'''
	Test that the stacki pallet(s) at least are somewhat sane
	'''
	palletdir = '/export/stack/pallets/'

	result = host.run(f'probepal {palletdir}')
	assert result.rc == 0
	palinfo = json.loads(result.stdout)
	# it shouldn't be empty
	assert palinfo[palletdir]

	stacki_pallets = []
	important_dirs = ['graph', 'nodes', 'RPMS', 'repodata']
	for pallet in palinfo[palletdir]:
		if pallet['name'] == 'stacki':
			for subdir in important_dirs:
				assert host.file(f"{pallet['pallet_root']}/{subdir}").is_directory
			stacki_pallets.append(pallet)

	# there should be at least one stacki pallet
	assert stacki_pallets

def test_stacki_central_server(host):
	'''
	test that the frontend is correctly configured to act as a central server
	(serving pallets to other frontends)
	'''
	result = host.run("stack list pallet output-format=json")
	assert result.rc == 0
	palinfo = [
		{k: v for k,v in p.items() if k not in ['boxes', 'is_install_media']}
		for p in json.loads(result.stdout)
	]

	result = host.run('curl http://127.0.0.1/install/pallets/pallets.cgi')
	assert result.rc == 0
	assert result.stdout
	central_pallets = json.loads(result.stdout)

	palgetter = itemgetter('name', 'version', 'release', 'arch', 'os')

	assert sorted(palinfo, key=palgetter) == sorted(central_pallets, key=palgetter)

def test_stacki_ca_correct(host):
	'''
	test that the ssl certificate authority was created correctly
	'''

	version_chk_result = host.run('openssl version')
	assert version_chk_result.rc == 0
	old_openssl = version_chk_result.stdout.startswith('OpenSSL 1.0')

	result = host.run('openssl x509 -noout -issuer -in /etc/security/ca/ca.crt')
	assert result.rc == 0

	# on sles15 (openssl 1.1.0i) output looks like:
	# issuer=O = StackIQ, OU = frontend-0-0-CA, L = Solana Beach, ST = California, C = US, CN = frontend-0-0
	#
	# on rhel7 (openssl 1.0.2k-16) / sles12sp3 (openssl 1.0.2j-59.1)
	# issuer= /O=StackIQ/OU=sd-stacki-147-CA/L=Solana Beach/ST=California/C=US/CN=sd-stacki-147.labs.teradata.com
	#
	# honestly, it's $CURRENT_YEAR, how hard is it to produce a more parser friendly output
	if old_openssl:
		# split across '/', then '=', ignore 'issuer= '
		ca_dict = dict(item.strip().split('=') for item in result.stdout.split('/')[1:])
	else:
		# split across commas, then ' = '
		ca_dict = dict(item.strip().split(' = ') for item in result.stdout.split(','))
		ca_dict['O'] = ca_dict['issuer=O']

	stacki_set = {k: v for k, v in stack.settings.get_settings().items() if k.startswith('ssl.')}

	# note, we're ignoring CN and OU, as these will vary
	assert ca_dict['L'] == stacki_set['ssl.locality']
	assert ca_dict['C'] == stacki_set['ssl.country']
	assert ca_dict['ST'] == stacki_set['ssl.state']
	assert ca_dict['O'] == stacki_set['ssl.organization']
