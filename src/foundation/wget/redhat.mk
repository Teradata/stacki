build:
	gunzip -c wget-$(VERSION).tar.gz | $(TAR) -xf -
	( 					\
		cd wget-$(VERSION);		\
		PATH=/opt/rocks/bin:$$PATH ./configure --prefix=$(PKGROOT);\
		$(MAKE);			\
	)
