#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

from django.views.generic import View
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout

from stack.restapi.models import BlackList
from stack.restapi.models import SudoList
from stack.exception import CommandError
import stack.commands

import pymysql

import json
import os
import sys
import subprocess

import logging
import shlex
import re

import traceback

# Start a logger
log = logging.getLogger("SWS")

# MySQL Access Denied Error Codes.
# from: https://mariadb.com/kb/en/mariadb/mariadb-error-codes/
MYSQL_EX = [1044, 1045, 1142, 1143, 1227]


class StackWS(View):

	# Decorator Function to check if a user is logged in
	def _check_login_(func):
		def runner(inst, *args, **kwargs):
			request = args[0]
			if request.user.is_authenticated():
				return func(inst, *args, **kwargs)
			else:
				j = json.dumps({'logged_in': False})
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
		params = [p for p in filter(lambda x: len(x.split('=')) >= 2, args)]

		# Filter out all the args
		args = [a for a in filter(lambda x: len(x.split('=')) == 1, args)]

		done = False
		command = None
		cmd_arg_list = []

		# Check to see if the user is a superuser
		admin = request.user.is_superuser

		# Get the database connection
		db_conn = _get_db_conn_(admin=admin)

		# Get the command module to execute
		mod_name = '.'.join(args)

		log.info(f'user {request.user.username} called "{mod_name}" {params}')

		# Check if command is blacklisted
		if self._blacklisted(mod_name):
			return HttpResponseForbidden(f'Blacklisted Command: Command {mod_name} is not permitted',
						     content_type="text/plain")

		# Check if user has permission to run
		# command module
		if not request.user.has_perm(mod_name):
			return HttpResponseForbidden('Unauthorized Command: User %s is not allowed to run %s' %
						     (request.user.username, mod_name),
						     content_type="text/plain")

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

						# Flush the cache, we do this
						# since multiple threads may be
						# running and there is no
						# mechanism for one thread to
						# invalidate the cache of
						# another thread.
						command.db.clearCache()

						done = True
					else:
						cmd_arg_list.append(args.pop())
			except ImportError:
				cmd_arg_list.append(args.pop())
			except:
				log.error("%s" % sys.exc_info()[1])

		# If command does not exist, return Not Found
		if not command:
			output = {"API Error": "Command Not Found"}
			return HttpResponse(str(json.dumps(output)),
					    content_type="application/json",
					    status=404)

		# Parse the command out. A couple of special
		# cases are called out.
		cmd_arg_list.reverse()
		cmd_arg_list.extend(params)
		cmd_arg_list.append("output-format=json")
		cmd_module = str('.'.join(mod.split('.')[2:]))

		# Don't allow "run host" commands. This opens
		# the door for arbitrary command executions
		if cmd_module == "run.host":
			return HttpResponseForbidden("'run host' command is not permitted",
						     content_type="text/plain")

		# If command is a sync/load command, run
		# it with sudo, as the command will require
		# some root privileges. However, if the user
		# isn't a django superuser (with admin privileges)
		# don't allow command to run.
		elif self._isSudoCommand(cmd_module):
			if not request.user.is_superuser:
				cmd_str = cmd_module.replace('.', ' ')
				return HttpResponseForbidden(f"Command \"{cmd_str}\" requires Admin Privileges" ,
							     content_type="text/plain")
			# Run the sync command using sudo
			else:
				c = [
					"/usr/bin/sudo",
					"/opt/stack/bin/stack",
				]

				# If we are running pytest-xdist, we need to pass the
				# environment variable into the sudo call
				if 'PYTEST_XDIST_WORKER' in os.environ:
					c.insert(1, 'PYTEST_XDIST_WORKER='+os.environ['PYTEST_XDIST_WORKER'])

				c.extend(cmd_module.split('.'))
				c.extend(cmd_arg_list)
				log.info(f'{c}')
				p = subprocess.Popen(c,
						     stdout=subprocess.PIPE,
						     stderr=subprocess.PIPE,
						     encoding='utf-8')
				output, error = p.communicate()
				rc = p.wait()
				if rc:
					j = {"API Error": error, "Output": output}
					return HttpResponse(str(json.dumps(j)),
							    content_type="application/json",
							    status=500)
				else:
					if not output:
						output = {}

					# Check to see if text is json
					try:
						j = json.loads(output)
					except:
						j = {"Output": output}

					return HttpResponse(str(json.dumps(j)),
							    content_type="application/json",
							    status=200)
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
					errortext = "Database Permission Denied. Admin privileges required"
					status_code = 403
				else:
					status_code = 500
				return HttpResponse(json.dumps({'API Error': errortext}),
						    content_type='application/json',
						    status=status_code)
			except CommandError as e:
				# Get output from command
				text = command.getText()

				if not text:
					text = {}

				return HttpResponse(json.dumps({'API Error': '%s' % e, 'Output': text}),
						    content_type='application/json',
						    status=500)

			# Any other type of error, simply forward it
			# to the client
			except:
				errortext = str(traceback.format_exc())
				log.error(errortext)
				return HttpResponse(json.dumps({'API Error': errortext}),
						    content_type='application/json',
						    status=500)

			# Get output from command
			text = command.getText()

			if not text:
				text = {}

			# Check to see if text is json
			try:
				j = json.loads(text)
			except:
				j = {"Output": text}
			return HttpResponse(str(json.dumps(j)),
					    content_type="application/json")

	# Check if command is blacklisted
	def _blacklisted(self, mod):
		# Get all blacklisted commands
		c = BlackList.objects.values("command")
		# Get actual command values
		bl = map(lambda x: x['command'], c)
		for cmd in bl:
			# Make sure to match the module names
			cmd = re.sub('[ \t]+', '.', cmd)
			r = re.compile(str(cmd))
			m = r.match(mod)
			if m:
				# Match the exact blacklisted command
				if m.group() == mod:
					return True
		return False

	def _isSudoCommand(self, mod):
		# Get a list of all sudo commands
		c = SudoList.objects.values("command")
		sl = [ i['command'] for i in c ]
		for cmd in sl:
			cmd = re.sub('[ \t]+', '.', cmd)
			r = re.compile(str(cmd))
			m = r.match(mod)
			if m and m.group() == mod:
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
	if admin is True:
		username = 'apache'
		# Get Cluster username and password
		cluster_conf = open("/etc/apache.my.cnf", 'r')
		password = ''
		for line in cluster_conf:
			l = line.split("=")
			if len(l) == 2:
				if l[0].strip() == 'password':
					password = l[1].strip()
	else:
		username = 'nobody'
		password = ''

	# Connect to a copy of the database if we are running pytest-xdist
	if 'PYTEST_XDIST_WORKER' in os.environ:
		db_name = 'cluster' + os.environ['PYTEST_XDIST_WORKER']
	else:
		db_name = 'cluster'

	link = pymysql.connect(user=username,
			       passwd=password,
			       unix_socket='/var/run/mysql/mysql.sock',
			       db=db_name,
			       autocommit=True)
	return link


# Function to log in the user
def log_in(request):

	username = request.POST['USERNAME']
	password = request.POST['PASSWORD']

	user = authenticate(username=username, password=password)
	if user is not None:
		login(request, user)
		s = {'login': 'True'}
		return HttpResponse(str(json.dumps(s)),
				    content_type="application/json")
	else:
		s = {'login': 'False'}
		return HttpResponse(str(json.dumps(s)),
				    status=401,
				    content_type="application/json")


# Function to log out
def log_out(request):
	logout(request)
	s = {'logout': 'True'}
	return HttpResponse(str(json.dumps(s)),
			    content_type="application/json")


# Function to check log in user
def check_user(request):
	if request.user.is_authenticated():
		s = {'user': request.user.username}
	else:
		s = {'user': 'None'}
	return HttpResponse(str(json.dumps(s)),
			    content_type="application/json")


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

	s = {'csv': text, 'name': ufile.name, 'dir': csv_dir}
	return HttpResponse(str(json.dumps(s)),
			    content_type="application/json")

