from unittest.mock import patch, create_autospec, PropertyMock
from stack.expectmore import ExpectMore
from stack.switch.x1052 import SwitchDellX1052

# Intercept expectmore calls
mock_expectmore = patch(target = "stack.switch.x1052.ExpectMore", autospec = True).start()
# Need to set the instance mock returned from calling ExpectMore()
mock_expectmore.return_value = create_autospec(
	spec = ExpectMore,
	spec_set = True,
	instance = True,
)
# Need to set the match_index to the base console prompt so that the switch thinks it is at the
# correct prompt, and wont try to page through output.
type(mock_expectmore.return_value).match_index = PropertyMock(return_value = SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT))
# Throw an exception when we try to get the switch mac address infromation
mock_expectmore.return_value.ask.side_effect = ValueError("Test error")
