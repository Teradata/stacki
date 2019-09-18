import pytest
from unittest.mock import patch
from stack.profile import Pass1NodeHandler
from stack.util import KickstartNodeError

class Pass1NodeHandlerUnderTest(Pass1NodeHandler):
	"""Class override to mock __init__ to remove required dependencies."""

	def __init__(self, *args, **kwargs):
		pass

@patch(target="subprocess.Popen", autospec=True)
def test_endTag_stack_eval_command_failure(mock_popen):
	"""Test that a KickstartNodeError is raised when an eval fails."""
	# Set up required attributes on the node handler
	test_node_handler = Pass1NodeHandlerUnderTest()
	test_node_handler.setEvalState = True
	test_node_handler.doEval = True
	test_node_handler.evalShell = "sh"
	test_node_handler.evalText = "foocommand"
	# Set up return value for mock_popen.communicate and a nonzero return code
	mock_popen.return_value.communicate.return_value = ("foo", "bar")
	mock_popen.return_value.returncode = 255

	with pytest.raises(KickstartNodeError):
		test_node_handler.endTag_stack_eval(ns="foo", tag="bar")
