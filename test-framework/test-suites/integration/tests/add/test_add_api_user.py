import pytest
import json

def test_add_api_user(host):
	"""Runs adding user"""
	result = host.run('stack list api user output-format=json')
	assert result.rc == 0
	user_json = json.loads(result.stdout)
	found_test_user = False
	for j in user_json:
		if j["username"] == 'test':
			found_test_user = True

	if found_test_user:
		host.run("stack remove api user test")

	# Check if we can add a user.
	result = host.run("stack add api user test admin=true output-format=json")
	assert result.rc == 0
	api_user = json.loads(result.stdout)[0]
	assert api_user["username"] == "test"
	
	# Check if we can add a user with domainname set to empty
	host.run("stack remove api user test")
	result = host.run('stack list host attr localhost output-format=json attr=hostname')
	assert result.rc == 0
	host_json = json.loads(result.stdout)
	hostname = host_json[0]['value']
	host.run("stack set network zone private zone=''")
	result = host.run("stack add api user test admin=true output-format=json")
	assert result.rc == 0
	j = json.loads(result.stdout)
	h = j[0]['hostname']
	assert h == hostname
