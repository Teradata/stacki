SRCVERSION	= 3.10.2
SRCFILE		= pygobject-$(SRCVERSION).tar.xz
UNPACK		= xzcat
PREP		= yum install -y gobject-introspection-devel cairo-gobject-devel
