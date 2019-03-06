from unittest.mock import patch, create_autospec, PropertyMock
from stack.expectmore import ExpectMore
from stack.switch.x1052 import SwitchDellX1052

# Switch data to mock MAC address table
SWITCH_DATA = """
show mac address-table
    show mac address-table
Flags: I - Internal usage VLAN
Aging time is 300 sec

    Vlan          Mac Address         Port       Type
------------ --------------------- ---------- ----------
     1         00:00:00:00:00:00    gi1/0/10   dynamic
     1         f4:8e:38:44:10:15       0         self

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
