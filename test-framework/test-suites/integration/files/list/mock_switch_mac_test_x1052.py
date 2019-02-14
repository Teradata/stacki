from unittest.mock import Mock, patch, mock_open


# Intercept pexpect calls
patch('stack.switch.x1052.pexpect').start()

# We also don't need to sleep
patch('stack.switch.x1052.time').start()

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
"""

# Return our SWITCH_DATA during a read
patch('stack.switch.x1052.open', mock_open(read_data=SWITCH_DATA)).start()
