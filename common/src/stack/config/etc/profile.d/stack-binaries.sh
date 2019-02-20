export STACK_ROOT=/opt/stack

if [ -d $STACK_ROOT/bin ]; then
	export PATH=$PATH:$STACK_ROOT/bin:$STACK_ROOT/go/bin
fi

if [ -d $STACK_ROOT/sbin ]; then
	export PATH=$PATH:$STACK_ROOT/sbin
fi

if [ -d $STACK_ROOT/lib/pkgconfig ]; then
	export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$STACK_ROOT/lib/pkgconfig
fi
