#! /opt/stack/bin/python3

import sys
from stack.password import Password


def usage():
	print('`{0}` alone will generate a random cleartext password string'.format(sys.argv[0]))
	print('`{0} crypt` will generate a random hashed password string'.format(sys.argv[0]))
	print('`{0} crypt $CLEARTEXT`` alone will generate a hashed from $CLEARTEXT'.format(sys.argv[0]))


if __name__ == '__main__':
	# if no args specified, generate a random 'cleartext' password string
	# if argv[1] is 'crypt', encrypt a random password in the standard unix crypt format
	# if argv[2] exists, encrypt that instead of generating a random cleartext password

	p = Password()

	cleartext_password = None
	password_type = None

	if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
		usage()
		sys.exit()
	if len(sys.argv) > 1:
		password_type = sys.argv[1].strip('\n')
		if password_type != 'crypt':
			usage()
			sys.exit()
	if len(sys.argv) > 2:
		cleartext_password = sys.argv[2].strip('\n')

	if password_type == 'crypt':
		print(p.get_crypt_pw(cleartext_password))
	else:
		print(p.get_cleartext_pw(cleartext_password))
