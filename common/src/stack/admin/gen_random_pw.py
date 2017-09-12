#!@PYTHON@

from __future__ import print_function
import sys
from stack.password import Password


if __name__ == '__main__':
	# if no args specified, generate a random 'cleartext' password string
	# if argv[1] is 'crypt', encrypt a random password in the standard unix crypt format
	# if argv[2] exists, encrypt that instead of generating a random cleartext password
	p = Password()

	cleartext_password = None
	password_type = None

	if len(sys.argv) > 1:
		password_type = sys.argv[1].strip()
	if len(sys.argv) > 2:
		cleartext_password = sys.argv[2].strip()

	if password_type == 'crypt':
		print(p.get_crypt_pw(cleartext_password).decode())
	else:
		print(p.get_cleartext_pw(cleartext_password).decode())
