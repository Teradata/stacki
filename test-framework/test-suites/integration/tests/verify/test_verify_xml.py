import json

class TestVerifyXml:
	def test_verify_xml_cart(self, host, revert_etc, revert_export_stack_carts):
		'''Test if stack verify xml if able to identify errors
		in XML files present in carts.'''

		CART_XML = '/export/test-files/verify/xml/cart-verifyxmltest.xml'
		host.run("stack add cart verifyxmltest")
		host.run("cp %s /export/stack/carts/verifyxmltest/graph/", CART_XML)

		op = host.run("stack verify xml output-format=json")
		assert op.rc == 0

		o = json.loads(op.stdout)
		expectedOp = {
			"filename": "/export/stack/carts/verifyxmltest/graph/cart-verifyxmltest.xml",
			"linenumber": "5",
			"errmessage": "mismatched tag"
		}

		for line in o:
			assert(line['filename'] == expectedOp['filename'])
			assert(line['linenumber'] == expectedOp['linenumber'])
			assert(line['errmessage'] == expectedOp['errmessage'])

		# Cleanup
		host.run("stack remove cart verifyxmltest")
