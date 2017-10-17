# @copyright@
# @copyright@

bootstrap:
	$(STACKBUILD)/bin/package-install -m "Development Tools" "Infrastructure Server"
	$(STACKBUILD)/bin/package-install createrepo genisoimage git emacs vim
