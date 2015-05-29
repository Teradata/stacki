#! /opt/stack/bin/python
#
# ATLAS asks what type of x86 processor it should optimize for. here is
# the question it asks:
#
#	1. Other/UNKNOWN
#	2. AMD Athlon
#	3. 32 bit AMD Hammer
#	4. 64 bit AMD Hammer
#	5. Pentium PRO
#	6. Pentium II
#	7. Pentium III
#	8. Pentium 4
#	9. EM64T
#

AMD_Athlon = 2
AMD_Hammer_32 = 3
AMD_Hammer_64 = 4
Pentium_PRO = 5
Pentium_II = 6
Pentium_III = 7
Pentium_4 = 8
EM64T = 9

import string
import sys

#
# for intel processors, the format is (family, model, atlas-id)
#
processors = [
	('GenuineIntel', '6', '1', Pentium_PRO),
	('GenuineIntel', '6', '3', Pentium_II),
	('GenuineIntel', '6', '5', Pentium_II),
	('GenuineIntel', '6', '6', Pentium_II),
	('GenuineIntel', '6', '7', Pentium_III),
	('GenuineIntel', '6', '8', Pentium_III),
	('GenuineIntel', '6', '10', Pentium_III),
	('GenuineIntel', '6', '11', Pentium_III),
	('GenuineIntel', '15', '0', Pentium_4),
	('GenuineIntel', '15', '1', Pentium_4),
	('GenuineIntel', '15', '2', Pentium_4),
	('GenuineIntel', '15', '3', Pentium_4),

	('GenuineIntel', '15', '4', EM64T),

	# Athlon dual-core 32-bit mode
	('AuthenticAMD', '15', '75', AMD_Hammer_32),
	('AuthenticAMD', '15', '5', AMD_Hammer_32),  # Opteron in 32-bit mode

	('AuthenticAMD', '6', '10', AMD_Athlon),  # AMD Athlon MP 2800+
	('AuthenticAMD', '6', '8', AMD_Athlon),  # AMD Athlon MP 2200+
	('AuthenticAMD', '6', '6', AMD_Athlon),	# AMD Athlon MP
	('AuthenticAMD', '6', '4', AMD_Athlon),	# AMD Athlon
	('AuthenticAMD', '6', '2', AMD_Athlon)   # AMD Athlon
]

family = ''
model = ''
vendor = ''

file = open('/proc/cpuinfo', 'r')

for line in file.readlines():
	# print 'line: ', line

	tokens = string.split(line)

	if len(tokens) > 2:
		if tokens[0] == 'cpu' and tokens[1] == 'family':
			family = tokens[3]
		elif tokens[0] == 'model':
			model = tokens[2]
		elif tokens[0] == 'vendor_id':
			vendor = tokens[2]

		if family != '' and model != '' and vendor != '':
			for cpu in processors:
				ven, fam, mod, id = cpu

				if fam == family and mod == model \
						and ven == vendor:

					print id
					sys.exit(0)

#
# if we made it this far, we don't know what the processor is. output
# the unknown id
#
print '1'
