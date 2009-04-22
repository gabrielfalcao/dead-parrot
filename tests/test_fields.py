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
import pmock
from urllib2 import URLError
from deadparrot import models
from deadparrot.models import fields
from deadparrot.models import Model
from datetime import date, time, datetime
from decimal import Decimal

class TestFieldsBasicBehavior(unittest.TestCase):
    """
    Tests if the fields works with the simpliest uses: to/from a dict
    which means "meta-serialization", and tests if
    their values are working well when getting/setting
    """
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
                                          negatives=["false", "no"])
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
        self.assertRaises(TypeError, fields.Field, primary_key=None)

    def test_charfield_fail_construct(self):
        self.assertRaises(TypeError, fields.CharField, max_length=None)

    def test_datetimefield_fail_construct(self):
        self.assertRaises(TypeError, fields.DateTimeField, format=None)

    def test_charfield_success(self):
        class Person(Model):
            first_name = fields.CharField(max_length=40, primary_key=True)

        person_dict = {'Person': {'first_name': u'John Doe'}}
        john = Person.from_dict(person_dict)
        self.assertEquals(john.first_name, u'John Doe')
        self.assertEquals(john.to_dict(), person_dict)
        self.assertEquals(john._meta._fields['first_name'].primary_key, True)

    def test_charfield_success_validate(self):
        class Person(Model):
            first_name = fields.CharField(max_length=5)
            class Meta:
                fields_validation_policy = models.VALIDATE_NONE

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
        self.assertEquals(john._meta._fields['creation_date'].primary_key,
                          False)

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

        self.assertRaises(fields.FieldValidationError,
                          Person.from_dict, person_dict)

    def test_decimalfield_raises_on_construct(self):
        self.assertRaises(TypeError, fields.DecimalField,
                          max_digits="two", decimal_places=None)

    def test_decimalfield_raises_on_setattr(self):
        class Person(Model):
            wage = fields.DecimalField(decimal_places=2, max_digits=6)

        expected_dict = {'Person': {'wage': None}}

        self.assertRaises(TypeError,
                          Person.from_dict,
                          expected_dict)

    def test_decimalfield_fail_on_set(self):
        class Person(Model):
            wage = fields.DecimalField(max_digits=6, decimal_places=2)

        person_dict = {'Person': {'wage': '4000.55'}}

        man = Person.from_dict(person_dict)
        self.assertRaises(fields.FieldValidationError,
                          setattr, man, 'wage', '10:10:10')

    def test_decimalfield_fail_from_dict(self):
        class Person(Model):
            wage = fields.DecimalField(max_digits=2, decimal_places=2)

        fail_dict_weird = {'Person': {'wage': "10:10:10"}}
        self.assertRaises(fields.FieldValidationError, Person.from_dict, fail_dict_weird)

    def test_emailfield_success(self):
        class Person(Model):
            first_name = fields.CharField(max_length=20, validate=False)
            email = fields.EmailField()

        person_dict = {'Person': {'first_name': u'John Doe',
                                  'email': 'johndoe@jdfake.net'}}

        john = Person.from_dict(person_dict)
        self.assertEquals(john.first_name, u'John Doe')
        self.assertEquals(john.email, 'johndoe@jdfake.net')
        self.assertEquals(john.to_dict(), person_dict)

    def test_emailfield_validate_fail_on_set(self):
        class Person(Model):
            email = fields.EmailField()

        person_dict = {'Person': {'email': 'johndoe@jdfake.net'}}

        john = Person.from_dict(person_dict)
        self.assertRaises(fields.FieldValidationError,
                          setattr, john, 'email',
                          'testesadasdsad.sdsad.asdasd')

    def test_emailfield_fail_on_validate(self):
        class Person(Model):
            email = fields.EmailField()

        dicts = [{'Person': {'email': 'johndoejdfakenet'}},
                 {'Person': {'email': 'dfdsf@@sdsd.com'}},
                 {'Person': {'email': 'a@s.c'}},
                 {'Person': {'email': 'asdas.xsad.xom'}},
                 {'Person': {'email': 'johndoejdfak.enet'}},]

        for person_dict in dicts:
            try:
                Person.from_dict(person_dict)
                self.fail("Should raise exception when serializing" \
                          " from %r" % person_dict)
            except fields.FieldValidationError:
                pass

    def test_emailfield_fail_on_validate(self):
        class Person(Model):
            email = fields.EmailField()

        person_dict = {'Person': {'email': None}}
        self.assertRaises(TypeError, Person.from_dict, person_dict)

    def test_emailfield_fail_construct(self):
        self.assertRaises(TypeError, fields.EmailField, max_length=None)

    def test_integerfield_success(self):
        class Person(Model):
            childrens = fields.IntegerField()

        person_dict = {'Person': {'childrens': 3}}

        john = Person.from_dict(person_dict)
        self.assertEquals(john.childrens, 3)
        self.assertEquals(john.to_dict(), person_dict)

    def test_integerfield_fail_on_validate(self):
        class Person(Model):
            childrens = fields.IntegerField()

        person_dict = {'Person': {'childrens': None}}
        self.assertRaises(fields.FieldValidationError,
                          Person.from_dict,
                          person_dict)

    def test_floatfield_success(self):
        class Person(Model):
            weight = fields.FloatField()

        person_dict = {'Person': {'weight': 3.2}}

        john = Person.from_dict(person_dict)
        self.assertEquals(john.weight, 3.2)
        self.assertEquals(john.to_dict(), person_dict)

    def test_floatfield_fail_on_validate(self):
        class Person(Model):
            weight = fields.FloatField()

        person_dict = {'Person': {'weight': None}}
        self.assertRaises(fields.FieldValidationError,
                          Person.from_dict,
                          person_dict)

    def test_booleanfield_success(self):
        class Person(Model):
            married = fields.BooleanField(positives=["true", "yes"],
                                          negatives=["false", "no"])

        person_dict = {'Person': {'married': True}}

        john = Person.from_dict(person_dict)
        self.assertEquals(john.married, True)
        self.assertEquals(john.to_dict(), person_dict)

    def test_booleanfield_fail(self):
        class Person(Model):
            married = fields.BooleanField(positives=["true", "yes"],
                                          negatives=["false", "no"])

        person_dict = {'Person': {'married': None}}

        self.assertRaises(TypeError, Person.from_dict, person_dict)

    def test_booleanfield_fail_construct(self):
        self.assertRaises(TypeError,
                          fields.BooleanField,
                          negatives=None,
                          positives=None)

    def test_phonenumberfield_success_maxlength(self):
        class Person(Model):
            cellphone = fields.PhoneNumberField( \
                format="(00) 0000-0000",
                max_length=20
            )

        person_dict = {'Person': {'cellphone': "(21) 9966-6699"}}

        john = Person.from_dict(person_dict)
        self.assertEquals(john.cellphone, "(21) 9966-6699")
        self.assertEquals(john.to_dict(), person_dict)

    def test_phonenumberfield_success(self):
        class Person(Model):
            cellphone = fields.PhoneNumberField(format="(00) 0000-0000")

        person_dict = {'Person': {'cellphone': "(21) 9966-6699"}}

        john = Person.from_dict(person_dict)
        self.assertEquals(john.cellphone, "(21) 9966-6699")
        self.assertEquals(john.to_dict(), person_dict)


    def test_phonenumberfield_fail_construct(self):
        self.assertRaises(TypeError,
                          fields.PhoneNumberField,
                          format=None,
                          charfield=None)
        self.assertRaises(TypeError,
                          fields.PhoneNumberField,
                          charfield=None)
        self.assertRaises(TypeError,
                          fields.PhoneNumberField,
                          format=None)

    def test_phonenumberfield_fail_validate(self):
        class Person(Model):
            cellphone = fields.PhoneNumberField(format="(00) 0000-0000")

        person_dict1 = {'Person': {'cellphone': "(21)99666699"}}
        person_dict2 = {'Person': {'cellphone': 2199666699}}

        self.assertRaises(fields.FieldValidationError,
                          Person.from_dict,
                          person_dict1)

        self.assertRaises(TypeError,
                          Person.from_dict,
                          person_dict2)

    def test_textfield_success(self):
        class Person(Model):
            biography = fields.TextField()

        bio = u'I am a man who walks alone\n' * 20
        person_dict = {'Person': {'biography': bio}}
        john = Person.from_dict(person_dict)

        self.assertEquals(john.biography, bio)
        self.assertEquals(john.to_dict(), person_dict)

    def test_textfield_fail(self):
        class Person(Model):
            biography = fields.TextField()

        person_dict = {'Person': {'biography': "FooBar"}}
        self.assertRaises(TypeError,
                          Person.from_dict,
                          person_dict)

    def test_urlfield_success_verify(self):
        checker_mock = pmock.Mock()

        blog_url = "http://foo.bar.com/blog"

        class Person(Model):
            blog = fields.URLField(verify_exists=True,
                                   url_checker=checker_mock)

        person_dict = {'Person': {'blog': blog_url}}

        checker_mock.expects(pmock.once()) \
            .set_url(pmock.eq(blog_url))

        checker_mock.expects(pmock.once()) \
            .is_valid() \
            .will(pmock.return_value(True))

        checker_mock.expects(pmock.once()) \
            .does_exists() \
            .will(pmock.return_value(True))

        john = Person.from_dict(person_dict)

        self.assertEquals(john.blog, blog_url)
        self.assertEquals(john.to_dict(), person_dict)
        checker_mock.verify()

    def test_urlfield_success_no_verify(self):
        checker_mock = pmock.Mock()

        blog_url = "http://foo.bar.com/blog"

        class Person(Model):
            blog = fields.URLField(verify_exists=False,
                                   url_checker=checker_mock)

        person_dict = {'Person': {'blog': blog_url}}

        checker_mock.expects(pmock.once()) \
            .set_url(pmock.eq(blog_url))

        checker_mock.expects(pmock.once()) \
            .is_valid() \
            .will(pmock.return_value(True))

        checker_mock.expects(pmock.never()) \
            .does_exists()

        john = Person.from_dict(person_dict)

        self.assertEquals(john.blog, blog_url)
        self.assertEquals(john.to_dict(), person_dict)
        checker_mock.verify()

    def test_urlfield_success_no_verify_maxlength(self):

        blog_url = "http://foo.bar.com/blog"

        class Person(Model):
            blog = fields.URLField(verify_exists=False,
                                   max_length=20)

        person_dict = {'Person': {'blog': blog_url}}

        john = Person.from_dict(person_dict)

        self.assertEquals(john.blog, blog_url)
        self.assertEquals(john.to_dict(), person_dict)

    def test_urlfield_success_validate_url(self):
        blog_url = "http://foo.bar.com/blog"

        class Person(Model):
            blog = fields.URLField(verify_exists=False)

        person_dict = {'Person': {'blog': blog_url}}

        john = Person.from_dict(person_dict)

        self.assertEquals(john.blog, blog_url)
        self.assertEquals(john.to_dict(), person_dict)

    def test_urlfield_fail_validate_url(self):
        blog_url = "http://foo&*(.bar.com/b897698&%log"

        class Person(Model):
            blog = fields.URLField(verify_exists=False)

        person_dict = {'Person': {'blog': blog_url}}

        self.assertRaises(fields.FieldValidationError,
                          Person.from_dict,
                          person_dict)

    def test_urlfield_fail_nonexistent_url(self):
        blog_url = "http://qwerty.foo.bar"
        checker_mock = pmock.Mock()

        class Person(Model):
            blog = fields.URLField(verify_exists=True,
                                   url_checker=checker_mock)

        person_dict = {'Person': {'blog': blog_url}}

        checker_mock.expects(pmock.once()) \
            .set_url(pmock.eq(blog_url))

        checker_mock.expects(pmock.once()) \
            .is_valid() \
            .will(pmock.return_value(True))

        checker_mock.expects(pmock.once()) \
            .does_exists() \
            .will(pmock.return_value(False))

        self.assertRaises(fields.FieldValidationError,
                          Person.from_dict,
                          person_dict)

    def test_urlfield_fail_validate_url(self):
        def make_class():
            class Person(Model):
                blog = fields.URLField(verify_exists=None)

        self.assertRaises(TypeError, make_class)

    def test_urlfield_fail_value_nonstring(self):
        class Person(Model):
            blog = fields.URLField(verify_exists=False)

        person_dict = {'Person': {'blog': None}}

        self.assertRaises(TypeError,
                          Person.from_dict,
                          person_dict)


    def test_url_checker(self):
        urlmock = pmock.Mock()
        fields.urllib2 = urlmock

        urlmock.expects(pmock.once()) \
            .urlopen(pmock.eq("http://foo.bar.com")) \
            .will(pmock.return_value(None))

        checker = fields.URLChecker()
        checker.set_url("http://foo.bar.com")

        self.assertEquals(checker.url, "http://foo.bar.com")
        self.assertTrue(checker.is_valid())
        self.assertTrue(checker.does_exists())

        urlmock.verify()

    def test_auto_foreignkey(self):
        pass
#         class Person(Model):
#             father = fields.ForeignKey('self')
