#
# Do not edit
#

MANPAGES.1=$(basename $(wildcard *.1.in))
MANPAGES +=$(MANPAGES.1)

ifneq ($(MANPAGES.1),)
HTMLPAGES.1=$(addsuffix .html, $(MANPAGES.1))
install-man:: install-man-1
install-html:: install-html-1
%.1: %.1.in
	$(SED) $(SEDMAN) $^ > $@
%.1.html: %.1
	$(MAN2HTML) $^ | awk $(AWKHTML) > $@
install-man-1: $(MANPAGES.1)
	if [ ! -d $(MANPATH)/man1 ]; then \
		mkdir -p $(MANPATH)/man1; \
		chmod 755 $(MANPATH)/man1; \
	fi
	$(INSTALL) -ma+r $^ $(MANPATH)/man1
install-html-1: $(HTMLPAGES.1)
	if [ ! -d $(HTMLPATH) ]; then \
		mkdir $(HTMLPATH); \
		chmod 755 $(HTMLPATH); \
	fi
	$(INSTALL) -ma+r $^ $(HTMLPATH)/
clean::
	rm -f $(MANPAGES.1)
	rm -f $(HTMLPAGES.1)
docs:: $(MANPAGES.1) $(HTMLPAGES.1)
endif

MANPAGES.2=$(basename $(wildcard *.2.in))
MANPAGES +=$(MANPAGES.2)

ifneq ($(MANPAGES.2),)
HTMLPAGES.2=$(addsuffix .html, $(MANPAGES.2))
install-man:: install-man-2
install-html:: install-html-2
%.2: %.2.in
	$(SED) $(SEDMAN) $^ > $@
%.2.html: %.2
	$(MAN2HTML) $^ | awk $(AWKHTML) > $@
install-man-2: $(MANPAGES.2)
	if [ ! -d $(MANPATH)/man2 ]; then \
		mkdir -p $(MANPATH)/man2; \
		chmod 755 $(MANPATH)/man2; \
	fi
	$(INSTALL) -ma+r $^ $(MANPATH)/man2
install-html-2: $(HTMLPAGES.2)
	if [ ! -d $(HTMLPATH) ]; then \
		mkdir $(HTMLPATH); \
		chmod 755 $(HTMLPATH); \
	fi
	$(INSTALL) -ma+r $^ $(HTMLPATH)/
clean::
	rm -f $(MANPAGES.2)
	rm -f $(HTMLPAGES.2)
docs:: $(MANPAGES.2) $(HTMLPAGES.2)
endif

MANPAGES.3=$(basename $(wildcard *.3.in))
MANPAGES +=$(MANPAGES.3)

ifneq ($(MANPAGES.3),)
HTMLPAGES.3=$(addsuffix .html, $(MANPAGES.3))
install-man:: install-man-3
install-html:: install-html-3
%.3: %.3.in
	$(SED) $(SEDMAN) $^ > $@
%.3.html: %.3
	$(MAN2HTML) $^ | awk $(AWKHTML) > $@
install-man-3: $(MANPAGES.3)
	if [ ! -d $(MANPATH)/man3 ]; then \
		mkdir -p $(MANPATH)/man3; \
		chmod 755 $(MANPATH)/man3; \
	fi
	$(INSTALL) -ma+r $^ $(MANPATH)/man3
install-html-3: $(HTMLPAGES.3)
	if [ ! -d $(HTMLPATH) ]; then \
		mkdir $(HTMLPATH); \
		chmod 755 $(HTMLPATH); \
	fi
	$(INSTALL) -ma+r $^ $(HTMLPATH)/
clean::
	rm -f $(MANPAGES.3)
	rm -f $(HTMLPAGES.3)
docs:: $(MANPAGES.3) $(HTMLPAGES.3)
endif

MANPAGES.4=$(basename $(wildcard *.4.in))
MANPAGES +=$(MANPAGES.4)

ifneq ($(MANPAGES.4),)
HTMLPAGES.4=$(addsuffix .html, $(MANPAGES.4))
install-man:: install-man-4
install-html:: install-html-4
%.4: %.4.in
	$(SED) $(SEDMAN) $^ > $@
%.4.html: %.4
	$(MAN2HTML) $^ | awk $(AWKHTML) > $@
install-man-4: $(MANPAGES.4)
	if [ ! -d $(MANPATH)/man4 ]; then \
		mkdir -p $(MANPATH)/man4; \
		chmod 755 $(MANPATH)/man4; \
	fi
	$(INSTALL) -ma+r $^ $(MANPATH)/man4
install-html-4: $(HTMLPAGES.4)
	if [ ! -d $(HTMLPATH) ]; then \
		mkdir $(HTMLPATH); \
		chmod 755 $(HTMLPATH); \
	fi
	$(INSTALL) -ma+r $^ $(HTMLPATH)/
clean::
	rm -f $(MANPAGES.4)
	rm -f $(HTMLPAGES.4)
docs:: $(MANPAGES.4) $(HTMLPAGES.4)
endif

MANPAGES.5=$(basename $(wildcard *.5.in))
MANPAGES +=$(MANPAGES.5)

ifneq ($(MANPAGES.5),)
HTMLPAGES.5=$(addsuffix .html, $(MANPAGES.5))
install-man:: install-man-5
install-html:: install-html-5
%.5: %.5.in
	$(SED) $(SEDMAN) $^ > $@
%.5.html: %.5
	$(MAN2HTML) $^ | awk $(AWKHTML) > $@
install-man-5: $(MANPAGES.5)
	if [ ! -d $(MANPATH)/man5 ]; then \
		mkdir -p $(MANPATH)/man5; \
		chmod 755 $(MANPATH)/man5; \
	fi
	$(INSTALL) -ma+r $^ $(MANPATH)/man5
install-html-5: $(HTMLPAGES.5)
	if [ ! -d $(HTMLPATH) ]; then \
		mkdir $(HTMLPATH); \
		chmod 755 $(HTMLPATH); \
	fi
	$(INSTALL) -ma+r $^ $(HTMLPATH)/
clean::
	rm -f $(MANPAGES.5)
	rm -f $(HTMLPAGES.5)
docs:: $(MANPAGES.5) $(HTMLPAGES.5)
endif

MANPAGES.6=$(basename $(wildcard *.6.in))
MANPAGES +=$(MANPAGES.6)

ifneq ($(MANPAGES.6),)
HTMLPAGES.6=$(addsuffix .html, $(MANPAGES.6))
install-man:: install-man-6
install-html:: install-html-6
%.6: %.6.in
	$(SED) $(SEDMAN) $^ > $@
%.6.html: %.6
	$(MAN2HTML) $^ | awk $(AWKHTML) > $@
install-man-6: $(MANPAGES.6)
	if [ ! -d $(MANPATH)/man6 ]; then \
		mkdir -p $(MANPATH)/man6; \
		chmod 755 $(MANPATH)/man6; \
	fi
	$(INSTALL) -ma+r $^ $(MANPATH)/man6
install-html-6: $(HTMLPAGES.6)
	if [ ! -d $(HTMLPATH) ]; then \
		mkdir $(HTMLPATH); \
		chmod 755 $(HTMLPATH); \
	fi
	$(INSTALL) -ma+r $^ $(HTMLPATH)/
clean::
	rm -f $(MANPAGES.6)
	rm -f $(HTMLPAGES.6)
docs:: $(MANPAGES.6) $(HTMLPAGES.6)
endif

MANPAGES.7=$(basename $(wildcard *.7.in))
MANPAGES +=$(MANPAGES.7)

ifneq ($(MANPAGES.7),)
HTMLPAGES.7=$(addsuffix .html, $(MANPAGES.7))
install-man:: install-man-7
install-html:: install-html-7
%.7: %.7.in
	$(SED) $(SEDMAN) $^ > $@
%.7.html: %.7
	$(MAN2HTML) $^ | awk $(AWKHTML) > $@
install-man-7: $(MANPAGES.7)
	if [ ! -d $(MANPATH)/man7 ]; then \
		mkdir -p $(MANPATH)/man7; \
		chmod 755 $(MANPATH)/man7; \
	fi
	$(INSTALL) -ma+r $^ $(MANPATH)/man7
install-html-7: $(HTMLPAGES.7)
	if [ ! -d $(HTMLPATH) ]; then \
		mkdir $(HTMLPATH); \
		chmod 755 $(HTMLPATH); \
	fi
	$(INSTALL) -ma+r $^ $(HTMLPATH)/
clean::
	rm -f $(MANPAGES.7)
	rm -f $(HTMLPAGES.7)
docs:: $(MANPAGES.7) $(HTMLPAGES.7)
endif

MANPAGES.8=$(basename $(wildcard *.8.in))
MANPAGES +=$(MANPAGES.8)

ifneq ($(MANPAGES.8),)
HTMLPAGES.8=$(addsuffix .html, $(MANPAGES.8))
install-man:: install-man-8
install-html:: install-html-8
%.8: %.8.in
	$(SED) $(SEDMAN) $^ > $@
%.8.html: %.8
	$(MAN2HTML) $^ | awk $(AWKHTML) > $@
install-man-8: $(MANPAGES.8)
	if [ ! -d $(MANPATH)/man8 ]; then \
		mkdir -p $(MANPATH)/man8; \
		chmod 755 $(MANPATH)/man8; \
	fi
	$(INSTALL) -ma+r $^ $(MANPATH)/man8
install-html-8: $(HTMLPAGES.8)
	if [ ! -d $(HTMLPATH) ]; then \
		mkdir $(HTMLPATH); \
		chmod 755 $(HTMLPATH); \
	fi
	$(INSTALL) -ma+r $^ $(HTMLPATH)/
clean::
	rm -f $(MANPAGES.8)
	rm -f $(HTMLPAGES.8)
docs:: $(MANPAGES.8) $(HTMLPAGES.8)
endif

MANPAGES.l=$(basename $(wildcard *.l.in))
MANPAGES +=$(MANPAGES.l)

ifneq ($(MANPAGES.l),)
HTMLPAGES.l=$(addsuffix .html, $(MANPAGES.l))
install-man:: install-man-l
install-html:: install-html-l
%.l: %.l.in
	$(SED) $(SEDMAN) $^ > $@
%.l.html: %.l
	$(MAN2HTML) $^ | awk $(AWKHTML) > $@
install-man-l: $(MANPAGES.l)
	if [ ! -d $(MANPATH)/manl ]; then \
		mkdir -p $(MANPATH)/manl; \
		chmod 755 $(MANPATH)/manl; \
	fi
	$(INSTALL) -ma+r $^ $(MANPATH)/manl
install-html-l: $(HTMLPAGES.l)
	if [ ! -d $(HTMLPATH) ]; then \
		mkdir $(HTMLPATH); \
		chmod 755 $(HTMLPATH); \
	fi
	$(INSTALL) -ma+r $^ $(HTMLPATH)/
clean::
	rm -f $(MANPAGES.l)
	rm -f $(HTMLPAGES.l)
docs:: $(MANPAGES.l) $(HTMLPAGES.l)
endif

