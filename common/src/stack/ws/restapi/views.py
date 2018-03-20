#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout

from stack.restapi.models import BlackList

import pymysql

import json
import stack.commands
import stack.api
import os, sys, time
import subprocess

import logging
import shlex
import re

import traceback


from distutils.sysconfig import get_python_lib

# Start a logger
log = logging.getLogger("stack-ws")

# MySQL Access Denied Error Codes.
# from: https://mariadb.com/kb/en/mariadb/mariadb-error-codes/
MYSQL_EX = [1044, 1045, 1142, 1143, 1227]

## The modules list.host.profile, list.host.xml, and
## list.node.xml, when called through the command line,
## use the correct xml parser. However, when the module
## is called directly, the system XML parser is used. 
## This causes problems when parsing undefined attributes.
## So separate out the xml commands and run them directly

xml_cmds = [
	'list.host.profile',
	'list.host.xml',
	'list.node.xml',
]

class StackWS(View):

	# Decorator Function to check if a user is logged in
	def _check_login_(func):
		def runner(inst, *args, **kwargs):
			request = args[0]
			if request.user.is_authenticated():
				return func(inst, *args, **kwargs)
			else:
				j = json.dumps({'logged_in':False})
				return HttpResponseForbidden(str(j),
					content_type="application/json")

		return runner


	# HTTP Response to GET. Sole purpose of this function
	# is to return a CSRF Cookie
	@method_decorator(ensure_csrf_cookie)
	def get(self, request):
		return HttpResponse('{}')

	# Main POST Function. Runs the actual Stacki Command Line
	@_check_login_
	def post(self, request):
		body = json.loads(request.body)

		# Get the command being used
		cmd = str(body['cmd'])
		args = shlex.split(cmd)

		# Log to file
		log.info("Session Starting")

		# filter out all the params
		param_filter = lambda x: len(x.split('=')) == 2
		params = [p for p in filter(param_filter, args)]

		# Filter out all the args
		arg_filter = lambda x: len(x.split('=')) == 1
		args = [a for a in filter(arg_filter, args)]

		done = False
		command = None
		cmd_arg_list = []

		# Check to see if the user is a superuser
		admin = request.user.is_superuser

		# Get the database connection
		db_conn = _get_db_conn_(admin=admin)

		# Get the command module to execute
		mod_name = '.'.join(args)

		log.info("Webservice user %s called %s" \
			% (request.user.username, mod_name))

		# Check if command is blacklisted
		if self._blacklisted(mod_name):
			msg = "Blacklisted Command: " + \
				"Command %s is not permitted" % mod_name
			return HttpResponseForbidden(msg,
				content_type = "text/plain")

		# Check if user has permission to run
		# command module
		if not request.user.has_perm(mod_name):
			msg = "Unauthorized Command: " + \
				"User %s is not allowed to run %s" \
				% (request.user.username, mod_name)
			return HttpResponseForbidden(msg,
				content_type = "text/plain")

		# Get command module class
		while not done:
			try:
				if len(args) == 0:
					done = True
				else:
					mod_name = '.'.join(args)
					mod = 'stack.commands.%s' % mod_name

					__import__(mod)
					m = eval(mod)

					if hasattr(m, 'Command'):
						command = m.Command(db_conn)
						done = True
					else:
						cmd_arg_list.append(args.pop())
			except ImportError:
					cmd_arg_list.append(args.pop())
			except:
				log.error("%s" % sys.exc_info()[1])

		# If command does not exist, return Not Found
		if not command:
			output = {"API Error":"Command Not Found"}
			return HttpResponse(str(json.dumps(output)),
				content_type="application/json",
				status = 404)

		# Parse the command out. A couple of special
		# cases are called out.
		cmd_arg_list.reverse()
		cmd_arg_list.extend(params)
		cmd_arg_list.append("output-format=json")
		cmd_module = str('.'.join(mod.split('.')[2:]))

		# Don't allow "run host" commands. This opens
		# the door for arbitrary command executions
		if cmd_module == "run.host":
			return HttpResponseForbidden(
			"'run host' command is not permitted",
			content_type="text/plain")

		# Any command that runs an "import xml.*"
		# is required to shell out. See top of file
		# for explanation
		elif cmd_module in xml_cmds:
			c = []
			# If the user is not an admin, lower
			# privileges before running the command
			if not request.user.is_superuser:
				c.extend(['/usr/bin/sudo','-u','nobody'])
			c.append("/opt/stack/bin/stack")
			c.extend(cmd_module.split('.'))
			c.extend(cmd_arg_list)
			p = subprocess.Popen(c, stdin=None,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE)
			o, e = p.communicate()
			rc = p.wait()
			if rc:
				j = {"API Error":e, "Output": o}
				return HttpResponse(str(json.dumps(j)),
					content_type = "application/json",
					status = 500)
			else:
				if not o:
					o = {}
				return HttpResponse(str(json.dumps(o)),
					content_type = "application/json",
					status = 200)
		# If command is a sync/load command, run
		# it with sudo, as the command will require
		# some root privileges. However, if the user
		# isn't a django superuser (with admin privileges)
		# don't allow command to run.
		elif cmd_module.startswith("sync.") or \
			cmd_module.startswith("load.") or \
			cmd_module.startswith("unload.") or \
            cmd_module.startswith("run.host.test") or \
			cmd_module == 'remove.host':
			if not request.user.is_superuser:
				verb = cmd_module.split('.')[0]
				return HttpResponseForbidden(
				"All '%s' commands require Admin Privileges" % verb,
				content_type="text/plain")
			# Run the sync command using sudo
			else:
				c = [
					"/usr/bin/sudo",
					"/opt/stack/bin/stack",
				]
				c.extend(cmd_module.split('.'))
				c.extend(cmd_arg_list)
				p = subprocess.Popen(c, stdout=subprocess.PIPE,
					stderr=subprocess.PIPE)
				o, e = p.communicate()
				rc = p.wait()
				if rc:
					j = {"API Error":e, "Output": o}
					return HttpResponse(str(json.dumps(j)),
						content_type = "application/json",
						status = 500)
				else:
					if not o:
						o = {}
					return HttpResponse(str(json.dumps(o)),
						content_type = "application/json",
						status = 200)
		# If it's not the sync command, run the
		# command module wrapper directly.
		else:
			try:
				rc = command.runWrapper(cmd_module, cmd_arg_list)
			# If we hit a database error, check if it's an access
			# denied error. If so, sanitize the error message, and
			# don't expose database access.
			except pymysql.OperationalError as e:
				errortext = str(sys.exc_info()[1])
				log.error(errortext)
				if int(e.args[0]) in MYSQL_EX:
					errortext = "Database Permission Denied. " +\
						"Admin privileges required"
					status_code = 403
				else:
					status_code = 500
				j = {"API Error":errortext}
				return HttpResponse(str(json.dumps(j)),
					content_type="application/json",
					status=status_code)
			# Any other type of error, simply forward it
			# to the client
			except:
				errortext = str(traceback.format_exc())
				log.error(errortext)
				j = {"API Error":errortext}
				return HttpResponse(str(json.dumps(j)),
					content_type="application/json",
					status=500)

			# Get output from command
			text = command.getText()
			
			if not text:
				text = {}

			# Check to see if text is json
			try:
				j = json.loads(text)
			except:
				j = {"Output":text}
			return HttpResponse(str(json.dumps(text)),
				content_type = "application/json")

	# Check if command is blacklisted
	def _blacklisted(self, mod):
		# Get all blacklisted commands
		c = BlackList.objects.values("command")
		f = lambda x: x['command']
		# Get actual command values
		bl = map(f, c)
		for cmd in bl:
			# Make sure to match the module names
			cmd = re.sub('[ \t]+','.',cmd)
			r = re.compile(str(cmd))
			m = r.match(mod)
			if m:
				# Match the exact blacklisted command
				if m.group() == mod:
					return True
		return False
	
# Create Connections to the database, and return
# connection based on the administrative privilege.
# Use this instead of Django's internal database
# management. Django's internal DB management
# creates a layer between the user and the DB
# and wraps up certain functions. We need direct
# access to the database layer.

def _get_db_conn_(admin=False):
	if admin == True:
		username = 'apache'
		# Get Cluster username and password
		cluster_conf = open("/etc/my.cnf", 'r')
		password = ''
		for line in cluster_conf:
			l = line.split("=")
			if len(l) == 2:
				if l[0].strip() == 'password':
					password = l[1].strip()
	else:
		username = 'nobody'
		password = ''

	link = pymysql.connect(
		user = username,
		passwd = password,
		unix_socket='/var/run/mysql/mysql.sock',
		db = 'cluster', autocommit = True)
	return link


# Function to log in the user
def log_in(request):

	username = request.POST['USERNAME']
	password = request.POST['PASSWORD']

	user = authenticate(username = username, password = password)
	if user is not None:
		login(request, user)
		s = {'login':'True'}
		return HttpResponse(str(json.dumps(s)),
			content_type = "application/json")
	else:
		s = {'login':'False'}
		return HttpResponse(str(json.dumps(s)),
			status=401,
			content_type = "application/json")

# Function to log out
def log_out(request):
	logout(request)
	s = {'logout':'True'}
	return HttpResponse(str(json.dumps(s)),
		content_type="application/json")

# Function to check log in user
def check_user(request):
	if request.user.is_authenticated():
		s = {'user':request.user.username}
	else:
		s = {'user':'None'}
	return HttpResponse(str(json.dumps(s)),
		content_type = "application/json")

# Upload Function. Uploads a file to the provided location
def upload(request):

	ufile = request.FILES["csvFile"]
	csv_dir = '/tmp/' + ufile.name

	d = open(csv_dir, 'wb+')
	chunk = ufile.read()
	d.write(chunk)
	d.close()

	f = open(csv_dir, 'r')
	text = f.read()
	f.close()

	s = {'csv':text, 'name':ufile.name, 'dir':csv_dir}
	return HttpResponse(str(json.dumps(s)),
		content_type="application/json")

def list_dir(request, file):
	"""
	REST response for listing files and folders for a given directory on the frontend
	Location determined by URI, return a list of all directories and files in JSON
	In GUI, this is used for browsing which files to add to the /srv/salt/stack/xfiles
	share folder
	"""

	#determine the parent location to list files and folders
	if file == None:
		file = '/'
	else:
		file = '/' + file

	parent = file

	#create dictionary to be returned
	data = {}
	data["id"] = file
	data["label"] = 'name'
	data["children"] = []
	data["name"] = parent

	F = []
	D = []

	#attempt to list, unless permissions prohibit then return no children
	try:
		#insert names of files and directories into respective arrays
		for file in os.listdir(parent):
			filepath = parent + file
			if os.path.isfile(filepath):
				if not file.startswith('.'):
					F.append(file)
			elif os.path.isdir(filepath):
				D.append(file)

		#sort files and directories arrays
		F.sort()
		D.sort()

		#insert new item for each file and directory into children
		for name in F:
			data["children"].append({
				"type": "file",
				"id": parent + name,
				"name": name})

		for name in D:
			data["children"].append({
				"type": "folder",
				"id": parent + name,
				"name": name,
				"children": True})
	except:
		data["children"] = []

	return HttpResponse(str(json.dumps(data)),
		content_type="application/json")
