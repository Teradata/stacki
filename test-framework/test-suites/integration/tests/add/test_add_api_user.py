import pytest
import json

@pytest.mark.usefixtures("revert_database")
def test_add_api_user_qdn(host):
	"""Runs adding user with a FQDN and PQDN"""
	result = host.run('stack list host attr localhost output-format=json attr=domainname')
	#[{"host": "cluster-up-frontend", "scope": "host", "type": "const", "attr": "hostname", "value":"cluster-up-frontend"}]
	assert result.rc == 0
	domain_json = json.loads(result.stdout)
	domainname = domain_json[0]['value']

	result = host.run('stack list host attr localhost output-format=json attr=hostname')
	assert result.rc == 0
	host_json = json.loads(result.stdout)
	hostname = host_json[0]['value']

	result = host.run('stack add api user test0 admin=true')
	assert result.rc == 0
	assert hostname in result.stdout
	assert "." in result.stdout
	assert domainname in result.stdout

	result = host.run('stack set host attr localhost attr=domainname value=""')
	assert result.rc == 0

	result = host.run('stack add api user test1 admin=true')
	assert result.rc == 0
	assert hostname in result.stdout
	assert "." not in result.stdout
	assert domainname not in result.stdout

