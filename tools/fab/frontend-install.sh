#! /bin/bash

# setup any_python
# this lets frontend-install.py be written in a python2 and python3
# and can use /usr/bin/env any_python for the shebang
# note `then :` is the bash equivalent of `pass`. skip linking if link exists
if [[ -n "$(which any_python)" ]]
then
	:
elif [[ -n "$(which python)" ]]
then
	ln -s $(which python) /usr/bin/any_python
elif [[ -n "$(which python3)" ]]
then
	ln -s $(which python3) /usr/bin/any_python
fi

# Assume frontend-install.py is sitting next to where frontend-install.sh is, and run it
# from that path.
"$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/frontend-install.py "$@"
