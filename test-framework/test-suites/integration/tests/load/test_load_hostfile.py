import json
import pytest
import re
import tempfile


@pytest.mark.usefixtures("revert_database")
class TestLoadHostfile:
	"""Uses the listed test files within test-files/load and runs them through stack load hostfile."""

	# add other csv's here after they are fixed, or better yet make this a glob
	HOSTFILE_SPREADHSEETS = ['multi_frontend', 'single_backend', 'frontend_add_eth', 'frontend_replace_ip',
					'single_backend_and_multi_frontend', 'autoip']

	@staticmethod
	def update_csv_variables(host, csvfile):
		"""Edit the file as needed to match particular environment."""
		private_network = None
		vagrant_network = None
		dirn = '/export/test-files/load/hostfile_'
		input_file = dirn + csvfile + '_input' + '.csv'
		output_file = dirn + csvfile + '_output' + '.csv'

		result = host.run('stack report hostfile a:frontend')
		# Cleaning up the hostfile, there is an extra return, so strip()
		# Remove the header, so split on new line and drop first [1:]
		# join them back together, so '\n'.join
		# make sure we didn't get an extra line in there, so strip() again

		frontend_ifaces = '\n'.join(result.stdout.strip().split('\n')[1:]).strip()
		print(frontend_ifaces)
		# Read in the input and output file's current state
		with open(input_file, 'r') as in_file:
			in_file_data = in_file.read()
		with open(output_file, 'r') as out_file:
			out_file_data = out_file.read()

		# Replace the target string
		in_file_data = in_file_data.replace('REPLACE', str(frontend_ifaces))
		out_file_data = out_file_data.replace('REPLACE', str(frontend_ifaces))

		# Write the files out to temporary files that have the variables
		input_tmp_file = tempfile.NamedTemporaryFile(delete=True)
		with open(input_tmp_file.name, 'w') as file:
			file.write(in_file_data)
		output_tmp_file = tempfile.NamedTemporaryFile(delete=True)
		with open(output_tmp_file.name, 'w') as file:
			file.write(out_file_data)

		return input_tmp_file, output_tmp_file

	@pytest.mark.parametrize("csvfile", HOSTFILE_SPREADHSEETS)
	def test_load_hostfile(self, host, csvfile):
		"""Goes through and loads each individual csv then compares report matches expected output."""
		# get filename
		input_tmp_file, output_tmp_file = self.update_csv_variables(host, csvfile)

		# Add a network address with 2 hosts
		result = host.run('stack add network autoip address=10.1.1.4 mask=255.255.255.252')

		host.run('stack load hostfile')
		# Load the hostfile input
		print(csvfile)
		result = host.run('cat %s' % input_tmp_file.name)
		print(result.stdout)
		print(result.rc)
		print(result.stderr)
		result = host.run('stack load hostfile file=%s' % input_tmp_file.name)
		print(result.stdout)
		print(result.rc)
		print(result.stderr)
		# Get the new stack hostfile back out
		stack_output_file = tempfile.NamedTemporaryFile(delete=True)
		host.run('stack report hostfile > %s' % stack_output_file.name)

		# Check that it matches our expected output
		with open(output_tmp_file.name) as test_file:
			test_lines = test_file.readlines()
		with open(stack_output_file.name) as stack_file:
			stack_lines = stack_file.readlines()
		print("Expected:")
		print(test_lines)
		print("What we got:")
		print(stack_lines)
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

