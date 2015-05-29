MSGFMT		= /usr/bin/msgfmt
INSTALL		= install
LOCALDIR	= /usr/share/locale

ifdef __RULES_SOLARIS_MK
INSTALL = /usr/ucb/install
else
INSTALL = install
endif

build:: 
	for f in `find ./ -name "*.po"`; do \
		$(MSGFMT)  -o `basename $$f .po`.mo $$f ;\
	done

install:
	for f in `ls -1 *.mo`;do \
		mkdir -p $(ROOT)/usr/share/locale/`basename $$f .mo`/LC_MESSAGES/; \
		$(INSTALL) -m 0644  $$f $(ROOT)/usr/share/locale/`basename $$f .mo`/LC_MESSAGES/insert-ethers.mo ;\
	done

clean ::
	rm -f *.mo

