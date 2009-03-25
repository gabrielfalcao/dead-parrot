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

import unittest
from deadparrot.client.models import Model
from deadparrot.client.models import Attribute
from deadparrot.client.models import DateTimeAttribute
from deadparrot.client.models import DateAttribute
from deadparrot.client.models import TimeAttribute
from datetime import datetime, date, time

class TestAttributes(unittest.TestCase):
    def test_camel_name(self):
        nc = Attribute(unicode)
        nc.fill('my_over_long_attribute_name', 'Attribute Value')
        self.assertEquals(nc.camel_name, 'myOverLongAttributeName')

    def test_unicode(self):
        nc = Attribute(unicode)
        nc.fill('full_name', 'John Doe')
        self.assertEquals(nc.name, 'full_name')
        self.assertEquals(nc.camel_name, 'fullName')
        self.assertEquals(nc.value, u'John Doe')

    def test_float(self):
        nc = Attribute(float)
        nc.fill('weight', '120.53')
        self.assertEquals(nc.name, 'weight')
        self.assertEquals(nc.camel_name, 'weight')
        self.assertEquals(nc.value, 120.53)

    def test_int(self):
        nc = Attribute(int)
        nc.fill('age', '21.53')
        self.assertEquals(nc.name, 'age')
        self.assertEquals(nc.camel_name, 'age')
        self.assertEquals(nc.value, 21)

    def test_datetime(self):
        dta = DateTimeAttribute("%Y/%m/%d %H:%M:%S")
        dta.fill('creation_date', '2009/03/24 00:46:20')
        self.assertEquals(dta.name, 'creation_date')
        self.assertEquals(dta.camel_name, 'creationDate')
        self.assertEquals(dta.value.date(), datetime(2009, 3, 24).date())

    def test_date(self):
        dta = DateAttribute("%Y/%m/%d")
        dta.fill('creation_date', '2009/03/24')
        self.assertEquals(dta.name, 'creation_date')
        self.assertEquals(dta.camel_name, 'creationDate')
        self.assertEquals(dta.value, date(2009, 3, 24))

    def test_time(self):
        dta = TimeAttribute("%H:%M:%S")
        dta.fill('creation_time', '23:44:10')
        self.assertEquals(dta.value, time(hour=23, minute=44, second=10))

class TestModel(unittest.TestCase):
    def test_metadata(self):
        class Person(Model):
            class Meta:
                single_name = 'Person'
                plural_name = 'People'

        p = Person()
        self.failUnless(p._meta is not None)
        self.assertEquals(p._meta.single_name, 'Person')
        self.assertEquals(p._meta.plural_name, 'People')

    def test_meta_serialization(self):
        class Person(Model):
            name = Attribute(unicode)
            birthdate = DateAttribute("%d/%m/%Y")

        p = Person()
        p.name = "John Doe"
        p.birthdate = date(1988, 02, 10)

