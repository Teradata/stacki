import pytest
from stack.checklist import Backend, State, StateMessage
from checklist import Checklist
import copy
import sys
import time

class TestChecklistMain:

	def test_getBackendByMac(self):
		sys.path.append('/opt/stack/bin')
		c = Checklist()
		b  = Backend('host-8', 'default', 'default', 'sles')
		b1 = Backend('host-9', 'default', 'default', 'sles')
		b.macList = ['aa:bb:aa:aa:bb:aa']
		b.ipList  = ['8.8.8.8']
		b1.macList = ['aa:bb:aa:aa:bb:ee']
		b1.ipList = ['8.8.8.9']
		c.ipBackendMap = {'8.8.8.8' : b, '8.8.8.9' : b1}

		assert c.getBackendByMac('aa:bb:aa:aa:bb:ee') == b1
		assert c.getBackendByMac('aa:bb:aa:aa:bb:ef') == None

	def test_processTftp(self):
		sys.path.append('/opt/stack/bin')
		c = Checklist()
		b  = Backend('host-8', 'default', 'default', 'sles')
		b1 = Backend('host-9', 'default', 'default', 'sles')
		b.macList = ['aa:bb:aa:aa:bb:aa']
		b.ipList  = ['8.8.8.8']
		b1.macList = ['aa:bb:aa:aa:bb:ee']                
		b1.ipList = ['8.8.8.9']
		c.ipBackendMap = {'8.8.8.8' : b, '8.8.8.9' : b1}
		b.installKernel = 'vmlinuz-sles-12-sp3-x86_64'
		b.installRamdisk = 'initrd-sles-12-sp3-x86_64'
		b.osKernel = ''
		b.osRamdisk = ''
		b1.osKernel = 'chain.c32'
		b1.osRamdisk = ''
		b1.installKernel = 'mlinuz-sles-12-sp3-x86_64'
		b1.installRamdisk = ''

		sm = StateMessage('8.8.8.8', State.TFTP_RRQ, False, 
			time.time(), 'pxelinux.cfg/01-52-54-00-de-20-b1')
		assert c.processTftp(sm) == Checklist.IGNORE_TFTP_MSG

		sm1 = StateMessage('8.8.8.8', State.TFTP_RRQ, False,
			time.time(), 'initrd-sles-12-sp3-x86_64')
		assert c.processTftp(sm1) == Checklist.SUCCESS_TFTP \
			and sm1.state == State.Initrd_RRQ
		sm2 = StateMessage('8.8.8.9', State.TFTP_RRQ, False,
			time.time(), 'initrd-sles-12-sp3-x86')
		assert c.processTftp(sm2) == Checklist.REFRESH_STATE
		sm3 = StateMessage('8.8.8.8', State.TFTP_RRQ, False,
			time.time(), 'vmlinuz-sles-12-sp3-x86_64')
		assert c.processTftp(sm3) == Checklist.SUCCESS_TFTP \
			and sm3.state == State.VMLinuz_RRQ_Install
		sm4 = StateMessage('8.8.8.9', State.TFTP_RRQ, False,
			time.time(), 'chain.c32')
		assert c.processTftp(sm4) == Checklist.SUCCESS_TFTP and \
			sm4.state == State.Rebooting_HDD

	def test_restoreDhcpMsgs(self):
		sys.path.append('/opt/stack/bin')
		c = Checklist()
		b  = Backend('host-8', 'default', 'default', 'sles')
		b1 = Backend('host-9', 'default', 'default', 'sles')
		b.macList = ['aa:bb:aa:aa:bb:aa']
		b.ipList  = ['8.8.8.8']
		b1.macList = ['aa:bb:aa:aa:bb:ee']
		b1.ipList = ['8.8.8.9']
		c.ipBackendMap = {'8.8.8.8' : b, '8.8.8.9' : b1}
		b.installKernel = 'vmlinuz-sles-12-sp3-x86_64'
		b.installRamdisk = 'initrd-sles-12-sp3-x86_64'
		b.osKernel = ''
		b.osRamdisk = ''
		b1.osKernel = 'chain.c32'
		b1.osRamdisk = ''
		b1.installKernel = 'mlinuz-sles-12-sp3-x86_64'
		b1.installRamdisk = ''

		sm1 = StateMessage('8.8.8.8', State.Set_DB_Partitions, False,
			time.time())
		sm2 = StateMessage('8.8.8.8', State.Set_Bootaction_OS, False,
			time.time())
		b.stateArr.append(sm1)
		b.stateArr.append(sm2)
		dhcp1 = StateMessage('8.8.8.8', State.DHCPDISCOVER, False,
			time.time())
		b.dhcpStateArr.append(dhcp1)
		dhcp2 = StateMessage('8.8.8.8', State.DHCPREQUEST, False,
			time.time())
		b.dhcpStateArr.append(dhcp2)

		arr1 = copy.deepcopy(b.dhcpStateArr)
		stArr1 = copy.deepcopy(b.stateArr)
		c.restoreDhcpMsgs(sm1)
		assert arr1 == b.dhcpStateArr
		assert stArr1 == b.stateArr

		sm3 = StateMessage('8.8.8.9', State.SSH_Open, False,
			time.time())
		b1.stateArr.append(sm3)
		sm4 = StateMessage('8.8.8.9', State.AUTOINST_Present, False,
			time.time())
		b1.stateArr.append(sm4)
		b1.dhcpStateArr = b.dhcpStateArr
		dhcp1.time = time.time()
		dhcp2.time = time.time()
		sm1 = StateMessage('8.8.8.9', State.TFTP_RRQ, False,
			time.time())
		c.restoreDhcpMsgs(sm1)
		assert len(b1.dhcpStateArr) == 0
