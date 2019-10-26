import pytest
import json
from operator import itemgetter

@pytest.mark.parametrize("command", ["box", "pallet", "cart", "network", "host", "host interface"])
def test_stack_list(command, host, report_output):
	result = host.run(f"stack list {command}")
	assert result.rc == 0
	report_output(f"list {command}", result.stdout)

def test_stacki_pallets_sane(host):
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
	result = host.run("stack list pallet output-format=json")
	assert result.rc == 0
	palinfo = [
		dict((k,v)
		for k, v in p.items() if k != 'boxes')
		for p in json.loads(result.stdout)
	]

	result = host.run('curl http://127.0.0.1/install/pallets/pallets.cgi')
	assert result.rc == 0
	assert result.stdout
	central_pallets = json.loads(result.stdout)

	palgetter = itemgetter('name', 'version', 'release', 'arch', 'os')

	assert sorted(palinfo, key=palgetter) == sorted(central_pallets, key=palgetter)
