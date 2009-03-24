# -*- coding: utf-8; -*-
#
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

import os
import re
import sys
import unittest

from glob import glob

def get_test_modules():
    for filename in glob("tests/test_*.py"):
        filename = filename[6:-3]
        if re.search("^\w[\w_]+$", filename):
            module = __import__('tests.%s' % filename)
            yield unittest.TestLoader().loadTestsFromModule(getattr(module, filename))

def test_suite():
    return unittest.TestSuite([t for t in get_test_modules()])
