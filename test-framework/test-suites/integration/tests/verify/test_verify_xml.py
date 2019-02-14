import json

class TestVerifyXml:
	def test_verify_xml_cart(self, host, revert_etc, revert_export_stack_carts, test_file):
		'''Test if stack verify xml if able to identify errors
		in XML files present in carts.'''

		path = test_file('verify/xml/cart-verifyxmltest.xml')
		host.run("stack add cart verifyxmltest")
		host.run(f"cp {path} /export/stack/carts/verifyxmltest/graph/")

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
