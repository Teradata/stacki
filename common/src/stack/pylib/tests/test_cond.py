# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.cond import EvalCondExpr

attrs = {
	'pallets': "['stacki-5.0-sles12', 'SLES-12-sp2', 'nginx-12-sles12', 'highlands-5.0-sles12']",
	'foo.bar': True,
	'a.b.c.d': 'fred'
}

def test_dot():

	assert(EvalCondExpr('foo.bar is True', attrs))
	assert(EvalCondExpr('foo.bar', attrs))
	assert(EvalCondExpr('not foo.bar is False', attrs))

	assert(EvalCondExpr('a.b.c.d == "fred"', attrs))

	assert(EvalCondExpr('"stacki-5.0-sles12" in pallets', attrs))

