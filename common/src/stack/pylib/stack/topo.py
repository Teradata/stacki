#! /opt/stack/bin/python
# 
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import json
from jsoncomment import JsonComment


def _load_topology():
	topo = { 'redis':    'redis',
		 'database': 'localhost' }

	try:
		parser = JsonComment(json)
		with open('/opt/stack/etc/topo.json') as fin:
			topo = parser.load(fin)
	except ValueError:
		pass
	except FileNotFoundError:
		pass

	return topo


_topo = _load_topology()


class Redis:
	server = _topo['redis']


class Database:
	server = _topo['database']


