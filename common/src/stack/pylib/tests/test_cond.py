# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.cond import EvalCondExpr

attrs = {
	'a'  : 'foo',
	'a.b': 'bar',
	'b'  : 'foo.bar',
	'b.a': 'bar.foo',
	'p'  : [ "aa", "bb" ],
	'p.a'  : [ "aa.bb", "bb.aa" ]
}

def test_dot():

	assert(EvalCondExpr("a   == 'foo'", attrs))
	assert(EvalCondExpr("a.b == 'bar'", attrs))
	assert(EvalCondExpr("b   == 'foo.bar'", attrs))
	assert(EvalCondExpr("b.a == 'bar.foo'", attrs))

	assert(EvalCondExpr("'a' not in p", attrs))
	assert(EvalCondExpr("'bb' in p", attrs))

	assert(EvalCondExpr("'bb.aa' in p.a", attrs))

