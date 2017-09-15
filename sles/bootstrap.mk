GROUPS=32bit Basis-Devel SDK-C-C++

PACKAGES=rpm-build libzip2 apache2 squashfs cmake apache2-devel createrepo asciidoc xmlto readline-devel slang-devel popt-devel

$(GROUPS):
	zypper in -y -t pattern $@

$(PACKAGES):
	zypper in -y $@

