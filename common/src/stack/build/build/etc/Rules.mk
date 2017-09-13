# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

ifndef __RULES_MK
__RULES_MK = yes

SHELL = /bin/sh


# --------------------------------------------------------------------- #
# Site specific variables 
# --------------------------------------------------------------------- #
ifeq ($(VENDOR),)
VENDOR    = StackIQ
endif
ifeq ($(COPYRIGHT),)
COPYRIGHT = StackIQ
endif
ifneq ($(COPYRIGHT.EXTRA),)
COPYRIGHT += / $(COPYRIGHT.EXTRA)
endif
DATE      = $(shell date +"%B %d %Y")
TIME	  = $(shell date +"%T")
TZ	  = $(shell date +"%Z")
PACKAGE   = StackIQ
BUGREPORT = info@stackiq.com
WEBSITE   = www.stackiq.com
FTPSITE   = ftp.stackiq.com
MAILTO    = info@stackiq.com

# --------------------------------------------------------------------- #
# Compilers
# --------------------------------------------------------------------- #

YUICOMPRESSOR = $(STACKBUILD)/bin/yuicompressor-2.4.2.jar
YUICOMPRESS   = java -jar $(YUICOMPRESSOR)

CC = gcc
CFLAGS    = -g -Wall
CPPFLAGS  = -DVERSION="\"$(VERSION)\""

RPCGEN = rpcgen
RPCGENFLAGS = -C -T

MAN2HTML = man2html
SED = sed

# --------------------------------------------------------------------- #
# Default rule
# --------------------------------------------------------------------- #
.DEFAULT_GOAL := default
default: pkg

# --------------------------------------------------------------------- #
# Read in the standard makefiles
# --------------------------------------------------------------------- #
include $(STACKBUILD)/etc/stack-version.mk
include $(STACKBUILD)/etc/python.mk
-include version.mk
-include .buildenv-$(ROLL)/version.mk 

# --------------------------------------------------------------------- #
# Use this target to make sure only the root account is building
# packages.  Some work without but many require root, standardize
# and always require root.
# --------------------------------------------------------------------- #

.PHONY: root-check
root-check:
	@if [ "$(USERID)" != "0" ] ; then \
		echo ; \
		echo ; \
		echo ERROR - YOU MUST BE ROOT TO BUILD PACKAGES; \
		echo ; \
		echo ; \
		exit 1 ; \
	fi

# --------------------------------------------------------------------- #
# Get the absolute path for the root of the sandbox
# --------------------------------------------------------------------- #
STACKBUILD.ABSOLUTE = $(shell cd $(STACKBUILD); pwd)

# --------------------------------------------------------------------- #
# Compute the package name based on the last two directory names
# --------------------------------------------------------------------- #

PATH.CHILD	= $(notdir $(CURDIR))
PATH.PARENTPATH	= $(dir $(CURDIR))
PATH.PARENTLIST	= $(subst /, ,$(dir $(CURDIR)))
PATH.PARENT	= $(word $(words $(PATH.PARENTLIST)), $(PATH.PARENTLIST))
PATH.GRANDPARENTLIST = $(subst $(PATH.PARENT),,$(PATH.PARENTLIST))
PATH.GRANDPARENT     = $(word $(words $(PATH.GRANDPARENTLIST)), \
	$(PATH.GRANDPARENTLIST))

ifeq ($(PATH.PARENT),src)
NAME ?= $(PATH.CHILD)
endif

ifeq ($(PATH.PARENT),BUILD)
NAME ?= $(shell echo $(PATH.CHILD) | $(SED) 's/-$(VERSION)$$//')
endif

NAME ?= $(PATH.PARENT)-$(PATH.CHILD)

.PHONY: dump-info
dump-info::
	@echo "DIR             = $(CURDIR)"
	@echo "ROLL            = $(ROLL)"
	@echo "STACK           = $(STACK)"
	@echo "NAME            = $(NAME)"
	@echo "RELEASE         = $(RELEASE)"
	@echo "VERSION         = $(VERSION)"
	@echo "OS              = $(OS)"
	@echo "ARCH            = $(ARCH)"
	@echo "ORDER           = $(ORDER)"
	@echo "ROLL.MEMBERSHIP = $(ROLL.MEMBERSHIP)"

.PHONY: pretar
pretar::

# --------------------------------------------------------------------- #
# Artifactory Support
# --------------------------------------------------------------------- #
AFURL = https://sdartifact.td.teradata.com/artifactory/pkgs-generic-snapshot-sd/stacki/git

ifneq ($(AFS),)
.PHONY: afup
afup:
	for o in $(AFS); do curl -H X-JFrog-Art-Api:$(AFKEY) -T$$o $(AFURL)/; done

pretar::
	for o in $(AFS); do curl -H X-JFrog-Art-Api:$(AFKEY) -O $(AFURL)/$$o; done

clean::
	-rm -f $(AFS)
endif

# --------------------------------------------------------------------- #
# Architecture
# --------------------------------------------------------------------- #

ARCH = $(shell $(STACKBUILD.ABSOLUTE)/bin/arch)
OS   = $(shell $(STACKBUILD.ABSOLUTE)/bin/os)

-include $(ARCH).mk
-include $(OS).mk
-include $(STACKBUILD)/etc/Rules-$(OS).mk

ifeq ($(ARCH),x86_64)
LIBARCH = lib64
else
LIBARCH = lib
endif

# --------------------------------------------------------------------- #
# Build man pages and HTML pages
#
# To create a manpage and the html version simple place a file called
# <foo>.<sec>.in in the current directory.  <foo> is the name of the
# manpage, and <sec> is the section name (e.g. 2).  The below rules
# build a makefile that picks up these files and even installs them as
# part of the RPM.
#
# --------------------------------------------------------------------- #

MANSECTIONS = "1 2 3 4 5 6 7 8 l"
MANPATH  = $(ROOT)/$(PKGROOT)/man
HTMLPATH = $(ROOT)/$(PKGROOT)/doc

AWKHTML  = 'BEGIN { state=0; } /<HTML>/ { state=1; } { if (state) { print; }}'

SEDMAN   = \
	-e 's%@PATH.CHILD@%$(PATH.CHILD)%g' \
	-e 's%@PATH.PARENT@%$(PATH.PARENT)%g' \
	-e 's%@NAME@%$(NAME)%g' \
	-e 's%@VERSION@%$(VERSION)%g' \
	-e 's%@RELEASE@%$(RELEASE)%g' \
	-e 's%@COPYRIGHT@%$(COPYRIGHT)%g' \
	-e 's%@DATE@%$(DATE)%g' \
	-e 's%@PACKAGE@%$(PACKAGE)%g' \
	-e 's%@BUGREPORT@%$(BUGREPORT)%g' \
	-e 's%@WEBSITE@%$(WEBSITE)%g' \
	-e 's%@FTPSITE@%$(FTPSITE)%g' \
	-e 's%@MAILTO@%$(MAILTO)%g'

include .buildenv-$(ROLL)/install.mk

man: $(MANPAGES)

.PHONY: install-man
.PHONY: install-html
install-man::
install-html::

HTMLDOC = $(wildcard *.html.in)
ifneq ($(HTMLDOC),)
%.html: %.html.in
	$(SED) $(SEDMAN) $^ > $@

clean::
	-rm -f $(basename $(HTMLDOC))
endif

.buildenv-$(ROLL)/install.mk: Makefile
	@if [ ! -d .buildenv-$(ROLL) ]; then mkdir .buildenv-$(ROLL); fi
	@echo $(MANSECTIONS) | awk '\
	BEGIN { \
		RS=" "; FS="\n"; \
		print "#\n# Do not edit\n#\n"; \
	} \
	{ \
		printf "MANPAGES.%s=$$(basename $$(wildcard *.%s.in))\n", \
			$$1, $$1; \
		printf "MANPAGES +=$$(MANPAGES.%s)\n", $$1; \
		printf "\n"; \
		printf "ifneq ($$(MANPAGES.%s),)\n", $$1; \
		printf "HTMLPAGES.%s=$$(addsuffix .html, $$(MANPAGES.%s))\n", \
			$$1, $$1; \
		printf "install-man:: install-man-%s\n", $$1; \
		printf "install-html:: install-html-%s\n", $$1; \
		printf "%%.%s: %%.%s.in\n", $$1, $$1; \
		printf "\t$$(SED) $$(SEDMAN) $$^ > $$@\n"; \
		printf "%%.%s.html: %%.%s\n", $$1, $$1; \
		printf "\t$$(MAN2HTML) $$^ | awk $$(AWKHTML) > $$@\n"; \
		printf "install-man-%s: $$(MANPAGES.%s)\n", $$1, $$1; \
		printf "\tif [ ! -d $$(MANPATH)/man%s ]; then \\\n", $$1; \
		printf "\t\tmkdir -p $$(MANPATH)/man%s; \\\n", $$1; \
		printf "\t\tchmod 755 $$(MANPATH)/man%s; \\\n", $$1; \
		printf "\tfi\n"; \
		printf "\t$$(INSTALL) -ma+r $$^ $$(MANPATH)/man%s\n", $$1; \
		printf "install-html-%s: $$(HTMLPAGES.%s)\n", $$1, $$1; \
		printf "\tif [ ! -d $$(HTMLPATH) ]; then \\\n"; \
		printf "\t\tmkdir $$(HTMLPATH); \\\n"; \
		printf "\t\tchmod 755 $$(HTMLPATH); \\\n"; \
		printf "\tfi\n"; \
		printf "\t$$(INSTALL) -ma+r $$^ $$(HTMLPATH)/\n"; \
		printf "clean::\n"; \
		printf "\trm -f $$(MANPAGES.%s)\n", $$1; \
		printf "\trm -f $$(HTMLPAGES.%s)\n", $$1; \
		printf "docs:: $$(MANPAGES.%s) $$(HTMLPAGES.%s)\n", $$1, $$1; \
		printf "endif\n"; \
		printf "\n"; \
	}' > $@

install:: install-man install-html

# --------------------------------------------------------------------- #
# For Scripts insert the version number
# --------------------------------------------------------------------- #

SCRIPTTYPES = py sh bash csh ksh tcsh pl
SEDSCRIPT = \
	-e s%@NAME@%$(NAME)%g \
	-e s%@VERSION@%$(VERSION)%g \
	-e s%@PROJECT_NAME@%$(PROJECT_NAME)%g \
	-e s%@PYTHON@%$(PY.PATH)%g 

include .buildenv-$(ROLL)/scripts.mk

.PHONY: scripts
scripts:: $(SCRIPTS)

clean::
	@rm -rf .buildenv-$(ROLL)

.buildenv-$(ROLL)/scripts.mk: Makefile
	@if [ ! -d .buildenv-$(ROLL) ]; then mkdir .buildenv-$(ROLL); fi
	@echo $(SCRIPTTYPES) | awk '\
	BEGIN { \
		RS=" "; FS="\n"; \
		print "#\n# Do not edit\n#\n"; \
	} \
	{ \
		printf "%%: %%.%s\n", $$1; \
		printf "\t$$(SED) $$(SEDSCRIPT) $$^ > $$@\n"; \
		printf "\tchmod +x $$@\n"; \
		printf "\n"; \
	}' > $@

# --------------------------------------------------------------------- #
# Bootstrap
# --------------------------------------------------------------------- #

bootstrap-$(OS)::
bootstrap:: bootstrap-$(OS)

# --------------------------------------------------------------------- #
# Build the XML config file
# --------------------------------------------------------------------- #

RCFILES = $(addsuffix rc, $(SCRIPTS))
SEDRC   = $(SEDSCRIPT)

include .buildenv-$(ROLL)/rcfiles.mk

.buildenv-$(ROLL)/rcfiles.mk: Makefile
	@if [ ! -d .buildenv-$(ROLL) ]; then mkdir .buildenv-$(ROLL); fi
	@echo $(RCFILES) | awk '					\
		BEGIN {							\
			RS=" "; FS="\n";				\
		}							\
		{							\
			printf "%s: %s.xml\n", $$1, $$1;		\
			printf "\t$$(SED) $$(SEDRC) $$^ > $$@\n";	\
		}' > $@


endif # __RULES_MK

