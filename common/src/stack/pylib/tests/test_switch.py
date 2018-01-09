#!/opt/stack/bin/python3.6

import stack.switch as ethernet_switch
from stack.api import Call


#switch_ip = '39.87.48.58'
switch_ip = '192.168.2.1'


switch = ethernet_switch.SwitchDellX1052(switch_ip, 'admin', 'admin')

def test_tftp_ip():
	switch.set_tftp_ip('1.1.1.1')
	assert switch.stacki_server_ip == '1.1.1.1'

def test_vlan_parse():
	assert switch._vlan_parser('3-7,9-10,44,3') == '3,4,5,6,7,9,10,44'
	assert switch._vlan_parser('3-7,9-10,44') == '3,4,5,6,7,9,10,44'

def test_get_port():
	assert switch.get_port_from_interface(
		'interface gigabitethernet1/0/20'
		) == '20'
	assert switch.get_port_from_interface(
		'interface gigabitethernet2/3/40'
		) == '40'
