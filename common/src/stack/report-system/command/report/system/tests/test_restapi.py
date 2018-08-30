import subprocess
import json

def test_restapi_list_host():
	proc = subprocess.Popen(
		'wsclient list host localhost'.split(),
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		encoding='utf-8',
		)

	out, err = proc.communicate()

	assert proc.returncode == 0
	assert err == ''
	assert len(json.loads(out)) == 1
