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
from deadparrot.core.models import fields
from deadparrot.core.models import Model
from deadparrot.core.models import build_metadata
from deadparrot.core.models import Attribute
from deadparrot.core.models import DateTimeAttribute
from deadparrot.core.models import DateAttribute
from deadparrot.core.models import TimeAttribute
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

class TestBasicModel(object):
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

class TestModelInstrospection(object):#unittest.TestCase):
    def test_field_names(self):
        class Foo(Model):
            baz = fields.Field()

        foobar = Foo()
        self.assertEquals(foobar._meta._fields['baz'].name, 'baz')

class TestFields(unittest.TestCase):
    def init(self):
        class Person(Model):
            first_name = fields.CharField(max_length=40)
            last_name = fields.CharField(max_length=40)
            birthdate = fields.DateField(format="%d/%m/%Y")
            wakeup_at = fields.TimeField(format="%H:%M:%S")
            creation_date = fields.DateTimeField(format="%Y-%m-%d %H:%M:%S")
            wage = fields.DecimalField(max_digits=6, decimal_places=2)
            email = fields.EmailField()
            favorite_phrase = fields.CharField(max_length=0, validate=False)
            weight = fields.FloatField()
            married = fields.BooleanField(positives=["true", "yes"],
                                          negatives=["false", "not"])
            childrens = fields.IntegerField()
            cellphone = fields.PhoneNumberField(format="(00) 0000-0000")
            biography = fields.TextField()
            blog = fields.URLField(verify_exists=True)
            father = fields.ForeignKey('self')

            @property
            def full_name(self):
                return u"%s %s" % (self.first_name, self.last_name)

            def __unicode__(self):
                return "%s, son of %s" % (self.full_name, self.father.full_name)

            class Meta:
                fields_validation_policy = fields.VALIDATE_NONE

        self.PersonClass = Person

    def test_charfield_success(self):
        class Person(Model):
            first_name = fields.CharField(max_length=40)

        expected_dict = {'Person': {'first_name': u'John Doe'}}
        john = Person.from_dict(expected_dict)
        self.assertEquals(john.first_name, u'John Doe')
        self.assertEquals(john.to_dict(), expected_dict)

    def test_charfield_fail(self):
        class Person(Model):
            first_name = fields.CharField(max_length=10)

        fail_unicode_dict = {'Person': {'first_name': u'blah' * 4}}
        fail_int_dict = {'Person': {'first_name': 0000000}}
        fail_none_dict = {'Person': {'first_name': None}}
        fail_type_dict = {'Person': {'first_name': unicode}}
        self.assertRaises(fields.FieldValidationError,
                          Person.from_dict,
                          fail_unicode_dict)
        self.assertRaises(TypeError, Person.from_dict, fail_int_dict)
        self.assertRaises(TypeError, Person.from_dict, fail_none_dict)
        self.assertRaises(TypeError, Person.from_dict, fail_type_dict)

    def _test_datetimefield_success(self):
        class Person(Model):
            creation_date = fields.DateTimeField(\
                format="%Y-%m-%d %H:%M:%S")

        expected_dict = {'Person': {'creation_date':
                                    u'2009-03-29 14:38:20'}}
        john = Person.from_dict(expected_dict)
        self.assertEquals(john.birthdate,
                          datetime.strftime("'2009-03-29 14:38:20'",
                                            "%Y-%m-%d %H:%M:%S"))
        self.assertEquals(john.to_dict(), expected_dict)

    def test_types_successfully(self):
        pass
    def test_types_exceptions(self):
        pass


