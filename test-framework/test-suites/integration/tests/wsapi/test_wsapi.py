import os
import sys
import subprocess
import pytest
import json

command="list host"

class TestWSAPI_sudo:
	"""
	This test does the following.
	1. Add a sudo command
	2. sync the command
	3. check to see that the command exists in /etc/sudoers
	4. run wsclient against the code to check if it's run
	   through sudo or not
	5. remove sudo command
	"""
	def test_api_add_sudo_command(self, host):
		# Add list host to sudo commands
		op = host.run(f"stack add api sudo command command=\"{command}\"")
		assert op.rc == 0

	def test_api_list_sudo_command(self, host):
		# Make sure it's there
		op = host.run("stack list api sudo command output-format=json")
		assert op.rc == 0
		o = json.loads(op.stdout)
		cmd = [ x["command"] for x in o ]
		assert (command in cmd)

	def test_api_re_add_sudo_command(self, host):
		# Try to add it again. This should fail
		op = host.run(f"stack add api sudo command command=\"{command}\"")
		assert op.rc == 255 and op.stderr.startswith(f"error - Command {command} is already in sudo list")

	def test_api_report_sudo_command(self, host):
		# Now check report works
		op = host.run("stack report api sudo command")
		assert op.rc == 0
		cmd_found = False
		for line in op.stdout.split("\n"):
			if f"/opt/stack/bin/stack {command} *" in line:
				cmd_found = True
				break

		assert cmd_found

	def test_api_sync_sudo_command(self, host):
		# Now make sure the sync command works
		op = host.run("stack sync api sudo command")
		assert op.rc == 0
		cmd_found = False
		with open("/etc/sudoers.d/stacki_ws",'r') as f:
			for line in f.readlines():
				if f"/opt/stack/bin/stack {command} *" in line:
					cmd_found = True
					break

		assert cmd_found

	def test_api_remove_sudo_command(self, host):
		# Now check report works
		# Undo - Remove the sudo command
		op = host.run(f"stack remove api sudo command command=\"{command}\"")
		assert op.rc == 0
		
	def test_api_re_remove_sudo_command(self, host):
		# Try the remove again. This should fail
		op = host.run(f"stack remove api sudo command command=\"{command}\"")
		assert op.rc == 255 and op.stderr.startswith(f"error - Command {command} is not a sudo command")

	def test_api_re_sync_sudo_command(self, host):
		# Sync again
		# Now make sure the sync command works
		op = host.run("stack sync api sudo command")
		assert op.rc == 0
		cmd_found = False
		with open("/etc/sudoers.d/stacki_ws",'r') as f:
			for line in f.readlines():
				if f"/opt/stack/bin/stack {command} *" in line:
					cmd_found = True
					break

		assert not cmd_found

	def test_api_add_bogus_sudo_command(self, host):
		# Add * to sudo commands. This is explicitly not allowed
		op = host.run(f"stack add api sudo command command=*")
		assert op.rc == 255 and op.stderr.startswith("error - Invalid command specification")

	def test_api_add_bogus_sudo_command_2(self, host):
		# Add fake command to sudo commands
		op = host.run(f"stack add api sudo command command=huh")
		assert op.rc == 255 and op.stderr.startswith("error - Command huh not found")

class TestWSAPI_Blacklist:
	"""
	This test does the following.
	1. Add a sudo command
	2. sync the command
	3. check to see that the command exists in /etc/sudoers
	4. run wsclient against the code to check if it's run
	   through sudo or not
	5. remove sudo command
	"""
	def test_api_blacklist_command(self, host):
		# Add list host to blacklist commands
		op = host.run(f"stack add api blacklist command command=\"{command}\"")
		assert op.rc == 0

	def test_api_list_blacklist_command(self, host):
		# Make sure it's there
		op = host.run("stack list api blacklist command output-format=json")
		assert op.rc == 0
		o = json.loads(op.stdout)
		cmd = [ x["command"] for x in o ]
		assert (command in cmd)

	def test_api_re_add_blacklist_command(self, host):
		# Try to add it again. This should fail
		op = host.run(f"stack add api blacklist command command=\"{command}\"")
		assert op.rc == 255 and op.stderr.startswith(f"error - Command {command} is already blacklisted")

	def test_api_remove_blacklist_command(self, host):
		# Now check report works
		# Undo - Remove the blacklist command
		op = host.run(f"stack remove api blacklist command command=\"{command}\"")
		assert op.rc == 0
		
	def test_api_re_remove_blacklist_command(self, host):
		# Try the remove again. This should fail
		op = host.run(f"stack remove api blacklist command command=\"{command}\"")
		assert op.rc == 255 and op.stderr.startswith(f"error - Command {command} is not blacklisted")


class TestWSAPI_User:
	def test_api_add_user(self, host):
		# Add api user
		op = host.run(f"stack add api user testuser")
		assert op.rc == 0

	def test_api_list_user(self, host):
		# Make sure it's there
		op = host.run("stack list api user output-format=json")
		assert op.rc == 0
		o = json.loads(op.stdout)
		print (o)
		userlist = [ x["username"] for x in o ]
		assert ("testuser" in userlist)

	def test_api_re_add_user(self, host):
		# Try to add it again. This should fail
		op = host.run(f"stack add api user testuser")
		assert op.rc == 255 and op.stderr.startswith(f"error - Username testuser is already in use")

	def test_api_add_user_perms(self, host):
		# Add perms to user
		op = host.run(f"stack add api user perms testuser perm=\"list host\"")
		assert op.rc == 0

	def test_api_add_user_perms(self, host):
		# Add perms to user
		op = host.run(f"stack add api user perms testuser perm=huh")
		assert op.rc == 255 and op.stderr.startswith("error - Command huh not found")

	def test_api_remove_user_perms(self, host):
		op = host.run(f"stack remove api user perms testuser perm=\"list host\"")
		assert op.rc == 255 and op.stderr.startswith("error - User testuser does not have perm \"list host\"")

	def test_api_remove_user(self, host):
		# Undo - Remove the user
		op = host.run(f"stack remove api user testuser")
		assert op.rc == 0
		
	def test_api_re_remove_user(self, host):
		# Try the remove again. This should fail
		op = host.run(f"stack remove api user testuser") 
		assert op.rc == 255 and op.stderr.startswith(f"error - Cannot find user testuser")

class TestWSAPI_Group:
	def test_api_add_group(self, host):
		# Add group
		op = host.run(f"stack add api group testgroup")
		assert op.rc == 0

	def test_api_list_group(self, host):
		# Make sure it's there
		op = host.run("stack list api group output-format=json")
		assert op.rc == 0
		o = json.loads(op.stdout)
		print (o)
		grouplist = [ x["group"] for x in o ]
		assert ("testgroup" in grouplist)

	def test_api_re_add_group(self, host):
		# Try to add it again. This should fail
		op = host.run(f"stack add api group testgroup")
		assert op.rc == 255 and op.stderr.startswith(f"error - Group testgroup is already in use")

	def test_api_add_group_perms(self, host):
		# Add perms to group
		op = host.run(f"stack add api group perms testgroup perm=huh")
		assert op.rc == 255 and op.stderr.startswith("error - Command huh not found")

	def test_api_remove_group_perms(self, host):
		op = host.run(f"stack remove api group perms testgroup perm=\"list host\"")
		assert op.rc == 255 and op.stderr.startswith("error - Group testgroup does not have perm \"list host\"")

	def test_api_remove_group(self, host):
		# Undo - Remove the group
		op = host.run(f"stack remove api group testgroup")
		assert op.rc == 0
		
	def test_api_re_remove_group(self, host):
		# Try the remove again. This should fail
		op = host.run(f"stack remove api group testgroup") 
		assert op.rc == 255 and op.stderr.startswith(f"error - Cannot find group testgroup")
