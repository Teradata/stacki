# @SI_Copyright@
# @SI_Copyright@

dump-info bootstrap rpm pkg install-rpm clean nuke:
	for x in *; do					\
		if [ -d $$x ]; then			\
			(cd $$x; $(MAKE) $@); 		\
		fi;					\
	done
