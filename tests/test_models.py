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
from deadparrot.client.models import build_metadata
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
        dta2 = DateTimeAttribute("%Y/%m/%d %H:%M:%S")
        dta.fill('creation_date', '2009/03/24 00:46:20')
        self.assertEquals(dta.name, 'creation_date')
        self.assertEquals(dta.camel_name, 'creationDate')
        self.assertEquals(dta.value.date(), datetime(2009, 3, 24).date())
        self.assertRaises(TypeError, dta.fill, 'creation_date', 100.5)

    def test_date(self):
        dta1 = DateAttribute("%Y/%m/%d")
        dta2 = DateAttribute("%Y/%m/%d")
        dta1.fill('creation_date', '2009/03/24')
        dta2.fill('creation_date', date(2009, 3, 24))
        self.assertEquals(dta1.name, 'creation_date')
        self.assertEquals(dta1.camel_name, 'creationDate')
        self.assertEquals(dta1.value, date(2009, 3, 24))
        self.assertEquals(dta2.value, date(2009, 3, 24))
        self.assertRaises(TypeError, dta1.fill, 'creation_date', 100.5)

    def test_time(self):
        dta = TimeAttribute("%H:%M:%S")
        dta.fill('creation_time', '23:44:10')
        self.assertEquals(dta.value, time(hour=23, minute=44, second=10))
        self.assertRaises(TypeError, dta.fill, 'creation_time', 100.5)

    def test_unknown(self):
        nc = Attribute(object)
        self.assertRaises(TypeError, nc.fill, 'full_name', 'John Doe')

class TestModel(unittest.TestCase):
    def test_build_metadata(self):
        class Car(Model):
            pass

        class Meta:
            pass

        class Dummy:
            pass

        self.assertEquals(build_metadata(Car, Meta).single_name, 'Car')
        self.assertEquals(build_metadata(Car, Meta).plural_name, 'Cars')

    def test_metadata(self):
        class Person(Model):
            class Meta:
                single_name = 'Person'
                plural_name = 'People'

        p = Person()
        self.failUnless(p._meta is not None)
        self.assertEquals(p._meta.single_name, 'Person')
        self.assertEquals(p._meta.plural_name, 'People')

    def test_to_dict(self):
        class Person(Model):
            name = Attribute(unicode)
            birthdate = DateAttribute("%d/%m/%Y")

        p = Person()
        p.name = "John Doe"
        p.birthdate = date(1988, 02, 10)

        my_dict = {
            'Person': {
                'name': u"John Doe",
                'birthdate': u"10/02/1988"
            }
        }

        self.assertEquals(my_dict, p.to_dict())

    def test_set_to_dict(self):
        class Person(Model):
            name = Attribute(unicode)
            birthdate = DateAttribute("%d/%m/%Y")
            def __unicode__(self):
                return "<Person %s>" % self.name.value

            class Meta:
                plural_name = 'People'

        p1 = Person()
        p1.name = "John Doe"
        p1.birthdate = date(1988, 02, 10)

        p2 = Person()
        p2.name = "Mary Jane"
        p2.birthdate = date(1970, 12, 20)
        crowd = Person.Set([p1, p2])
        self.assertEquals(len(crowd), 2)
        for p in crowd:
            self.failUnless(isinstance(p, Person))

        my_dict = {
            'People': [
                {'Person': {
                    'name': u"John Doe",
                    'birthdate': u"10/02/1988"
                    }
                 },
                {'Person': {
                    'name': u"Mary Jane",
                    'birthdate': u"20/12/1970"
                     }
                 }
            ]
        }

        self.assertEquals(my_dict, crowd.to_dict())

    def test_from_dict(self):
        class Person(Model):
            name = Attribute(unicode)
            birthdate = DateAttribute("%d/%m/%Y")

        my_dict = {
            'Person': {
                'name': u"John Doe",
                'birthdate': u"10/02/1988"
            }
        }

        p = Person.from_dict(my_dict)
        self.failUnless(isinstance(p, Person))
        self.assertEquals(p.name.value, u"John Doe")
        self.assertEquals(p.birthdate.value, date(1988, 02, 10))

    def test_set_from_dict(self):
        class Person(Model):
            name = Attribute(unicode)
            birthdate = DateAttribute("%d/%m/%Y")
            class Meta:
                plural_name = 'People'
        my_dict = {
            'People': [
                {'Person': {
                    'name': u"John Doe",
                    'birthdate': u"10/02/1988"
                    }
                 },
                {'Person': {
                    'name': u"Mary Jane",
                    'birthdate': u"20/12/1970"
                     }
                 }
            ]
        }
        People = Person.Set()
        crowd = People.from_dict(my_dict)
        self.failUnless(isinstance(crowd, People))
        self.assertEquals(crowd[0].name.value, u"John Doe")
        self.assertEquals(crowd[0].birthdate.value, date(1988, 02, 10))
