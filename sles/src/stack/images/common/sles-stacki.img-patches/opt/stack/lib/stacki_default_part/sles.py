sles11_default = [('/', 16000, 'xfs') ,
	 ('swap', 1000, 'swap') ,
	 ('/var', 16000, 'xfs') ,
	 ('/state/partition1', 0, 'xfs')]

sles11_uefi = [('/boot/efi', 256, 'vfat'),
	 ('/', 16000, 'xfs') ,
	 ('swap', 1000, 'swap') ,
	 ('/var', 16000, 'xfs') ,
	 ('/state/partition1', 0, 'xfs')]

sles12_default = sles11_default

sles12_uefi = sles11_uefi

default = sles12_default

