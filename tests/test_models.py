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
import simplejson

from deadparrot.core.models import fields
from deadparrot.core import models
from deadparrot.core.models import Model
from deadparrot.core.models import build_metadata
from datetime import date, time, datetime

from utils import one_line_xml

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
        self.assertEquals(p._meta.fields_validation_policy, models.VALIDATE_ALL)

    def test_construction(self):
        class Person(Model):
            name = fields.CharField(max_length=20)
            birthdate = fields.DateField(format="%d/%m/%Y")

        person = Person(name=u"blaj", birthdate=u'10/10/2000')
        self.assertEquals(person.name, 'blaj')
        self.assertEquals(person.birthdate, date(2000, 10, 10))

    def test_construction_fail(self):
        class Person(Model):
            name = fields.CharField(max_length=20)
            birthdate = fields.DateField(format="%d/%m/%Y")

        self.assertRaises(AttributeError,
                          Person, name=u"blaj", dsa=u'10/10/2000')

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

    def test_from_dict_fail_without_a_dict(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")

        self.assertRaises(TypeError, Person.from_dict, "")
        self.assertRaises(TypeError, Person.from_dict, [])
        self.assertRaises(TypeError, Person.from_dict, tuple())
        self.assertRaises(TypeError, Person.from_dict, 2)
        self.assertRaises(TypeError, Person.from_dict, 2.2)
        self.assertRaises(TypeError, Person.from_dict, None)

    def test_should_not_validate_with_meta_property(self):
        class Person(Model):
            name = fields.CharField(max_length=0)
            birthdate = fields.DateField(format="%d/%m/%Y")

            class Meta:
                fields_validation_policy = models.VALIDATE_NONE

        john = Person.from_dict({"Person": {"name": "John",
                                            "birthdate": "20/10/1980"}})
        self.assertEquals(john.name, "John")

class TestModelInstrospection(unittest.TestCase):
    def test_field_names(self):
        class Foo(Model):
            baz = fields.Field()

        foobar = Foo()
        self.assertEquals(foobar._meta._fields['baz'].name, 'baz')

    def test_properties(self):
        class Foo(Model):
            baz = fields.CharField(max_length=100)
            @property
            def foobaz(self):
                return u"Foo + %s" % self.baz

        my_dict = {
            'Foo': {
                'baz': u"Baz, Bar and so on...",
            }
        }

        foobar = Foo.from_dict(my_dict)
        self.assertEquals(foobar.baz, u"Baz, Bar and so on...")
        self.assertEquals(foobar.foobaz, u"Foo + Baz, Bar and so on...")

class TestModelSet(unittest.TestCase):
    my_dict = {
        'People':
        [
            {
                'Person': {
                    'name': u"John Doe",
                    'birthdate': u"10/02/1988"
                }
            },
            {
                'Person': {
                    'name': u"Mary Doe",
                    'birthdate': u"20/10/1989"
                }
            },
        ]
    }

    def test_construction_fail(self):
        self.assertRaises(TypeError, models.ModelSet, object(), None)

    def test_to_dict(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                plural_name = 'People'

        person1 = Person(name=u'John Doe', birthdate=u'10/02/1988')
        person2 = Person(name=u'Mary Doe', birthdate=u'20/10/1989')
        PersonSet = Person.Set()
        people = PersonSet(person1, person2)
        self.assert_(isinstance(people, models.ModelSet),
                     "people should be a ModelSet")

        self.assertEquals(people.to_dict(), self.my_dict)

    def test_from_dict(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                plural_name = 'People'

        person1 = Person(name=u'John Doe', birthdate=u'10/02/1988')
        person2 = Person(name=u'Mary Doe', birthdate=u'20/10/1989')
        PersonSet = Person.Set()
        people = PersonSet.from_dict(self.my_dict)
        self.assert_(isinstance(people, models.ModelSet),
                     "people should be a ModelSet")
        self.assertEquals(people.to_dict(), self.my_dict)

class TestModelSerialization(unittest.TestCase):
    class Person(Model):
            first_name = fields.CharField(max_length=40)
            birthdate = fields.DateField(format="%d/%m/%Y")

    my_json = simplejson.dumps({
        'Person': {
            'first_name': u"John Doe",
            'birthdate': u"10/02/1988"
        }
    })
    my_xml = """
    <Person>
       <first_name>John Doe</first_name>
       <birthdate>10/02/1988</birthdate>
    </Person>
    """
    def test_model_serialization_json(self):

        john = self.Person(first_name=u'John Doe',
                      birthdate=date(1988, 2, 10))

        self.assertEquals(john.serialize(to='json'),
                          self.my_json)

    def test_model_serialization_xml(self):
        john = self.Person(first_name=u'John Doe',
                           birthdate=date(1988, 2, 10))

        self.assertEquals(john.serialize(to='xml'),
                          one_line_xml(self.my_xml))


    def test_model_deserialization_json(self):
        john = self.Person.deserialize(self.my_json, format='json')
        self.assertEquals(one_line_xml(john.serialize(to='xml')),
                          one_line_xml(self.my_xml))

    def test_model_deserialization_xml(self):
        john = self.Person.deserialize(self.my_xml, format='xml')
        self.assertEquals(john.serialize(to='json'),
                          self.my_json)
