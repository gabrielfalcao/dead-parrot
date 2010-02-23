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

from nose.tools import assert_equals
from utils import assert_raises

from deadparrot.models import Attribute
from deadparrot.models import DateTimeAttribute
from deadparrot.models import DateAttribute
from deadparrot.models import TimeAttribute
from datetime import datetime, date, time

def test_camel_name():
    nc = Attribute(unicode)
    nc.fill('my_over_long_attribute_name', 'Attribute Value')
    assert_equals(nc.camel_name, 'myOverLongAttributeName')

def test_unicode():
    nc = Attribute(unicode)
    nc.fill('full_name', 'John Doe')
    assert_equals(nc.name, 'full_name')
    assert_equals(nc.camel_name, 'fullName')
    assert_equals(nc.value, u'John Doe')

def test_float():
    nc = Attribute(float)
    nc.fill('weight', '120.53')
    assert_equals(nc.name, 'weight')
    assert_equals(nc.camel_name, 'weight')
    assert_equals(nc.value, 120.53)

def test_int():
    nc = Attribute(int)
    nc.fill('age', '21.53')
    assert_equals(nc.name, 'age')
    assert_equals(nc.camel_name, 'age')
    assert_equals(nc.value, 21)

def test_datetime_success():
    dta = DateTimeAttribute("%Y/%m/%d %H:%M:%S")

    iters = '2009/03/24 00:46:20', \
            datetime.strptime('2009/03/24 00:46:20',
                              "%Y/%m/%d %H:%M:%S")
    for val in iters:
        dta.fill('creation_date', val)
        assert_equals(dta.name, 'creation_date')
        assert_equals(dta.camel_name, 'creationDate')
        assert_equals(dta.value.date(),
                          datetime(2009, 3, 24).date())

def test_datetime_raises():
    dta = DateTimeAttribute("%Y/%m/%d %H:%M:%S")

    iters = '2009/03/24 00:46:20', \
            datetime.strptime('2009/03/24 00:46:20',
                              "%Y/%m/%d %H:%M:%S")
    for val in iters:
        dta.fill('creation_date', val)
        assert_raises(TypeError,
                          dta.fill,
                          'creation_date',
                          100.5)

def test_date():
    dta1 = DateAttribute("%Y/%m/%d")
    dta2 = DateAttribute("%Y/%m/%d")
    dta1.fill('creation_date', '2009/03/24')
    dta2.fill('creation_date', date(2009, 3, 24))
    assert_equals(dta1.name, 'creation_date')
    assert_equals(dta1.camel_name, 'creationDate')
    assert_equals(dta1.value, date(2009, 3, 24))
    assert_equals(dta2.value, date(2009, 3, 24))
    assert_raises(TypeError, dta1.fill, 'creation_date', 100.5)

def test_time():
    dta1 = TimeAttribute("%H:%M:%S")
    dta2 = TimeAttribute("%H:%M:%S")
    dta1.fill('creation_time', '23:44:10')
    dta2.fill('creation_time', time(hour=23, minute=44, second=10))
    assert_equals(dta1.value, time(hour=23, minute=44, second=10))
    assert_equals(dta2.value, time(hour=23, minute=44, second=10))
    assert_raises(TypeError, dta1.fill, 'creation_time', 100.5)

def test_unsupported_type():
    nc = Attribute(object)
    assert_raises(TypeError, nc.fill, 'full_name', 'John Doe')
