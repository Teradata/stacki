#!/opt/stack/bin/python3

from flask import Flask, request, jsonify, send_from_directory, render_template, redirect
from urllib.request import unquote
from random import shuffle
import os
import logging
from logging import FileHandler
import redis
from time import time

ludicredis = redis.StrictRedis()

app = Flask(__name__)

PEERS = set()

MAX_PEERS = 3
ROOT_DIR = "/var/www/html"
REDIS_UPDATE_INTERVAL = 10
REDIS_LAST_UPDATED = {}

def time_passed(host):
	if host not in REDIS_LAST_UPDATED:
		REDIS_LAST_UPDATED[host] = time()
    return time() - REDIS_LAST_UPDATED[host] > REDIS_UPDATE_INTERVAL

def updateKey(key, value, timeout=None):
		"""
		Create an new *key* and *value* in the local Redis
		database with an optional *timeout*.
		If the *key* already exist the value is blindly updated, and
		the *timeout* is reset if it is specified.

		:param key: redis key
		:type key: string
		:param value: key value
		:type value: string
		:param timeout: key timeout in seconds
		:type timeout: int
		"""
		ludicredis.set(key, value)
		ludicredis.expire(key, timeout)

def updateHostKeys(client):
	"""
	Updates the Redis keys for a given host in the cluster.
	If Redis does not know about the host the cluster database is inspected and
	the keys are created with a one hour timeout.
	If Redis already contains the keys the timeout is reset.
	The following Redis keys are defined for the host::

		host:HOSTNAME:rack
		host:HOSTNAME:rank
		host:HOSTNAME:addr
		host:IPADDRESS:name

	:param addr: IP address
	:type addr: string
	:returns: dictionary with *name*, *addr*, *rack*, and *rank*
	"""
	if not client:
		client = '127.0.0.1'

	host = ludicredis.get('host:%s:name' % client)
	if host:
		host = host.decode()
		rack = ludicredis.get('host:%s:rack' % host).decode()
		rank = ludicredis.get('host:%s:rank' % host).decode()
		addr = ludicredis.get('host:%s:addr' % host).decode()

	if not host or not rack or not rank or not addr:
		for row in stack.api.Call('list.host', [ client ]):
			host = row['host']
			rack = row['rack']
			rank = row['rank']

		if host:
			updateKey('host:%s:name' % client, host,   60 * 60)
			updateKey('host:%s:addr' % host,   client, 60 * 60)
			updateKey('host:%s:rack' % host,   rack,   60 * 60)
			updateKey('host:%s:rank' % host,   rank,   60 * 60)

	d = { 'name': host,
		 'addr': client,
		 'rack': rack,
		 'rank': rank }

	return d

@app.errorhandler(404)
def four_o_four(error=None):
	error_message = error if type(error) is str else "File not found."
	message = {
		'status': 404,
		'message': error_message
	}

	resp = jsonify(message)
	resp.status_code = 404

	return resp


@app.route('/avalanche/lookup/<hashcode>', methods=['GET'])
def lookup(hashcode):
	res = {}
	res['success'] = True
	ipaddr = request.remote_addr
	_host = updateHostKeys(ipaddr)

	if time_passed(host):
		updateKey('host:%s:status' % _host['name'],
				       'Installing packages', 60*60)

	# return list of peers with the request hash
	res['peers'] = []
	peers = list(ludicredis.smembers(hashcode))
	shuffle(peers)
	for peer in peers:
		# only append a peer if it is not the requester
		if ipaddr not in peer.decode():
                        peer_port = ludicredis.smembers('%s:PORT' % ipaddr)
                        if peer_port:
                                res['peers'].append("%s:%s" % (peer.decode(), peer_port.pop().decode()))
                        else:
                                res['peers'].append("%s:%s" % (peer.decode(), '80'))		

		# if array of peers is max_peers, break
		if len(res['peers']) == MAX_PEERS:
			break

	return jsonify(res)


@app.route('/avalanche/register/<port>/<hashcode>', methods=['POST'])
def register(port=80, hashcode=None):
	res = {}
	res['success'] = True
	ipaddr = request.remote_addr

	if not hashcode:
		return four_o_four()

	# check if 
	if ipaddr not in PEERS:
		if not ludicredis.smembers("%s:PORT" % ipaddr):
			ludicredis.sadd("%s:PORT" % ipaddr, "%s" % port)
			PEERS.add(ipaddr)

	# Register Package
	ludicredis.sadd(hashcode, "%s" % ipaddr)

	return jsonify(res)


@app.route('/avalanche/unregister/hashcode/<hashcode>', methods=['DELETE'])
def unregister(hashcode):
	ipaddr = unquote(request.args['peer'])
	res = {}
	res['success'] = True

	result = ludicredis.srem(hashcode, ipaddr)
	if result:
		res['message'] = "'%s' was unregistered for hash: %s" % (ipaddr, hashcode)
	else:
		res['message'] = "'%s' was not registered for hash: %s" % (ipaddr, hashcode)

	return jsonify(res)

@app.route('/avalanche/peerdone', methods=['DELETE'])
def peerdone():
	ipaddr = request.remote_addr
	res = {}
	res['success'] = True

	for package in ludicredis.scan_iter():
		try:
			ludicredis.srem(package, ipaddr)
		except:
			pass	
		
	return jsonify(res)


@app.route('/avalanche/stop', methods=['GET'])
def stop_server():
	return "-1"

def main():
	logHandler = FileHandler('/var/log/ludicrous-server.log')
	logHandler.setLevel(logging.INFO)
	app.logger.setLevel(logging.INFO)
	app.logger.addHandler(logHandler)
	app.run(host='0.0.0.0', port=3825)


if __name__ == "__main__":
	main()
