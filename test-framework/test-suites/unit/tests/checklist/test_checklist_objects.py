import pytest
from stack.checklist import Backend, State, StateMessage, StateSequence
import time

class TestBackend:
	
	def test_isKnownState(self):
		b = Backend('sd-stacki-111', 'default', 'default', 'sles')
		sm1 = StateMessage('10.25.241.111', State.DHCPDISCOVER, False, time.time())
		sm2 = StateMessage('10.25.241.111', State.Profile_XML_Sent, False, time.time())
		b.stateArr.append(sm1)
		b.stateArr.append(sm2)

		sm3 = StateMessage('10.25.241.111', State.Rebooting_HDD, False, time.time())
		sm4 = StateMessage('10.25.241.111', State.Profile_XML_Sent, True, time.time())

		assert b.isKnownState(sm3.state) == False
		assert b.isKnownState(sm4.state) == True

		sm2.isError = True
		assert b.isKnownState(sm4.state) == False

	def test_isPostPkgInstallStage(self):
		b = Backend('sd-stacki-111', 'default', 'default', 'sles')
		sm1 = StateMessage('10.25.241.111', State.DHCPDISCOVER, False, time.time())
		sm2 = StateMessage('10.25.241.111', State.Profile_XML_Sent, False, time.time())
		b.stateArr.append(sm1)
		b.stateArr.append(sm2)
		assert b.isPostPkgInstallStage() == False

		sm3 = StateMessage('10.25.241.111', State.Ludicrous_Populated, False, time.time())
		sm4 = StateMessage('10.25.241.111', State.Set_Bootaction_OS, False, time.time())
		b.stateArr.append(sm3)
		b.stateArr.append(sm4)
		assert b.isPostPkgInstallStage() == True

	def test_lastSuccessfulState(self):
		b = Backend('sd-stacki-111', 'default', 'default', 'sles')
		assert b.lastSuccessfulState() == None

		sm1 = StateMessage('10.25.241.111', State.DHCPDISCOVER, False, time.time())
		b.stateArr.append(sm1)
		assert b.lastSuccessfulState() == sm1

		sm2 = StateMessage('10.25.241.111', State.Profile_XML_Sent, True, time.time())
		b.stateArr.append(sm2)
		assert b.lastSuccessfulState() == sm1

	def test_copyAttributes(self):
		b = Backend('sd-stacki-111', 'default', 'default', 'redhat')
		sm1 = StateMessage('10.25.241.111', State.DHCPDISCOVER, False, time.time())
		sm2 = StateMessage('10.25.241.111', State.Profile_XML_Sent, False, time.time())
		b.stateArr.append(sm1)
		b.stateArr.append(sm2)
		b.ipList = ['10.25.241.111']
		b.macList = ['ac:de:ef:dd:11:11']
		b.installKernel = 'kernel1'
		b.installRamdisk = 'ramdisk1'

		b1 = Backend('sd-stacki-112', 'default', 'default', 'redhat')
		smb1 = StateMessage('10.25.241.112', State.DHCPOFFER, False, time.time())
		b1.stateArr.append(smb1)
		b1.ipList = ['10.25.241.112']
		b1.macList = ['ac:de:ef:dd:11:12']
		b1.installKernel = 'kernel2'
		b1.installRamdisk = 'ramdisk2'
		b.copyAttributes(b1)

		assert b.hostName == 'sd-stacki-112'
		assert b.ipList[0] == '10.25.241.112'
		assert b.macList[0] == 'ac:de:ef:dd:11:12'
		assert b.installKernel == 'kernel2'
		assert b.installRamdisk == 'ramdisk2'
		assert b.stateArr[0].state == State.DHCPDISCOVER

class TestStateSequence:

	def test_nextExpectedState(self):
		assert StateSequence.nextExpectedState(State.TFTP_RRQ, 'redhat', '6') == None
		assert StateSequence.nextExpectedState(State.Set_Bootaction_OS, 'sles', '12.x') == State.Rebooting_HDD
		assert StateSequence.nextExpectedState(State.Rebooting_HDD, 'sles', '12.x') != State.DHCPDISCOVER

	def text_getTimeThreshold(self):
		assert StateSequence.getTimeThreshold(State.TFTP_RRQ, 'redhat', '6') == None
		assert StateSequence.getTimeThreshold(State.Set_Bootaction_OS, 'sles', '12.x') == 210

class TestStateMessage:

	def test_isEqual(self):
		sm1 = StateMessage('10.25.241.111', State.DHCPDISCOVER, False, time.time())
		sm2 = StateMessage('10.25.241.111', State.Profile_XML_Sent, False, time.time())
		assert sm1 != sm2

		sm3 = StateMessage('10.25.241.111', State.Set_Bootaction_OS, True, time.time())
		sm4 = StateMessage('10.25.241.111', State.Set_Bootaction_OS, False, time.time())
		assert sm3 != sm4

		sm3.isError = False
		assert sm3 == sm4
