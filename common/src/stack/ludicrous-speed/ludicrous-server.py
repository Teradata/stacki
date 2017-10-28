#!/opt/stack/bin/python3

from flask import Flask, request, jsonify, send_from_directory, render_template, redirect
from urllib.request import unquote
from random import shuffle
import os
import logging
from logging import FileHandler
import redis

ludicredis = redis.StrictRedis()

app = Flask(__name__)

packages = {}
peers = {}

MAX_PEERS = 3
ROOT_DIR = "/var/www/html"


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

	# return list of peers with the request hash
	res['peers'] = []
	peers = list(ludicredis.smembers(hashcode))
	shuffle(peers)
	for peer in peers:
		# only append a peer if it is not the requester
		if ipaddr not in peer.decode():
			res['peers'].append("%s" % peer.decode())
		
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

	# Register Package
	ludicredis.sadd(hashcode, "%s:%s" % (ipaddr, port))

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

	packages = ludicredis.scan(0)[1]

	for package in packages:
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
