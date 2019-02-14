#!/opt/stack/bin/python3

from flask import Flask, request, jsonify, send_from_directory, render_template, redirect
from urllib.request import unquote
from random import shuffle, randint
import os
import logging
from logging import FileHandler
import redis
from stack.topo import Redis
import stack.api

ludicredis = redis.StrictRedis(host=Redis.server)

app = Flask(__name__)

PEERS = set()

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


@app.route('/lookup/<hashcode>', methods=['GET'])
def lookup(hashcode):
	res = {}
	res['success'] = True
	ipaddr = request.remote_addr

	if randint(0, 100) < 10:
		# throttle the flood of message to only X% of package installs,
		# not looking for detail just want to know what stage we are in
		stack.api.Call('add.host.message', [ 'localhost', 
						     'channel=health',
						     'ttl=3600',
						     'message={"state": "install download"}',
						     'source=%s' % ipaddr ])

	# return list of peers with the request hash
	res['peers'] = []
	peers = list(ludicredis.smembers("ludicrous:%s" % hashcode))
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


@app.route('/register/<port>/<hashcode>', methods=['POST'])
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
	ludicredis.sadd("ludicrous:%s" % hashcode, "%s" % ipaddr)

	return jsonify(res)


@app.route('/unregister/hashcode/<hashcode>', methods=['DELETE'])
def unregister(hashcode):
	ipaddr = unquote(request.args['peer'])
	res = {}
	res['success'] = True

	result = ludicredis.srem("ludicrous:%s" % hashcode, ipaddr)
	if result:
		res['message'] = "'%s' was unregistered for hash: %s" % (ipaddr, hashcode)
	else:
		res['message'] = "'%s' was not registered for hash: %s" % (ipaddr, hashcode)

	return jsonify(res)

@app.route('/peerdone', methods=['DELETE'])
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

@app.route('/status', methods=['GET'])
def api_status():
	res = {}
	res['status'] = "good"
	return jsonify(res)

@app.route('/purge', methods=['DELETE'])
def purge_packages():
	res = {}
	res['sucess'] = True
	is_from_frontend = request.remote_addr == "127.0.0.1"
	if is_from_frontend:
		for package in ludicredis.scan_iter():
			try:
				if 'ludicrous' in package.decode():
					result = ludicredis.delete(package)
			except:
				pass
	else:
		res['success'] = False
	
	return jsonify(res)

def main():
	logHandler = FileHandler('/var/log/ludicrous-server.log')
	logHandler.setLevel(logging.INFO)
	app.logger.setLevel(logging.INFO)
	app.logger.addHandler(logHandler)
	app.run(host='0.0.0.0', port=3825)


if __name__ == "__main__":
	main()
