#
# Do not edit
#

%: %.py
	$(SED) $(SEDSCRIPT) $^ > $@
	chmod +x $@

%: %.sh
	$(SED) $(SEDSCRIPT) $^ > $@
	chmod +x $@

%: %.bash
	$(SED) $(SEDSCRIPT) $^ > $@
	chmod +x $@

%: %.csh
	$(SED) $(SEDSCRIPT) $^ > $@
	chmod +x $@

%: %.ksh
	$(SED) $(SEDSCRIPT) $^ > $@
	chmod +x $@

%: %.tcsh
	$(SED) $(SEDSCRIPT) $^ > $@
	chmod +x $@

%: %.pl
	$(SED) $(SEDSCRIPT) $^ > $@
	chmod +x $@

