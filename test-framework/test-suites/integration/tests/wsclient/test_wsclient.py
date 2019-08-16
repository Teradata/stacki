import json
import os
import re

import wsclient


class TestWSClient:
	def test_bin_wsclient(self, host, host_os):
		"Test the output of /opt/stack/bin/wsclient"

		# Run once... we seem to get the sudo warning which fails
		host.run("wsclient list host")

		# Now the API call should work
		result = host.run("wsclient list host")
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"host": "frontend-0-0",
				"rack": "0",
				"rank": "0",
				"appliance": "frontend",
				"os": host_os,
				"box": "frontend",
				"environment": None,
				"osaction": "default",
				"installaction": "default",
				"comment": None
			}
		]

	def test_remove_host_no_500(self, host, invalid_host, run_django_server):
		"Test a string encoding bugfix, API should return API Error, not 500"

		# Pull in the credentials
		with open('/root/stacki-ws.cred', 'r') as f:
			credentials = json.load(f)

		# Create our client
		client = wsclient.StackWSClient(
			'127.0.0.1',
			'admin',
			credentials[0]['key']
		)

		# Point our client at our own Django instance
		client.url = 'http://127.0.0.1:8000'

		# Login and run a simple command
		client.login()
		result = json.loads(client.run(f'remove host {invalid_host}'))

		assert result == {
			"API Error": f"error - cannot resolve host \"{invalid_host}\"\n",
			"Output": ""
		}

	def test_pylib_against_django(self, host, run_django_server, test_file):
		"Test the wsclient pylib code against our own Django instance"

		# Pull in the credentials
		with open('/root/stacki-ws.cred', 'r') as f:
			credentials = json.load(f)

		# Create our client
		client = wsclient.StackWSClient(
			'127.0.0.1',
			'admin',
			credentials[0]['key']
		)

		# Point our client at our own Django instance
		client.url = 'http://127.0.0.1:8000'

		# Login and run a simple command
		client.login()
		networks = json.loads(client.run('list network'))

		# Get the expected output directly from the CLI
		result = host.run("stack list network output-format=json")
		assert result.rc == 0

		# Make sure we got the data we were expecting
		assert networks == json.loads(result.stdout)

		# Confirm we only have the single network so far
		assert len(networks) == 1

		# Now load in the test network
		client.run(f"load networkfile file={test_file('wsclient/test_network.csv')}")

		# Add in the new network info to the old, for our check
		networks.append({
			"network": "test",
			"address": "10.20.30.0",
			"mask": "255.255.255.0",
			"gateway": "10.20.30.40",
			"mtu": 1500,
			"zone": "testdomain",
			"dns": False,
			"pxe": False
		})

		# Confirm we have two networks now
		result = host.run("stack list network output-format=json")
		assert result.rc == 0
		assert networks == json.loads(result.stdout)
