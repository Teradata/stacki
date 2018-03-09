ROLLROOT = ../../../..
include $(STACKBUILD)/etc/CCRules.mk

build:
	tar xzf $(NAME)-$(VERSION).tar.gz
	(					\
		cd $(NAME)-$(VERSION)/src;	\
		$(MAKE);			\
	)

install::
	(					\
		cd $(NAME)-$(VERSION)/src;	\
		$(MAKE) INSTALL_MOD_PATH=$(ROOT)\
			install;		\
	)

clean::
	rm -rf $(NAME)-$(VERSION)
