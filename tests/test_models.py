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
from decimal import Decimal

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

    def test_unsupported_type(self):
        nc = Attribute(object)
        self.assertRaises(TypeError, nc.fill, 'full_name', 'John Doe')

class TestBasicModel(unittest.TestCase):
    def test_build_metadata(self):
        class Car(Model):
            pass

        self.assertEquals(build_metadata(Car, {}).single_name, 'Car')
        self.assertEquals(build_metadata(Car, {}).plural_name, 'Cars')

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
            name = fields.CharField(max_length=20)
            birthdate = fields.DateField(format="%d/%m/%Y")

        p = Person()
        p.name = u"John Doe"
        p.birthdate = date(1988, 02, 10)

        my_dict = {
            'Person': {
                'name': u"John Doe",
                'birthdate': u"10/02/1988"
            }
        }

        self.assertEquals(my_dict, p.to_dict())

    def test_from_dict(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")

        my_dict = {
            'Person': {
                'name': u"John Doe",
                'birthdate': u"10/02/1988"
            }
        }

        p = Person.from_dict(my_dict)
        self.failUnless(isinstance(p, Person))
        self.assertEquals(p.name, u"John Doe")
        self.assertEquals(p.birthdate, date(1988, 02, 10))

    def test_from_dict_fail(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")

        my_dict = {
            'Blah': {
                'name': u"John Doe",
                'birthdate': u"10/02/1988"
            }
        }

        self.assertRaises(TypeError, Person.from_dict, my_dict)

class TestModelInstrospection(unittest.TestCase):
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

    def test_field_fail(self):
        self.assertRaises(TypeError, fields.Field, validate=None)

    def test_charfield_fail_construct(self):
        self.assertRaises(TypeError, fields.CharField, max_length=None)

    def test_datetimefield_fail_construct(self):
        self.assertRaises(TypeError, fields.DateTimeField, format=None)

    def test_charfield_success(self):
        class Person(Model):
            first_name = fields.CharField(max_length=40)

        person_dict = {'Person': {'first_name': u'John Doe'}}
        john = Person.from_dict(person_dict)
        self.assertEquals(john.first_name, u'John Doe')
        self.assertEquals(john.to_dict(), person_dict)

    def test_charfield_success_validate(self):
        class Person(Model):
            first_name = fields.CharField(max_length=5)
            class Meta:
                validate_none = True

        class Car(Model):
            brand = fields.CharField(max_length=2, validate=False)

        person_dict = {'Person': {'first_name': u'John Doe'}}
        car_dict = {'Car': {'brand': u'Chevy'}}
        john = Person.from_dict(person_dict)
        chevy = Car.from_dict(car_dict)
        self.assertEquals(john.first_name, u'John Doe')
        self.assertEquals(john.to_dict(), person_dict)
        self.assertEquals(chevy.brand, u'Chevy')
        self.assertEquals(chevy.to_dict(), car_dict)

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

    def test_datetimefield_success(self):
        class Person(Model):
            creation_date = fields.DateTimeField(\
                format="%Y-%m-%d %H:%M:%S")

        expected_dict = {'Person': {'creation_date':
                                    u'2009-03-29 14:38:20'}}
        john = Person.from_dict(expected_dict)
        self.assertEquals(john.creation_date,
                          datetime.strptime("2009-03-29 14:38:20",
                                            "%Y-%m-%d %H:%M:%S"))
        self.assertEquals(john.to_dict(), expected_dict)

    def test_datetimefield_fail_format(self):
        class Person(Model):
            creation_date = fields.DateTimeField(\
                format="any wrong format")

        expected_dict = {'Person': {'creation_date':
                                    u'2009-03-29 14:38:20'}}
        self.assertRaises(fields.FieldValidationError,
                          Person.from_dict,
                          expected_dict)

    def test_datetimefield_fail_types(self):
        class Person(Model):
            creation_date = fields.DateTimeField(format="%Y%m%d")

        fail_dict_int = {'Person': {'creation_date': 100000}}
        self.assertRaises(TypeError, Person.from_dict, fail_dict_int)

    def test_datetimefield_fail_format_type(self):
        def make_class():
            class Person(Model):
                creation_time = fields.DateTimeField(format=None)

        self.assertRaises(TypeError, make_class)


    def test_datefield_success(self):
        class Person(Model):
            creation_date = fields.DateField(format="%Y-%m-%d")

        expected_dict = {'Person': {'creation_date':
                                    u'2009-03-29'}}
        john = Person.from_dict(expected_dict)
        self.assertEquals(john.creation_date,
                          datetime.strptime("2009-03-29",
                                            "%Y-%m-%d").date())
        self.assertEquals(john.to_dict(), expected_dict)

    def test_datefield_fail_format(self):
        class Person(Model):
            creation_date = fields.DateField(\
                format="any wrong format")

        expected_dict = {'Person': {'creation_date':
                                    u'2009-03-29 14:38:20'}}
        self.assertRaises(fields.FieldValidationError,
                          Person.from_dict,
                          expected_dict)

    def test_datefield_fail_types(self):
        class Person(Model):
            creation_date = fields.DateField(format="%Y%m%d")

        fail_dict_int = {'Person': {'creation_date': 100000}}
        self.assertRaises(TypeError, Person.from_dict, fail_dict_int)

    def test_timefield_success(self):
        class Person(Model):
            creation_time = fields.TimeField(format="%H:%M:%S")

        expected_dict = {'Person': {'creation_time':
                                    u'15:54:56'}}
        john = Person.from_dict(expected_dict)
        self.assertEquals(john.creation_time,
                          datetime.strptime("15:54:56",
                                            "%H:%M:%S").time())
        self.assertEquals(john.to_dict(), expected_dict)

    def test_timefield_fail_format(self):
        class Person(Model):
            creation_time = fields.TimeField(\
                format="any wrong format")

        expected_dict = {'Person': {'creation_time':
                                    u'2009-03-29 14:38:20'}}
        self.assertRaises(fields.FieldValidationError,
                          Person.from_dict,
                          expected_dict)

    def test_timefield_fail_format_date(self):
        class Person(Model):
            creation_time = fields.TimeField(format="%Y%m%d")

        fail_dict_int = {'Person': {'creation_time': "10:10:10"}}
        self.assertRaises(ValueError, Person.from_dict, fail_dict_int)

    def test_decimalfield_success(self):
        class Person(Model):
            first_name = fields.CharField(max_length=20, validate=False)
            wage = fields.DecimalField(max_digits=6, decimal_places=2)

        person_dict = {'Person': {'first_name': u'John Doe',
                                  'wage': '4000.55'}}

        john = Person.from_dict(person_dict)
        self.assertEquals(john.first_name, u'John Doe')
        self.assertEquals(john.wage, Decimal("4000.55"))
        self.assertEquals(john.to_dict(), person_dict)

    def test_decimalfield_metadata(self):
        class Person(Model):
            wage = fields.DecimalField(max_digits=6, decimal_places=2)

        person_dict = {'Person': {'wage': '4000.55'}}

        john = Person.from_dict(person_dict)
        self.assertEquals(john.wage, Decimal("4000.55"))
        self.assertEquals(john._meta._fields['wage'].max_digits, 6)
        self.assertEquals(john._meta._fields['wage'].decimal_places, 2)

    def test_decimalfield_fail(self):
        class Person(Model):
            first_name = fields.CharField(max_length=20, validate=False)
            wage = fields.DecimalField(max_digits=2, decimal_places=2)

        person_dict = {'Person': {'first_name': u'John Doe',
                                  'wage': '4000.55'}}

        self.assertRaises(fields.FieldValidationError, Person.from_dict, person_dict)

    def test_decimalfield_fail_from_dict(self):
        class Person(Model):
            wage = fields.DecimalField(max_digits=2, decimal_places=2)

        fail_dict_weird = {'Person': {'wage': "10:10:10"}}
        self.assertRaises(fields.FieldValidationError, Person.from_dict, fail_dict_weird)

    def test_types_successfully(self):
        pass

    def test_types_exceptions(self):
        pass
