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

import pmock

from nose.tools import assert_equals
from utils import assert_raises

from deadparrot import models
from deadparrot.models import fields
from deadparrot.models import Model

from decimal import Decimal
from datetime import datetime

class TestFieldsBasicBehavior:
    """
    Tests if the fields works with the simpliest uses: to/from a dict
    which means "meta-serialization", and tests if
    their values are working well when getting/setting
    """
    def test_field_fail(self):
        assert_raises(TypeError, fields.Field, validate=None)
        assert_raises(TypeError, fields.Field, primary_key=None)
        assert_raises(TypeError, fields.Field, null=None)
        assert_raises(TypeError, fields.Field, blank=None)

    def test_field_success_null_and_blank(self):
        class Person(Model):
            first_name = fields.CharField(max_length=40)

        john = Person(first_name=u'John')
        assert_equals(john._meta._fields['first_name'].null, True)
        assert_equals(john._meta._fields['first_name'].blank, True)

    def test_charfield_fail_construct(self):
        assert_raises(TypeError, fields.CharField, max_length=None)

    def test_datetimefield_fail_construct(self):
        assert_raises(TypeError, fields.DateTimeField, format=None)

    def test_charfield_success(self):
        class Person(Model):
            first_name = fields.CharField(max_length=40,
                                          primary_key=True,
                                          null=False,
                                          blank=False)

        person_dict = {'Person': {'first_name': u'John Doe'}}
        john = Person.from_dict(person_dict)
        assert_equals(john.first_name, u'John Doe')
        assert_equals(john.to_dict(), person_dict)

    def test_charfield_success_metadata(self):
        class Person(Model):
            first_name = fields.CharField(max_length=40,
                                          primary_key=True,
                                          null=False,
                                          blank=False)

        assert_equals(Person._meta._fields['first_name'].primary_key, True)
        assert_equals(Person._meta._fields['first_name'].null, False)
        assert_equals(Person._meta._fields['first_name'].blank, False)

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
        assert_equals(john.first_name, u'John Doe')
        assert_equals(john.to_dict(), person_dict)
        assert_equals(chevy.brand, u'Chevy')
        assert_equals(chevy.to_dict(), car_dict)

    def test_charfield_fail(self):
        class Person(Model):
            first_name = fields.CharField(max_length=10)

        fail_unicode_dict = {'Person': {'first_name': u'blah' * 4}}
        fail_int_dict = {'Person': {'first_name': 0000000}}
        fail_none_dict = {'Person': {'first_name': None}}
        fail_type_dict = {'Person': {'first_name': unicode}}
        assert_raises(fields.FieldValidationError,
                          Person.from_dict,
                          fail_unicode_dict)
        assert_raises(TypeError, Person.from_dict, fail_int_dict)
        assert_raises(TypeError, Person.from_dict, fail_none_dict)
        assert_raises(TypeError, Person.from_dict, fail_type_dict)

    def test_datetimefield_success(self):
        class Person(Model):
            creation_date = fields.DateTimeField(\
                format="%Y-%m-%d %H:%M:%S")

        expected_dict = {'Person': {'creation_date':
                                    u'2009-03-29 14:38:20'}}
        john = Person.from_dict(expected_dict)
        assert_equals(john.creation_date,
                          datetime.strptime("2009-03-29 14:38:20",
                                            "%Y-%m-%d %H:%M:%S"))
        assert_equals(john.to_dict(), expected_dict)
        assert_equals(john._meta._fields['creation_date'].primary_key,
                          False)

    def test_datetimefield_fail_format(self):
        class Person(Model):
            creation_date = fields.DateTimeField(\
                format="any wrong format")

        expected_dict = {'Person': {'creation_date':
                                    u'2009-03-29 14:38:20'}}
        assert_raises(fields.FieldValidationError,
                          Person.from_dict,
                          expected_dict)

    def test_datetimefield_fail_types(self):
        class Person(Model):
            creation_date = fields.DateTimeField(format="%Y%m%d")

        fail_dict_int = {'Person': {'creation_date': 100000}}
        assert_raises(TypeError, Person.from_dict, fail_dict_int)

    def test_datetimefield_fail_format_type(self):
        def make_class():
            class Person(Model):
                creation_time = fields.DateTimeField(format=None)

        assert_raises(TypeError, make_class)


    def test_datefield_success(self):
        class Person(Model):
            creation_date = fields.DateField(format="%Y-%m-%d")

        expected_dict = {'Person': {'creation_date':
                                    u'2009-03-29'}}
        john = Person.from_dict(expected_dict)
        assert_equals(john.creation_date,
                          datetime.strptime("2009-03-29",
                                            "%Y-%m-%d").date())
        assert_equals(john.to_dict(), expected_dict)

    def test_datefield_fail_format(self):
        class Person(Model):
            creation_date = fields.DateField(\
                format="any wrong format")

        expected_dict = {'Person': {'creation_date':
                                    u'2009-03-29 14:38:20'}}
        assert_raises(fields.FieldValidationError,
                          Person.from_dict,
                          expected_dict)

    def test_datefield_fail_types(self):
        class Person(Model):
            creation_date = fields.DateField(format="%Y%m%d")

        fail_dict_int = {'Person': {'creation_date': 100000}}
        assert_raises(TypeError, Person.from_dict, fail_dict_int)

    def test_timefield_success(self):
        class Person(Model):
            creation_time = fields.TimeField(format="%H:%M:%S")

        expected_dict = {'Person': {'creation_time':
                                    u'15:54:56'}}
        john = Person.from_dict(expected_dict)
        assert_equals(john.creation_time,
                          datetime.strptime("15:54:56",
                                            "%H:%M:%S").time())
        assert_equals(john.to_dict(), expected_dict)

    def test_timefield_fail_format(self):
        class Person(Model):
            creation_time = fields.TimeField(\
                format="any wrong format")

        expected_dict = {'Person': {'creation_time':
                                    u'2009-03-29 14:38:20'}}
        assert_raises(fields.FieldValidationError,
                          Person.from_dict,
                          expected_dict)

    def test_timefield_fail_format_date(self):
        class Person(Model):
            creation_time = fields.TimeField(format="%Y%m%d")

        fail_dict_int = {'Person': {'creation_time': "10:10:10"}}
        assert_raises(ValueError, Person.from_dict, fail_dict_int)

    def test_decimalfield_success(self):
        class Person(Model):
            first_name = fields.CharField(max_length=20, validate=False)
            wage = fields.DecimalField(max_digits=6, decimal_places=2)

        person_dict = {'Person': {'first_name': u'John Doe',
                                  'wage': '4000.55'}}

        john = Person.from_dict(person_dict)
        assert_equals(john.first_name, u'John Doe')
        assert_equals(john.wage, Decimal("4000.55"))
        assert_equals(john.to_dict(), person_dict)

    def test_decimalfield_metadata(self):
        class Person(Model):
            wage = fields.DecimalField(max_digits=6, decimal_places=2)

        person_dict = {'Person': {'wage': '4000.55'}}

        john = Person.from_dict(person_dict)
        assert_equals(john.wage, Decimal("4000.55"))
        assert_equals(john._meta._fields['wage'].max_digits, 6)
        assert_equals(john._meta._fields['wage'].decimal_places, 2)

    def test_decimalfield_fail(self):
        class Person(Model):
            first_name = fields.CharField(max_length=20, validate=False)
            wage = fields.DecimalField(max_digits=2, decimal_places=2)

        person_dict = {'Person': {'first_name': u'John Doe',
                                  'wage': '4000.55'}}

        assert_raises(fields.FieldValidationError,
                          Person.from_dict, person_dict)

    def test_decimalfield_raises_on_construct(self):
        assert_raises(TypeError, fields.DecimalField,
                          max_digits="two", decimal_places=None)

    def test_decimalfield_raises_on_setattr(self):
        class Person(Model):
            wage = fields.DecimalField(decimal_places=2, max_digits=6)

        expected_dict = {'Person': {'wage': None}}

        assert_raises(TypeError,
                          Person.from_dict,
                          expected_dict)

    def test_decimalfield_fail_on_set(self):
        class Person(Model):
            wage = fields.DecimalField(max_digits=6, decimal_places=2)

        person_dict = {'Person': {'wage': '4000.55'}}

        man = Person.from_dict(person_dict)
        assert_raises(fields.FieldValidationError,
                          setattr, man, 'wage', '10:10:10')

    def test_decimalfield_fail_from_dict(self):
        class Person(Model):
            wage = fields.DecimalField(max_digits=2, decimal_places=2)

        fail_dict_weird = {'Person': {'wage': "10:10:10"}}
        assert_raises(fields.FieldValidationError, Person.from_dict, fail_dict_weird)

    def test_emailfield_success(self):
        class Person(Model):
            first_name = fields.CharField(max_length=20, validate=False)
            email = fields.EmailField()

        person_dict = {'Person': {'first_name': u'John Doe',
                                  'email': 'johndoe@jdfake.net'}}

        john = Person.from_dict(person_dict)
        assert_equals(john.first_name, u'John Doe')
        assert_equals(john.email, 'johndoe@jdfake.net')
        assert_equals(john.to_dict(), person_dict)

    def test_emailfield_validate_fail_on_set(self):
        class Person(Model):
            email = fields.EmailField()

        person_dict = {'Person': {'email': 'johndoe@jdfake.net'}}

        john = Person.from_dict(person_dict)
        assert_raises(fields.FieldValidationError,
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

    def test_emailfield_fail_construct(self):
        assert_raises(TypeError, fields.EmailField, max_length=None)

    def test_integerfield_success(self):
        class Person(Model):
            childrens = fields.IntegerField()

        person_dict = {'Person': {'childrens': 3}}

        john = Person.from_dict(person_dict)
        assert_equals(john.childrens, 3)
        assert_equals(john.to_dict(), person_dict)

    def test_integerfield_fail_on_validate(self):
        class Person(Model):
            childrens = fields.IntegerField()

        person_dict = {'Person': {'childrens': None}}
        assert_raises(fields.FieldValidationError,
                          Person.from_dict,
                          person_dict)

    def test_floatfield_success(self):
        class Person(Model):
            weight = fields.FloatField()

        person_dict = {'Person': {'weight': 3.2}}

        john = Person.from_dict(person_dict)
        assert_equals(john.weight, 3.2)
        assert_equals(john.to_dict(), person_dict)

    def test_floatfield_fail_on_validate(self):
        class Person(Model):
            weight = fields.FloatField()

        person_dict = {'Person': {'weight': None}}
        assert_raises(fields.FieldValidationError,
                          Person.from_dict,
                          person_dict)

    def test_booleanfield_success(self):
        class Person(Model):
            married = fields.BooleanField(positives=["true", "yes"],
                                          negatives=["false", "no"])

        person_dict = {'Person': {'married': True}}

        john = Person.from_dict(person_dict)
        assert_equals(john.married, True)
        assert_equals(john.to_dict(), person_dict)

    def test_booleanfield_success_with_stringified_boolean_type_true(self):
        class Person(Model):
            married = fields.BooleanField(positives=["true", "yes"],
                                          negatives=["false", "no"])

        person_dict = {'Person': {'married': 'True'}}
        john = Person.from_dict(person_dict)
        assert_equals(john.married, True)

    def test_booleanfield_success_with_stringified_boolean_type_false(self):
        class Person(Model):
            married = fields.BooleanField(positives=["true", "yes"],
                                          negatives=["false", "no"])

        person_dict = {'Person': {'married': 'False'}}
        john = Person.from_dict(person_dict)
        assert_equals(john.married, False)

    def test_booleanfield_fail(self):
        class Person(Model):
            married = fields.BooleanField(positives=["true", "yes"],
                                          negatives=["false", "no"])

        person_dict = {'Person': {'married': None}}

        assert_raises(TypeError, Person.from_dict, person_dict)

    def test_booleanfield_fail_construct(self):
        assert_raises(TypeError,
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
        assert_equals(john.cellphone, "(21) 9966-6699")
        assert_equals(john.to_dict(), person_dict)

    def test_phonenumberfield_success(self):
        class Person(Model):
            cellphone = fields.PhoneNumberField(format="(00) 0000-0000")

        person_dict = {'Person': {'cellphone': "(21) 9966-6699"}}

        john = Person.from_dict(person_dict)
        assert_equals(john.cellphone, "(21) 9966-6699")
        assert_equals(john.to_dict(), person_dict)


    def test_phonenumberfield_fail_construct(self):
        assert_raises(TypeError,
                          fields.PhoneNumberField,
                          format=None,
                          charfield=None)
        assert_raises(TypeError,
                          fields.PhoneNumberField,
                          charfield=None)
        assert_raises(TypeError,
                          fields.PhoneNumberField,
                          format=None)

    def test_phonenumberfield_fail_validate(self):
        class Person(Model):
            cellphone = fields.PhoneNumberField(format="(00) 0000-0000")

        person_dict1 = {'Person': {'cellphone': "(21)99666699"}}
        person_dict2 = {'Person': {'cellphone': 2199666699}}

        assert_raises(fields.FieldValidationError,
                          Person.from_dict,
                          person_dict1)

        assert_raises(TypeError,
                          Person.from_dict,
                          person_dict2)

    def test_textfield_success(self):
        class Person(Model):
            biography = fields.TextField()

        bio = u'I am a man who walks alone\n' * 20
        person_dict = {'Person': {'biography': bio}}
        john = Person.from_dict(person_dict)

        assert_equals(john.biography, bio)
        assert_equals(john.to_dict(), person_dict)

    def test_textfield_fail(self):
        class Person(Model):
            biography = fields.TextField()

        person_dict = {'Person': {'biography': 00}}
        assert_raises(TypeError,
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

        assert_equals(john.blog, blog_url)
        assert_equals(john.to_dict(), person_dict)
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

        assert_equals(john.blog, blog_url)
        assert_equals(john.to_dict(), person_dict)
        checker_mock.verify()

    def test_urlfield_success_no_verify_maxlength(self):

        blog_url = "http://foo.bar.com/blog"

        class Person(Model):
            blog = fields.URLField(verify_exists=False,
                                   max_length=20)

        person_dict = {'Person': {'blog': blog_url}}

        john = Person.from_dict(person_dict)

        assert_equals(john.blog, blog_url)
        assert_equals(john.to_dict(), person_dict)

    def test_urlfield_success_validate_url(self):
        blog_url = "http://foo.bar.com/blog"

        class Person(Model):
            blog = fields.URLField(verify_exists=False)

        person_dict = {'Person': {'blog': blog_url}}

        john = Person.from_dict(person_dict)

        assert_equals(john.blog, blog_url)
        assert_equals(john.to_dict(), person_dict)

    def test_urlfield_fail_validate_url(self):
        blog_url = "http://foo&*(.bar.com/b897698&%log"

        class Person(Model):
            blog = fields.URLField(verify_exists=False)

        person_dict = {'Person': {'blog': blog_url}}

        assert_raises(fields.FieldValidationError,
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

        assert_raises(fields.FieldValidationError,
                          Person.from_dict,
                          person_dict)

    def test_urlfield_fail_value_nonstring(self):
        class Person(Model):
            blog = fields.URLField(verify_exists=False)

        person_dict = {'Person': {'blog': None}}

        assert_raises(TypeError,
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

        assert_equals(checker.url, "http://foo.bar.com")
        assert (checker.is_valid())
        assert (checker.does_exists())

        urlmock.verify()
