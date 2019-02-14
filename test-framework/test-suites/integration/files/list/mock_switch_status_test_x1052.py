from unittest.mock import Mock, patch, mock_open


# Intercept pexpect calls
patch('stack.switch.x1052.pexpect').start()

# We also don't need to sleep
patch('stack.switch.x1052.time').start()

# Switch data to mock MAC address table
SWITCH_DATA = """
                                             Flow Link          Back   Mdix
Port     Type         Duplex  Speed Neg      ctrl State       Pressure Mode
-------- ------------ ------  ----- -------- ---- ----------- -------- -------
gi1/0/1  1G-Copper      --      --     --     --  Down           --     --
gi1/0/2  1G-Copper    Full    1000  Enabled  Off  Up          Disabled Off
gi1/0/3  1G-Copper    Full    1000  Enabled  Off  Up          Disabled On
te1/0/1  10G-Fiber      --      --     --     --  Down           --     --
"""

# Return our SWITCH_DATA during a read
patch('stack.switch.x1052.open', mock_open(read_data=SWITCH_DATA)).start()
