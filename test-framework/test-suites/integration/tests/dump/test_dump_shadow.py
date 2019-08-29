import json
from tempfile import NamedTemporaryFile

def test_dump_shadow(host):
	''' shadow attributes should not be dumped '''

	results = host.run('stack add attr attr=test value=shadowvalue shadow=true')
	assert results.rc == 0
	results = host.run('stack add host attr a:frontend attr=test2 value=shadowvalue shadow=true')
	assert results.rc == 0

	tempfi = NamedTemporaryFile()
	results = host.run(f'stack dump > {tempfi.name}')
	assert results.rc == 0

	with open(tempfi.name) as fi:
		data = json.load(fi)

		# check global scope
		shadows = [attr for attr in data['attr'] if 'shadow' in attr]
		assert shadows == []
		test_attrs =  [attr for attr in data['attr'] if attr['name'] == 'test']
		assert test_attrs == []

		# now check host level.  shouldn't make a difference, but check anyway.
		for host in data['host']:
			if host['appliance'] == 'frontend':
				shadows = [attr for attr in host['attr'] if 'shadow' in attr]
				assert shadows == []
				test_attrs =  [attr for attr in host['attr'] if attr['name'] == 'test2']
				assert test_attrs == []

