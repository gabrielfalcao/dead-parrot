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

import re
import md5
import random

import utils

def random_method():
    return re.search(r'[a-zA-Z]\w+', md5.new(str(random.random())).hexdigest()).group()

def test_random_method():
    got = random_method()
    assert isinstance(got, basestring), 'Should be string, got %s' % repr(got)

def test_utils_has_class_fake_getter():
    msg1 = 'deadparrot tests.utils module should have the class FakeGetter'
    assert hasattr(utils, 'FakeGetter'), msg1
    msg2 = 'deadparrot tests.utils.FakeGetter should be a class, got %r' % utils.FakeGetter
    assert isinstance(utils.FakeGetter, type), msg2

def test_fake_getter_gets_itself_infinitely_chained():
    getter = utils.FakeGetter()
    got = reduce(getattr, [random_method() for x in range(15)], getter)
    assert got is getter, 'Expected %r Got %s' % (getter, repr(got))

def test_fake_getter_gets_itself_infinitely_chained_can_be_called():
    getter = utils.FakeGetter()
    got = reduce(getattr, [random_method() for x in range(15)], getter)()
    assert got is getter, 'Expected %r Got %s' % (getter, repr(got))

