setenv STACK_ROOT /opt/stack

if ( -d $STACK_ROOT/bin ) then
	setenv PATH "${PATH}:$STACK_ROOT/bin"
endif

if ( -d $STACK_ROOT/sbin ) then
	setenv PATH "${PATH}:$STACK_ROOT/sbin"
endif


