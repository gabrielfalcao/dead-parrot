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

clean:
	@echo "Cleaning up build and *.pyc files..."
	@find . -name '*.pyc' -exec rm -rf {} \;
	@rm -rf build

unit:
	@echo "Running unit tests..."
	@nosetests -s --with-coverage --cover-package tests/unit

functional:
	@echo "Running functional tests..."
	@nosetests -s --with-coverage --cover-package tests/functional

doctest:
	@test $$TERM == 'xterm' && echo -ne "\e[1;34m"
	@echo "Running doctests..."
	@test $$TERM == 'xterm' && echo -ne "\e[1;31m"
	@python -c "import doctest;doctest.testfile('./README.rst', verbose=False, report=True)"
	@test $$TERM == 'xterm' && echo -ne "\e[1;32m"
	@echo "tests passed!"
	@test $$TERM == 'xterm' && echo -ne "\e[0m"

test: unit functional doctest

build: clean test
	@test $$TERM == 'xterm' && echo -ne "\e[1;33m"
	@echo "Buiding dead-parrot..."
	@test $$TERM == 'xterm' && echo -ne "\e[1;31m"
	@python setup.py build
	@test $$TERM == 'xterm' && echo -ne "\e[1;37m"
	@echo "Built sucessfully."
	@test $$TERM == 'xterm' && echo -ne "\e[1;32m"
	@echo "Get it in `pwd`/build/lib/"
	@test $$TERM == 'xterm' && echo -ne "\e[0m"