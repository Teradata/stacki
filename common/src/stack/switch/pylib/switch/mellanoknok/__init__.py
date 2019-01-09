#! /usr/bin/python

import os
from itertools import groupby
from operator import itemgetter

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import logging
logger = logging.getLogger('mellanoknok')
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter('%(asctime)s:%(name)s:%(funcName)s:%(message)s')
try:
	file_logger = logging.FileHandler('/var/log/mellanoknok.log')
	file_logger.setLevel(logging.DEBUG)
	file_logger.setFormatter(log_format)
	logger.addHandler(file_logger)
except Exception as e:
	logger = logging.getLogger('mellanoknok')
	logger.info('unable to write to logfile: "/var/log/mellanoknok.log"')
	logger.info(str(e))

stde_logger = logging.StreamHandler()
stde_logger.setLevel(logging.ERROR)
stde_logger.setFormatter(log_format)

logger.addHandler(stde_logger)

logger.info(__name__)


if 'STACKDEBUG' in os.environ:
	requests_log = logging.getLogger("requests.packages.urllib3")
	requests_log.setLevel(logging.DEBUG)
	requests_log.propagate = True


class ConnectionError(Exception):
	''' Unable to connect to the REST api server '''
	pass

class ArgumentError(Exception):
	''' An argument or field passed to the REST api returned an error '''
	pass


class Mellanoknok():

	def __init__(self, switch, username='admin', password=''):
		self.logger = logging.getLogger('mellanoknok')
		self._info('creating a Mellanoknok object')

		if not password:
			raise ConnectionError('Password required for authenticating to switch API')
		self._session = None
		self._headers = {'Content-Type': 'application/x-www-form-urlencoded'}
		self._base_url = f'http://{switch}/admin/'
		self._cmd_url = self._base_url + 'launch?script=json'
		self._credentials = f'f_user_id={username}&f_password={password}'
		self._connected = False

		self._connection_attempts = 0
		self._connect_to_api_server()


	def _info(self, *params):
		''' convenience function for logging, also allows for future changes to the way we log without changing every call to _info() '''
		self.logger.info([str(item) for item in params])


	def _connect_to_api_server(self):
		''' handle the initial connection to the api server, keeping the session alive as a member var '''

		# note that the login endpoint isn't at `base_url`...
		login_endpoint = self._base_url + 'launch?script=rh&template=login&action=login'

		self._session = requests.Session()

		try:
			self._info('logging in...', login_endpoint, self._headers)
			resp = self._session.post(login_endpoint, headers=self._headers, data=self._credentials)
		except requests.exceptions.ConnectionError:
			raise

		# keep the session cookie
		self._headers['cookie'] = resp.request.headers['Cookie']
		self._info('connected')
		# three consecutive timeouts, raise exception... allows auto-retry without infinite loops
		self._connection_attempts += 1
		if not resp.ok or self._connection_attempts > 3:
			raise ConnectionError('{0} - {1}\n'.format(resp.status_code, resp.reason))
		self._connection_attempts -= 1

		self._connected = True


	def _post(self, cmd):
		''' shorthand to POST to the rest API, attempt to reconnect if our session died '''
		self._info('POST', self._cmd_url, cmd)

		if not self._connected:
			self._connect_to_api_server()

		kwargs = {'headers': self._headers, 'json': {'cmd': cmd}}
		resp = self._session.post(self._cmd_url, **kwargs)

		if resp.status_code == 401:
			self._connect_to_api_server()
			resp = self._session.post(self._cmd_url, **kwargs)

		if resp.status_code == 404:
			msg = 'Unable run command.\nTried to POST at {0} with data: {1}'.format(self._cmd_url, kwargs)
			raise ArgumentError(msg)

		if not resp.ok:
			self._info(results.text)
			raise Exception

		return resp


	def get_interfaces(self):
		''' get all ib interfaces '''
		results = self._post('show interfaces ib')

		data = results.json()['data']

		# 'header' is the name of the interface in the table, in the form of 'IB1/1 state'
		# so return a dictionary of iface name -> {key-value pairs}
		return {k.split()[0]:next(v) for k, v in groupby(data, itemgetter('header'))}

