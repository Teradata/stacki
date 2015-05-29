build:
	gunzip -c wget-$(VERSION).tar.gz | $(TAR) -xf -
	( 					\
		cd wget-$(VERSION);		\
		./configure --prefix=$(PKGROOT)	\
			LDFLAGS=-L/usr/sfw/lib	\
			CPPFLAGS=-I/usr/sfw/include;\
		$(MAKE);			\
	)

