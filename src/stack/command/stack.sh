#! /bin/bash

if [ "$STACKPYTHON" == "3" ]; then
	PYTHON=/opt/stack/bin/python3
else
	PYTHON=/opt/stack/bin/python
fi

if [ -x ./stack.py ]; then
	STACK=./stack.py
else
	STACK=/opt/stack/bin/stack
fi

$PYTHON $STACK $@
