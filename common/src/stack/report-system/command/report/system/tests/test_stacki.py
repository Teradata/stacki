import pytest
import json

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
