import json
import pytest
import re
import tempfile


class TestLoadHostfile:
	"""Uses the listed test files within test-files/load and runs them through stack load hostfile."""

	# add other csv's here after they are fixed, or better yet make this a glob
	HOSTFILE_SPREADHSEETS = ['multi_frontend', 'single_backend', 'frontend_add_eth', 'frontend_replace_ip',
					'single_backend_and_multi_frontend', 'autoip']

	@staticmethod
	def update_csv_variables(host, csvfile):
		"""Edit the file as needed to match particular environment."""
		dirn = '/export/test-files/load/hostfile_'
		input_file = dirn + csvfile + '_input' + '.csv'
		output_file = dirn + csvfile + '_output' + '.csv'

		result = host.run('stack list host interface a:frontend output-format=json')
		my_json = json.loads(result.stdout)
		mac = my_json[0]["mac"]
		ip = my_json[0]["ip"]
		eth = my_json[0]["interface"]
		# Read in the input and output file's current state
		with open(input_file, 'r') as in_file:
			in_file_data = in_file.read()
		with open(output_file, 'r') as out_file:
			out_file_data = out_file.read()

		# Replace the target string
		in_file_data = in_file_data.replace('FRONT_VARIABLE_IP_ADDRESS', ip)
		in_file_data = in_file_data.replace('FRONT_VARIABLE_MAC_ADDRESS', mac)
		in_file_data = in_file_data.replace('FRONT_VARIABLE_ETH', eth)
		out_file_data = out_file_data.replace('FRONT_VARIABLE_IP_ADDRESS', ip)
		out_file_data = out_file_data.replace('FRONT_VARIABLE_MAC_ADDRESS', mac)
		out_file_data = out_file_data.replace('FRONT_VARIABLE_ETH', eth)

		# Write the files out to temporary files that have the variables
		input_tmp_file = tempfile.NamedTemporaryFile(delete=True)
		with open(input_tmp_file.name, 'w') as file:
			file.write(in_file_data)
		output_tmp_file = tempfile.NamedTemporaryFile(delete=True)
		with open(output_tmp_file.name, 'w') as file:
			file.write(out_file_data)

		return input_tmp_file, output_tmp_file

	@pytest.mark.parametrize("csvfile", HOSTFILE_SPREADHSEETS)
	def test_load_hostfile(self, host, csvfile, revert_etc):
		"""Goes through and loads each individual csv then compares report matches expected output."""
		# get filename
		input_tmp_file, output_tmp_file = self.update_csv_variables(host, csvfile)

		# Add a network address with 2 hosts
		result = host.run('stack add network autoip address=10.1.1.4 mask=255.255.255.252')

		host.run('stack load hostfile')
		# Load the hostfile input
		host.run('stack load hostfile file=%s' % input_tmp_file.name)
		# Get the new stack hostfile back out
		stack_output_file = tempfile.NamedTemporaryFile(delete=True)
		host.run('stack report hostfile > %s' % stack_output_file.name)

		# Check that it matches our expected output
		with open(output_tmp_file.name) as test_file:
			test_lines = test_file.readlines()
		with open(stack_output_file.name) as stack_file:
			stack_lines = stack_file.readlines()
		assert len(test_lines) == len(stack_lines)
		for i in range(len(test_lines)):
			assert test_lines[i].strip() == stack_lines[i].strip()
	
	def test_load_hostfile_ip_no_network(self, host):
		# load hostfile containing an interface with an IP but no network (invalid)
		result = host.run('stack load hostfile file=/export/test-files/load/load_hostfile_ip_no_network.csv')
		assert result.rc != 0
		assert 'inclusion of IP requires inclusion of network' in result.stderr

	def test_load_hostfile_duplicate_interface(self, host):
		# load hostfile containing duplicate interface names (invalid)
		result = host.run('stack load hostfile file=/export/test-files/load/load_hostfile_duplicate_interface.csv')
		assert result.rc != 0
		assert re.search(r'interface ".+" already specified for host', result.stderr) is not None

	def test_load_hostfile_with_unicode(self, host):
		result = host.run('stack load hostfile file=/export/test-files/load/load_hostfile_with_unicode.csv')
		assert result.rc != 0
		assert 'error - non-ascii character in file' in result.stderr
