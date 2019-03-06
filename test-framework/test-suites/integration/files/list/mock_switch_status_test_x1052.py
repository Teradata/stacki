from unittest.mock import patch, create_autospec, PropertyMock
from stack.expectmore import ExpectMore
from stack.switch.x1052 import SwitchDellX1052

# Switch data to mock MAC address table
SWITCH_DATA = """
                                             Flow Link          Back   Mdix
Port     Type         Duplex  Speed Neg      ctrl State       Pressure Mode
-------- ------------ ------  ----- -------- ---- ----------- -------- -------
gi1/0/1  1G-Copper      --      --     --     --  Down           --     --
gi1/0/2  1G-Copper    Full    1000  Enabled  Off  Up          Disabled Off
gi1/0/3  1G-Copper    Full    1000  Enabled  Off  Up          Disabled On
te1/0/1  10G-Fiber      --      --     --     --  Down           --     --

console#:
"""

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
type(mock_expectmore.return_value).match_index = PropertyMock(
	return_value = SwitchDellX1052.CONSOLE_PROMPTS.index(SwitchDellX1052.CONSOLE_PROMPT)
)
# Return our SWITCH_DATA from ExpectMore().ask()
mock_expectmore.return_value.ask.return_value = SWITCH_DATA.splitlines()
