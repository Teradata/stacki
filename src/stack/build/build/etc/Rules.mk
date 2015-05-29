# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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


# --------------------------------------------------------------------- #
# Make a local copy of stylesheets for usersguides
# --------------------------------------------------------------------- #
DOCROOT = $(STACKBUILD)/src/roll/etc/doc

entities.sgml::
	touch $@
	for sgml in $(basename $(shell ls *.sgml)); do	\
		echo "<!ENTITY source-$$sgml SYSTEM \"$$sgml.sgml\">" >> $@; \
	done
	for roll in $(ROLL_REQUIRES); do \
		echo "<!ENTITY roll-$$roll-depend \"<row><entry namest="req">&roll-$$roll;</entry></row>\">" >> $@; \
	done
	for roll in $(ROLL_CONFLICTS); do \
		echo "<!ENTITY roll-$$roll-depend \"<row><entry namest="con">&roll-$$roll;</entry></row>\">" >> $@; \
	done
ifneq ($(ROLL_REQUIRES_FULL_OS),)
	@echo '<!ENTITY source-roll-overview-complete-os SYSTEM "roll-overview-complete-os.sgml">' >> $@
else
	@echo '<!ENTITY source-roll-overview-complete-os "">' >> $@
endif
	@echo '<!ENTITY document-rollname "$(ROLL)">' >> $@
	@echo '<!ENTITY document-version "$(VERSION)">' >> $@
	@echo '<!ENTITY document-version_name "$(RELEASE_NAME)">' >> $@
	@echo '<!ENTITY document-pubdate "$(PUBDATE)">' >> $@
	@echo '<!ENTITY document-year "$(YEAR)">' >> $@
	@echo '<!ENTITY document-copyright "$(COPYRIGHT)">' >> $@
	@echo '<!ENTITY summary-compatible "$(SUMMARY_COMPATIBLE)">' >> $@
	@echo '<!ENTITY summary-maintainer "$(SUMMARY_MAINTAINER)">' >> $@
	@echo '<!ENTITY summary-architecture "$(SUMMARY_ARCHITECTURE)">' >> $@
	@echo '<!ENTITY codename "$(CODENAME)">' >> $@
	cat $(DOCROOT)/overview-entities.sgml >> $@
	cat $(DOCROOT)/general-entities.sgml >> $@


predoctemplates::
	cp $(DOCROOT)/overview.sgml \
		roll-overview.sgml
	cp $(DOCROOT)/overview-complete-os.sgml \
		roll-overview-complete-os.sgml
	cp $(DOCROOT)/copyright-disclaimer.sgml \
		roll-copyright-disclaimer.sgml
	cp $(DOCROOT)/installing-standard.sgml \
		roll-installing-standard.sgml
	cp $(DOCROOT)/installing-onthefly.sgml \
		roll-installing-onthefly.sgml
	cp $(DOCROOT)/installing-not-onthefly.sgml \
		roll-installing-not-onthefly.sgml
	cp $(DOCROOT)/apachev2-copyright.sgml \
		roll-apachev2-copyright.sgml
	cp $(DOCROOT)/artistic-copyright.sgml \
		roll-artistic-copyright.sgml
	cp $(DOCROOT)/ggplv1-copyright.sgml \
		roll-ggplv1-copyright.sgml
	cp $(DOCROOT)/ggplv2-copyright.sgml \
		roll-ggplv2-copyright.sgml
	cp $(DOCROOT)/glgplv21-copyright.sgml \
		roll-glgplv21-copyright.sgml
	cp $(DOCROOT)/glgplv2-copyright.sgml \
		roll-glgplv2-copyright.sgml
	cp $(DOCROOT)/python2-copyright.sgml \
		roll-python2-copyright.sgml
	cp $(DOCROOT)/rocks-copyright.sgml \
		roll-rocks-copyright.sgml
	cp $(DOCROOT)/agplv30-copyright.sgml \
		roll-agplv30-copyright.sgml
	cp $(DOCROOT)/images/select-rolls.png \
		images/roll-select-rolls.png
	cp $(DOCROOT)/images/rocks.png \
		images/roll-rocks.png

rcldoc::
	cp $(DOCROOT)/genrcldocs .
	./genrcldocs $(ROLL)

predoc:: predoctemplates rcldoc entities.sgml rocks-copyright.txt
	if [ ! -f ./rocks.dsl ]; then cp $(DOCROOT)/rocks.dsl .; fi; 
	if [ ! -f ./rocks.css ]; then cp $(DOCROOT)/rocks.css .; fi; 
	if [ ! -d ./stylesheet-images ]; then \
           cp -r $(DOCROOT)/stylesheet-images .; \
           rm -rf ./stylesheet-images/CVS ; \
           for i in caution important note tip warning ; do \
               if [ -f ./stylesheet-images/$$i-no-alpha.png ] ; then \
                   cp ./stylesheet-images/$$i-no-alpha.png \
		   ./stylesheet-images/$$i.png ; \
               fi \
           done \
	fi


clean::
	@rm -rf rocks.dsl rocks.css stylesheet-images entities.sgml
	@rm -f roll-*.sgml
	@rm -f images/roll-*.png
	@rm -f genrcldocs



endif # __RULES_MK

