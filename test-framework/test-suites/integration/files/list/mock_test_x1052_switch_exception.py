from unittest.mock import patch, create_autospec, PropertyMock
from stack.expectmore import ExpectMore

# Intercept expectmore calls
mock_expectmore = patch(target = "stack.switch.x1052.ExpectMore", autospec = True).start()
# Need to set the instance mock returned from calling ExpectMore()
mock_expectmore.return_value = create_autospec(
	spec = ExpectMore,
	spec_set = True,
	instance = True,
)
# Make connect fail
mock_expectmore.return_value.connect.side_effect = ValueError("Test error")
