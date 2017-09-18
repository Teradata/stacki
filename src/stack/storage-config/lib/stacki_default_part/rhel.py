rhel7_default = [('biosboot', 1, 'biosboot'),
	 ('/', 16000, 'ext4') ,
	 ('swap', 1000, 'swap') ,
	 ('/var', 16000, 'xfs') ,
	 ('/state/partition1', 0, 'xfs')]

rhel7_uefi = [('/boot/efi', 256, 'msdos'),
	 ('/', 16000, 'ext4') ,
	 ('swap', 1000, 'swap') ,
	 ('/var', 16000, 'xfs') ,
	 ('/state/partition1', 0, 'xfs')]

rhel6_default = [('/', 16000, 'ext4') ,
	 ('swap', 1000, 'swap') ,
	 ('/var', 16000, 'xfs') ,
	 ('/state/partition1', 0, 'xfs')]

rhel6_uefi = rhel7_uefi

default = rhel7_default
