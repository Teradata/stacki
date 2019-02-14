from unittest.mock import Mock, patch


# Intercept pexpect calls
mock_pexpect = patch('stack.switch.x1052.pexpect').start()

# Raise an exeption when pexpect tries to spawn
mock_pexpect.spawn = Mock(side_effect=Exception)
