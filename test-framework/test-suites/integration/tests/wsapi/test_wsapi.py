import json


class TestWSAPI_sudo:
	def test_api_sudo_commands(self, host, revert_etc):
		# Add list host to sudo commands
		op = host.run('stack add api sudo command command="list host"')
		assert op.rc == 0

		# Make sure it's there
		op = host.run("stack list api sudo command output-format=json")
		assert op.rc == 0
		assert "list host" in [x["command"] for x in json.loads(op.stdout)]

		# Try to add it again. This should fail
		op = host.run('stack add api sudo command command="list host"')
		assert op.rc == 255
		op.stderr == "error - Command list host is already in sudo list\n"

		# Now check report works
		op = host.run("stack report api sudo command sync=False")
		assert op.rc == 0
		assert "/opt/stack/bin/stack list host *" in op.stdout

		# Now make sure the sync command works
		op = host.run("stack sync api sudo command")
		assert op.rc == 0
		with open("/etc/sudoers.d/stacki_ws") as f:
			assert "/opt/stack/bin/stack list host *" in f.read()

		# Remove the sudo command
		op = host.run('stack remove api sudo command command="list host"')
		assert op.rc == 0

		# Try the remove again. This should fail
		op = host.run('stack remove api sudo command command="list host"')
		assert op.rc == 255
		assert op.stderr == "error - Command list host is not a sudo command\n"

		# Sync again and make sure the command gets removed
		op = host.run("stack sync api sudo command")
		assert op.rc == 0
		with open("/etc/sudoers.d/stacki_ws",'r') as f:
			assert "/opt/stack/bin/stack list host *" not in f.read()

	def test_api_add_bogus_sudo_command(self, host):
		# Add * to sudo commands. This is explicitly not allowed
		op = host.run("stack add api sudo command command=*")
		assert op.rc == 255
		assert op.stderr == "error - Invalid command specification\n"

	def test_api_add_bogus_sudo_command_2(self, host):
		# Add fake command to sudo commands
		op = host.run("stack add api sudo command command=huh")
		assert op.rc == 255
		assert op.stderr == "error - Command huh not found\n"


class TestWSAPI_Blacklist:
	def test_api_blacklist_commands(self, host):
		# Add list host to blacklist commands
		op = host.run('stack add api blacklist command command="list host"')
		assert op.rc == 0

		# Make sure it's there
		op = host.run("stack list api blacklist command output-format=json")
		assert op.rc == 0
		assert "list host" in [x["command"] for x in json.loads(op.stdout)]

		# Try to add it again. This should fail
		op = host.run('stack add api blacklist command command="list host"')
		assert op.rc == 255
		assert op.stderr == "error - Command list host is already blacklisted\n"

		# Remove the blacklist command
		op = host.run('stack remove api blacklist command command="list host"')
		assert op.rc == 0

		# Try the remove again. This should fail
		op = host.run('stack remove api blacklist command command="list host"')
		assert op.rc == 255
		assert op.stderr == "error - Command list host is not blacklisted\n"


class TestWSAPI_User:
	def test_api_user_commands(self, host):
		# Add api user
		op = host.run(f"stack add api user testuser")
		assert op.rc == 0

		# Make sure it's there
		op = host.run("stack list api user output-format=json")
		assert op.rc == 0
		assert "testuser" in [x["username"] for x in json.loads(op.stdout)]

		# Try to add it again. This should fail
		op = host.run("stack add api user testuser")
		assert op.rc == 255
		assert op.stderr == "error - Username testuser is already in use\n"

		# Add perms to user
		op = host.run('stack add api user perms testuser perm="list host"')
		assert op.rc == 0

		# Add perms to user
		op = host.run("stack add api user perms testuser perm=huh")
		assert op.rc == 255
		assert op.stderr == "error - Command huh not found\n"

		op = host.run('stack remove api user perms testuser perm="list host"')
		assert op.rc == 0

		op = host.run('stack remove api user perms testuser perm="list host"')
		assert op.rc == 255
		assert op.stderr == 'error - User testuser does not have perm "list host"\n'

		# Remove the user
		op = host.run("stack remove api user testuser")
		assert op.rc == 0

		# Try the remove again. This should fail
		op = host.run("stack remove api user testuser")
		assert op.rc == 255
		assert op.stderr == "error - Cannot find user testuser\n"


class TestWSAPI_Group:
	def test_api_group_commands(self, host):
		# Add group
		op = host.run("stack add api group testgroup")
		assert op.rc == 0

		# Make sure it's there
		op = host.run("stack list api group output-format=json")
		assert op.rc == 0
		assert "testgroup" in [x["group"] for x in json.loads(op.stdout)]

		# Try to add it again. This should fail
		op = host.run("stack add api group testgroup")
		assert op.rc == 255
		assert op.stderr == "error - Group testgroup is already in use\n"

		# Add perms to group
		op = host.run("stack add api group perms testgroup perm=huh")
		assert op.rc == 255
		assert op.stderr == "error - Command huh not found\n"

		op = host.run('stack remove api group perms testgroup perm="list host"')
		assert op.rc == 255
		assert op.stderr == 'error - Group testgroup does not have perm "list host"\n'

		# Remove the group
		op = host.run("stack remove api group testgroup")
		assert op.rc == 0

		# Try the remove again. This should fail
		op = host.run("stack remove api group testgroup")
		assert op.rc == 255
		assert op.stderr == "error - Cannot find group testgroup\n"
