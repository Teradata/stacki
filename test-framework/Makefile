SHELL = /bin/bash

.DEFAULT_GOAL = environment
.PHONY = environment clean

bin/pip: VERSION = 15.1.0

bin/pip:
	curl --retry 10 -fsO `curl --retry 10 -fs https://pypi.org/pypi/virtualenv/$(VERSION)/json | grep -o -E '"url":"https://files.pythonhosted.org/packages/[0-9a-f]+/[0-9a-f]+/[0-9a-f]+/virtualenv-$(VERSION).tar.gz"' | head -n 1 | cut -d '"' -f 4`
	tar xvzf virtualenv-$(VERSION).tar.gz
	python2.7 virtualenv-$(VERSION)/virtualenv.py venv
	rm -rf virtualenv-$(VERSION)/ virtualenv-$(VERSION).tar.gz
	ln -s venv/bin bin

environment: bin/pip
	source ./bin/activate && pip install -r requirements.txt
	
clean:
	rm -rf bin venv .cache .vagrant
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d -print0 | xargs -0 rm -rf --
	find . -name '.pytest_cache' -type d -print0 | xargs -0 rm -rf --
