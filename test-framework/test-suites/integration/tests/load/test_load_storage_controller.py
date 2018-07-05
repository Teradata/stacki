import tempfile
import pytest

STORAGE_SPREADSHEETS = ['error']


def parse_hosts(input_file):
	hostnames = set()
	with open(input_file) as open_file:
		# skip the header line
		lines = open_file.readlines()[1:]
		for line in lines:
			if line.startswith(',') or line.lower().startswith('name'):
				pass
			else:
				hostnames.add(line.split(',')[0].lower())
	return hostnames

@pytest.mark.usefixtures("revert_database")
@pytest.mark.usefixtures("add_host")
@pytest.mark.parametrize("csvfile", STORAGE_SPREADSHEETS)
def test_load_storage_controller(host, csvfile):
	# get filename
	dirn = '/export/test-files/load/storage_controller_'
	input_file = dirn + csvfile + '_input' + '.csv'
	output_file = dirn + csvfile + '_output' + '.csv'

	hostnames = sorted(parse_hosts(input_file))

	# check that it has no controller info by default
	for name in hostnames:
		result = host.run('stack list storage controller %s' % name)
		assert result.rc == 255
		assert result.stdout == ''

	# load the controller file
	result = host.run('stack load storage controller file=%s' % input_file)
	if 'error' in input_file:
		assert result.rc == 255
	else:
		assert result.rc == 0

	# Get the new stack controller file back out
	stack_output_file = tempfile.NamedTemporaryFile(delete=True)
	result = host.run('stack list storage controller > %s' % stack_output_file.name)
	assert result.rc == 0
	for name in hostnames:
		if name.lower() != 'global':
			result = host.run('stack list storage controller %s >> %s' % (name, stack_output_file.name))
		assert result.rc == 0

	# Check that it matches our expected output
	output_tmp_file = tempfile.NamedTemporaryFile(delete=True)
	with open(output_tmp_file.name) as test_file:
		test_lines = test_file.readlines()
	with open(output_file) as stack_file:
		stack_lines = stack_file.readlines()
	assert len(test_lines) == len(stack_lines)
	for i in range(len(test_lines)):
		assert test_lines[i].strip() == stack_lines[i].strip()



