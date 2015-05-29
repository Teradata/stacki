export STACK_ROOT=/opt/stack

if [ -d $STACK_ROOT/bin ]; then
	export PATH=$PATH:$STACK_ROOT/bin
fi

if [ -d $STACK_ROOT/sbin ]; then
	export PATH=$PATH:$STACK_ROOT/sbin
fi


