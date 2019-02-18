from unittest.mock import Mock, patch, mock_open

# Intercept pexpect calls
patch('stack.switch.x1052.pexpect').start()

# We also don't need to sleep
patch('stack.switch.x1052.time').start()

# Throw an exception when we try to write the switch mac address file
mock_open = patch('stack.switch.x1052.open').start()
mock_open.return_value = Mock(side_effect=Exception)
