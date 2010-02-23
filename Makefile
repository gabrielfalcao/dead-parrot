# Copyright (C) 2009 Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

ifeq ($(shell echo $$TERM),xterm)
    normal := "\e[0m"
    red    := "\e[1;31m"
    green  := "\e[1;32m"
    yellow := "\e[1;33m"
    blue   := "\e[1;34m"
    white  := "\e[1;37m"
else
    normal :=
    red    :=
    green  :=
    yellow :=
    blue   :=
    white  :=
endif
nose_command := nosetests --verbosity=2 -s --with-coverage --cover-package=deadparrot.server --cover-package=deadparrot.serialization --cover-package=deadparrot.models

help:
	@echo "Available targets are:"
	@echo "all                                          build files"
	@echo "clean                                        removes unused files"
	@echo "functional                                   runs functional tests"
	@echo "doctests                                     runs doctests"
	@echo "acceptance                                   runs acceptance tests"
	@echo "test                                         runs unit tests"
	@echo "build                                        build files"

all: build

clean:
	@echo "Cleaning up build files..."
	@rm -rf build
	@echo "Cleaning up *.pyc files..."
	@find . -name '*.pyc' -exec rm -rf {} \;
	@echo "Cleaning up *.json files..."
	@find . -name '*.json' -exec rm -rf {} \;

unit:
	@echo "Running unit tests..."
	@$(nose_command) tests/unit

functional: clean run_server
	@echo "Running functional tests..."
	@$(nose_command) tests/functional

doctest:
	@echo -ne $(blue)
	@echo "Running doctests..."
	@echo -ne $(red)
	@python -c "import doctest;doctest.testfile('./README.rst', verbose=False, report=True)"
	@echo -ne $(green)
	@echo "tests passed!"
	@echo -ne $(normal)

acceptance:
	@echo -ne $(yellow)
	@echo "Running acceptance tests (all codes from documentation)..."
	@echo -ne $(red)
	@python -c "import doctest;doctest.testfile('./docs/serialization.rst', verbose=False, report=True)"
	@echo -ne $(green)
	@echo "tests passed!"
	@echo -ne $(normal)

test: functional unit doctest acceptance

build: clean test
	@echo -ne $(yellow)
	@echo "Buiding dead-parrot..."
	@echo -ne $(red)
	@python setup.py build > /dev/null
	@echo -ne $(yellow)
	@echo "DONE."
	@echo -ne $(blue)
	@echo "Ensuring that the build is fine ..."
	@echo -ne $(red)
	@cp -drf tests `pwd`/build/lib/
	@cd `pwd`/build/lib/ && nosetests tests && rm -rf tests
	@echo -ne $(yellow)
	@echo "DONE."
	@echo -ne $(white)
	@echo "Built successfully."
	@echo -ne $(green)
	@echo "Get it in `pwd`/build/lib/"
	@echo -ne $(normal)

run_server: kill_server
	@echo "Running builtin HTTP server ..."
	@(cd tests/functional/parrotserver && bob go 2>&1) > log.txt &
	@sleep 5

kill_server:
	@echo -n "Shutting down builtin HTTP server ..."
	@(ps aux | egrep 'bob go' | egrep -v grep | awk '{ print $$2 }' | xargs kill -9 2>&1 | exit 0) > /dev/null
	@echo " Done."
