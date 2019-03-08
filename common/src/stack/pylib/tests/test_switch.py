#!/opt/stack/bin/python3.7

from stack.switch.x1052 import SwitchDellX1052
from stack.api import Call


#switch_ip = '39.87.48.58'
switch_ip = '192.168.2.1'


switch = SwitchDellX1052(switch_ip, 'admin', 'admin')

def test_tftp_ip():
	switch.set_tftp_ip('1.1.1.1')
	assert switch.stacki_server_ip == '1.1.1.1'
