SHELL = /bin/bash

.DEFAULT_GOAL = environment
.PHONY = environment clean

bin/pip:
	python3 -m venv venv
	ln -s venv/bin bin

environment: bin/pip
	source ./bin/activate && pip install -r requirements.txt

clean:
	rm -rf bin venv .cache .vagrant test-suites/*/.cache
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d -print0 | xargs -0 rm -rf --
	find . -name '.pytest_cache' -type d -print0 | xargs -0 rm -rf --
