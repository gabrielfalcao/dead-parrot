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
from deadparrot.lib import demjson

from deadparrot.models import fields, base
from deadparrot import models
from deadparrot.models import Model
from deadparrot.models import build_metadata
from datetime import date, datetime

from utils import one_line_xml, assert_raises

class TestBasicModel(unittest.TestCase):
    def test_build_metadata_verbose_name(self):
        class Car(Model):
            pass

        self.assertEquals(build_metadata(Car, {}).verbose_name, 'Car')
        self.assertEquals(build_metadata(Car, {}).verbose_name_plural, 'Cars')

    def test_model_metadata_has_fields_attr(self):
        class Car(Model):
            one = models.IntegerField()
            two = models.TextField()

        assert hasattr(Car()._meta, '_fields'), 'model._meta should have attribute _fields'

    def test_model_metadata_fields_attr_is_dict(self):
        class Car(Model):
            one = models.IntegerField()
            two = models.TextField()

        assert isinstance(Car()._meta._fields, dict), 'model._meta._fields should be a dictionary'

    def test_model_metadata_fields_attr_keys(self):
        class Car(Model):
            aa = models.IntegerField()
            bb = models.TextField()

        assert sorted(Car()._meta._fields.keys()) == ['aa', 'bb'], \
               'model._meta._fields should have ' \
               'the keys "aa" and "bb", but got %r' % \
               Car()._meta._fields.keys()

    def test_model_metadata_has_relationships_attr(self):
        class Car(Model):
            one = models.IntegerField()
            two = models.TextField()

        assert hasattr(Car()._meta, '_relationships'), 'model._meta should have attribute _relationships'

    def test_model_metadata_relationships_attr_is_dict(self):
        class Car(Model):
            one = models.IntegerField()
            two = models.TextField()

        assert isinstance(Car()._meta._relationships, dict), 'model._meta._relationships should be a dictionary'

    def test_model_metadata_relationships_attr_keys(self):
        class Bar(Model):
            aa = models.IntegerField(primary_key=True)

        class Foo(Model):
            zz = models.IntegerField(primary_key=True)
            aa = models.ForeignKey(Bar)
            bb = models.ManyToManyField(Bar)

        keys = sorted(Foo()._meta._relationships.keys())
        assert keys == ['aa', 'bb'], \
               'model._meta._relationships should have ' \
               'the keys "aa" and "bb", but got %r' % keys

    def test_model_metadata_has_relationships_plural_attr(self):
        class Car(Model):
            one = models.IntegerField()
            two = models.TextField()

        assert hasattr(Car()._meta, '_relationships_plural'), 'model._meta should have attribute _relationships_plural'

    def test_model_metadata_relationships_plural_attr_is_dict(self):
        class Car(Model):
            one = models.IntegerField()
            two = models.TextField()

        assert isinstance(Car()._meta._relationships_plural, dict), 'model._meta._relationships_plural should be a dictionary'

    def test_build_metadata_app_label(self):
        class Car(Model):
            __module__ = 'rentalsys.vehicles'

        class Person(Model):
            __module__ = 'medicalsys.management'

        class Building(Model):
            __module__ = 'engineering.constructions.items'

        self.assertEquals(build_metadata(Car, {}).app_label, 'vehicles')
        self.assertEquals(build_metadata(Person, {}).app_label, 'management')
        self.assertEquals(build_metadata(Building, {}).app_label, 'items')

    def test_metadata(self):
        class Person(Model):
            class Meta:
                verbose_name = 'Person'
                verbose_name_plural = 'People'

        self.failUnless(Person._meta is not None)
        self.assertEquals(Person._meta.verbose_name, 'Person')
        self.assertEquals(Person._meta.verbose_name_plural, 'People')
        self.assertEquals(Person._meta.fields_validation_policy, models.VALIDATE_ALL)
        self.assertEquals(Person._meta.has_pk, False)

    def test_metadata_for_pks(self):
        class Person(Model):
            id = models.IntegerField(primary_key=True)
            class Meta:
                verbose_name = 'Person'
                verbose_name_plural = 'People'

        self.assertEquals(Person._meta.has_pk, True)

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

    def test_to_dict_foreign_key(self):
        class House(Model):
            address = fields.TextField(primary_key=True)

        class Person(Model):
            name = fields.CharField(max_length=20, primary_key=True)
            birthdate = fields.DateField(format="%d/%m/%Y")
            live_in = fields.ForeignKey(House)

        p = Person()
        p.name = u"John Doe"
        p.birthdate = date(1988, 02, 10)
        p.live_in = House(address='Franklin St.')
        my_dict = {
            'Person': {
                'name': u"John Doe",
                'birthdate': u"10/02/1988",
                'live_in': {
                    'House': {
                        'address': 'Franklin St.'
                    }
                }
            }
        }

        self.assertEquals(my_dict, p.to_dict())

    def test_from_dict_foreign_key(self):
        class House(Model):
            address = fields.TextField(primary_key=True)

        class Person(Model):
            name = fields.CharField(max_length=20, primary_key=True)
            birthdate = fields.DateField(format="%d/%m/%Y")
            live_in = fields.ForeignKey(House)

        my_dict = {
            'Person': {
                'name': u"John Doe",
                'birthdate': u"10/02/1988",
                'live_in': {
                    'House': {
                        'address': 'Franklin St.'
                    }
                }
            }
        }

        p = Person.from_dict(my_dict)
        assert p.name == u'John Doe', "Expected 'John Doe', got %s" % repr(p.name)
        assert p.birthdate == date(1988, 2, 10), "Expected datetime.date(1988, 2, 10), got %s" % repr(p.birthdate)
        expected = House(address='Franklin St.')
        assert p.live_in is not None, '%r.live_in should not be None' % p
        assert p.live_in == expected, "Expected %r, got %s" % (expected, repr(p.birthdate))

    def test_from_dict_many_to_many_field(self):
        class Car(Model):
            name = fields.CharField(max_length=100, primary_key=True)

        class Person(Model):
            name = fields.CharField(max_length=20, primary_key=True)
            birthdate = fields.DateField(format="%d/%m/%Y")
            vehicles = fields.ManyToManyField(Car)

        my_dict = {
            'Person': {
                'name': u"John Doe",
                'birthdate': u"10/02/1988",
                'vehicles':  {
                    'Cars': [
                        {'Car': {'name': 'Ferrari'}},
                        {'Car': {'name': 'Fiat'}},
                    ]
                }
            }
        }

        p = Person.from_dict(my_dict)
        assert p.name == u'John Doe', "Expected 'John Doe', got %s" % repr(p.name)
        assert p.birthdate == date(1988, 2, 10), "Expected datetime.date(1988, 2, 10), got %s" % repr(p.birthdate)
        assert p.vehicles is not None, '%r.vehicles should not be None' % p

        car_model_set = p.vehicles.as_modelset()
        length = len(car_model_set)
        assert length == 2, "Expected 2 cars within %r.vehicles.as_modelset(), got %d" % (p.vehicles, length)
        assert car_model_set[0] == Car(name='Ferrari')
        assert car_model_set[1] == Car(name='Fiat')

    def test_to_dict_many_to_many_field(self):
        class House(Model):
            address = fields.TextField(primary_key=True)

        class Person(Model):
            name = fields.CharField(max_length=20, primary_key=True)
            birthdate = fields.DateField(format="%d/%m/%Y")
            live_in = fields.ForeignKey(House)

        my_dict = {
            'Person': {
                'name': u"John Doe",
                'birthdate': u"10/02/1988",
                'live_in': {
                    'House': {
                        'address': 'Franklin St.'
                    }
                }
            }
        }

        p = Person(name='John Doe', birthdate=date(1988, 2, 10), live_in=House(address='Franklin St.'))
        assert p.to_dict() == my_dict, 'Expected %r, got %r' % (my_dict, p.to_dict())

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

class TestModelInternals(unittest.TestCase):
    def setUp(self):
        class Foo(Model):
            bar = fields.CharField(max_length=10, blank=False)
            foobar = fields.CharField(max_length=10, blank=True)
        self.Foo = Foo

    def test_is_valid(self):
        foo2 = self.Foo(bar=u'boo')
        foo3 = self.Foo(foobar=u'meh', bar=u'boo')
        self.assertEquals(foo2._is_valid, True)
        self.assertEquals(foo3._is_valid, True)

    def test_is_not_valid(self):
        foo1 = self.Foo(foobar=u'boo')
        self.assertEquals(foo1._is_valid, False)

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

    def test_add_exists(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            def __unicode__(self):
                return u'Person(name="%s", birthdate="%s")' % \
                        (self.name, self.birthdate.strftime("%d/%m/%Y"))

            class Meta:
                verbose_name_plural = 'People'
        PersonSet = Person.Set()
        people = PersonSet()
        assert hasattr(people, 'add'), '%r should have the attribute add' % PersonSet
        assert callable(people.add), '%r.add should be a method (callable)' % PersonSet

    def test_add_success(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            def __unicode__(self):
                return u'Person(name="%s")' % self.name

            class Meta:
                verbose_name_plural = 'People'
        PersonSet = Person.Set()

        person = Person(name='Wee')
        people1 = PersonSet(*[person])
        people2 = PersonSet()
        people2.add(person)

        assert people1 == people2, '%r should be equal to %r' % (people1, people2)

    def test_add_fails_when_not_same_type(self):
        class Foo(Model):
            pass
        class Bar(Model):
            pass

        FooSet = Foo.Set()
        BarSet = Bar.Set()
        foos = FooSet()
        bars = BarSet()

        assert_raises(TypeError, foos.add, None, exc_pattern=r'add\(\) takes a Foo model instance as parameter, got None')
        assert_raises(TypeError, foos.add, 5, exc_pattern=r'add\(\) takes a Foo model instance as parameter, got 5')
        assert_raises(TypeError, bars.add, 10, exc_pattern=r'add\(\) takes a Bar model instance as parameter, got 10')

    def test_remove_exists(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            def __unicode__(self):
                return u'Person(name="%s", birthdate="%s")' % \
                        (self.name, self.birthdate.strftime("%d/%m/%Y"))

            class Meta:
                verbose_name_plural = 'People'
        PersonSet = Person.Set()
        people = PersonSet()
        assert hasattr(people, 'remove'), '%r should have the attribute remove' % PersonSet
        assert callable(people.remove), '%r.remove should be a method (callable)' % PersonSet

    def test_remove_success(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            def __unicode__(self):
                return u'Person(name="%s")' % self.name

            class Meta:
                verbose_name_plural = 'People'
        PersonSet = Person.Set()

        person1 = Person(name='Wee1')
        person2 = Person(name='Wee2')
        person3 = Person(name='Wee3')
        people1 = PersonSet(*[person1, person2, person3])
        people2 = PersonSet(*[person1, person3])
        people1.remove(person2)

        assert people1 == people2, '%r should be equal to %r' % (people1, people2)

    def test_remove_fails_when_not_same_type(self):
        class Foo(Model):
            pass
        class Bar(Model):
            pass

        FooSet = Foo.Set()
        BarSet = Bar.Set()
        foos = FooSet()
        bars = BarSet()

        assert_raises(TypeError, foos.remove, None, exc_pattern=r'remove\(\) takes a Foo model instance as parameter, got None')
        assert_raises(TypeError, foos.remove, 5, exc_pattern=r'remove\(\) takes a Foo model instance as parameter, got 5')
        assert_raises(TypeError, bars.remove, 10, exc_pattern=r'remove\(\) takes a Bar model instance as parameter, got 10')

    def test_to_dict(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            def __unicode__(self):
                return u'Person(name="%s", birthdate="%s")' % \
                        (self.name, self.birthdate.strftime("%d/%m/%Y"))

            class Meta:
                verbose_name_plural = 'People'

        person1 = Person(name=u'John Doe', birthdate=u'10/02/1988')
        person2 = Person(name=u'Mary Doe', birthdate=u'20/10/1989')
        PersonSet = Person.Set()
        people = PersonSet(person1, person2)
        self.assert_(isinstance(people, models.ModelSet),
                     "people should be a ModelSet")

        self.assertEquals(people.to_dict(), self.my_dict)
        self.assertEquals(unicode(people), 'Person.Set([Person(name="John Doe", birthdate="10/02/1988"), Person(name="Mary Doe", birthdate="20/10/1989")])')

    def test_to_list_operations_getitem(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                verbose_name_plural = 'People'

        person1 = Person(name=u'John Doe', birthdate=u'10/02/1988')
        person2 = Person(name=u'Mary Doe', birthdate=u'20/10/1989')
        PersonSet = Person.Set()
        people = PersonSet(person1, person2)

        self.assertEquals(people[0].name, u'John Doe')

    def test_to_list_operations_length(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                verbose_name_plural = 'People'

        person1 = Person(name=u'John Doe', birthdate=u'10/02/1988')
        person2 = Person(name=u'Mary Doe', birthdate=u'20/10/1989')
        PersonSet = Person.Set()
        people = PersonSet(person1, person2)

        self.assertEquals(len(people), 2)

    def test_to_list_operations_nonzero(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                verbose_name_plural = 'People'

        person1 = Person(name=u'John Doe', birthdate=u'10/02/1988')
        person2 = Person(name=u'Mary Doe', birthdate=u'20/10/1989')
        PersonSet = Person.Set()
        people = PersonSet(person1, person2)

        # nonzero
        self.assertEquals(bool(people), True)
        self.assertEquals(bool(PersonSet()), False)

    def test_to_list_operations_iteration(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                verbose_name_plural = 'People'

        person1 = Person(name=u'John Doe', birthdate=u'10/02/1988')
        person2 = Person(name=u'Mary Doe', birthdate=u'20/10/1989')
        PersonSet = Person.Set()
        people = PersonSet(person1, person2)

        self.assertEquals([u'John Doe', u'Mary Doe'],
                          [x.name for x in people])

    def test_to_list_operations_equality(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                verbose_name_plural = 'People'

        person1 = Person(name=u'John Doe', birthdate=u'10/02/1988')
        person2 = Person(name=u'Mary Doe', birthdate=u'20/10/1989')
        PersonSet = Person.Set()
        people = PersonSet(person1, person2)

        self.assertEquals(people, PersonSet(person1, person2))
        self.assertNotEquals(people, PersonSet(person2, person1))

    def test_from_dict(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                verbose_name_plural = 'People'

        person1 = Person(name=u'John Doe', birthdate=u'10/02/1988')
        person2 = Person(name=u'Mary Doe', birthdate=u'20/10/1989')
        PersonSet = Person.Set()
        people = PersonSet.from_dict(self.my_dict)
        self.assert_(isinstance(people, models.ModelSet),
                     "people should be a ModelSet")
        self.assertEquals(people.to_dict(), self.my_dict)
        self.assertEquals(people[0], person1)
        self.assertEquals(people[1], person2)

class TestModelSerialization(unittest.TestCase):
    class Person(Model):
            first_name = fields.CharField(max_length=40)
            birthdate = fields.DateField(format="%d/%m/%Y")

    my_json = demjson.encode({
        'Person': {
            'first_name': u"John Doe",
            'birthdate': u"10/02/1988"
        }
    })
    extra_json = demjson.encode({
        'Person': {
            'first_name': u"John Doe",
            'birthdate': u"10/02/1988",
            'foo': {'bar': u'Baz'}
        }
    })
    my_xml = """
    <Person>
       <first_name>John Doe</first_name>
       <birthdate>10/02/1988</birthdate>
    </Person>
    """
    extra_xml = """
    <Person>
       <first_name>John Doe</first_name>
       <metadata>
          <many>People</many>
          <foo>Bar</foo>
       </metadata>
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

    def test_model_deserialization_extra_json(self):
        john = self.Person.deserialize(self.extra_json, format='json')
        self.assertEquals(one_line_xml(john.serialize(to='xml')),
                          one_line_xml(self.my_xml))

    def test_model_deserialization_xml(self):
        john = self.Person.deserialize(self.my_xml, format='xml')
        self.assertEquals(john.serialize(to='json'),
                          self.my_json)

    def test_model_deserialization_xml_json(self):
        john = self.Person.deserialize(self.extra_xml, format='xml')
        self.assertEquals(john.serialize(to='json'),
                          self.my_json)

class TestModelSetSerialization(unittest.TestCase):
    class Person(Model):
            first_name = fields.CharField(max_length=40)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                verbose_name_plural = 'People'

    my_json = demjson.encode({
        'People':
        [
            {
                'Person': {
                    'first_name': u"John Doe",
                    'birthdate': u"10/02/1988"
                }
            },
            {
                'Person': {
                    'first_name': u"Mary Doe",
                    'birthdate': u"20/10/1989"
                }
            },
        ]
    })
    my_xml = """
    <People>
        <Person>
           <first_name>John Doe</first_name>
           <birthdate>10/02/1988</birthdate>
        </Person>
        <Person>
           <first_name>Mary Doe</first_name>
           <birthdate>20/10/1989</birthdate>
        </Person>
    </People>
    """
    def test_modelset_serialization_json(self):

        john = self.Person(first_name=u'John Doe',
                      birthdate=date(1988, 2, 10))
        mary = self.Person(first_name=u'Mary Doe',
                      birthdate=date(1989, 10, 20))
        PersonSet = self.Person.Set()
        people = PersonSet(john, mary)

        self.assertEquals(people.serialize(to='json'),
                          self.my_json)

    def test_modelset_deserialization_json(self):
        PersonSet = self.Person.Set()
        people = PersonSet.deserialize(self.my_json, format='json')

        self.assert_(isinstance(people, PersonSet))
        self.assertEquals(people[0].first_name, u'John Doe')

    def test_modelset_serialization_xml(self):
        john = self.Person(first_name=u'John Doe',
                      birthdate=date(1988, 2, 10))
        mary = self.Person(first_name=u'Mary Doe',
                      birthdate=date(1989, 10, 20))
        PersonSet = self.Person.Set()
        people = PersonSet(john, mary)

        self.assertEquals(one_line_xml(people.serialize(to='xml')),
                          one_line_xml(self.my_xml))

    def test_modelset_deserialization_xml(self):
        PersonSet = self.Person.Set()
        people = PersonSet.deserialize(self.my_xml, format='xml')

        self.assert_(isinstance(people, PersonSet))
        self.assertEquals(people[0].first_name, u'John Doe')

class TestModelRegistry(unittest.TestCase):
    def test_model_registry_global_dict(self):
        class Foo(Model):
            __module__ = 'loren.ipsum'

        apps = base._REGISTRY[Foo.__module__].keys()
        self.assert_('ipsum' in apps)

        fooclass = base._REGISTRY[Foo.__module__]['ipsum']['Foo']
        self.assertEquals(fooclass, Foo)

    def test_model_registry_apps(self):
        class Foo(Model):
            __module__ = 'loren.ipsum'

        fooclass = base._APP_REGISTRY['ipsum']['Foo']
        self.assertEquals(fooclass, Foo)

    def test_model_registry_modules(self):
        class Foo(Model):
            __module__ = 'loren.ipsum'

        fooclass = base._MODULE_REGISTRY['loren.ipsum']['Foo']
        self.assertEquals(fooclass, Foo)

    def test_model_registry_get_all_raises(self):
        self.assertRaises(TypeError,
                          models.ModelRegistry.get_all, by_class=213)
        self.assertRaises(TypeError,
                          models.ModelRegistry.get_all, by_class=[1])
        self.assertRaises(TypeError,
                          models.ModelRegistry.get_all, by_class=[1])

        self.assertRaises(TypeError,
                          models.ModelRegistry.get_all, by_module=213)
        self.assertRaises(TypeError,
                          models.ModelRegistry.get_all, by_module=[1])
        self.assertRaises(TypeError,
                          models.ModelRegistry.get_all, by_module=[1])

        self.assertRaises(TypeError,
                          models.ModelRegistry.get_all, by_app_label=213)
        self.assertRaises(TypeError,
                          models.ModelRegistry.get_all, by_app_label=[1])
        self.assertRaises(TypeError,
                          models.ModelRegistry.get_all, by_app_label=[1])

    def test_repeated_names_but_different_app_labels(self):
        class Person(Model):
            __module__ = 'universe.mars'
            from_mars = fields.CharField(max_length=10)

        martian = Person(from_mars='yes')
        class Person(Model):
            __module__ = 'universe.earth'
            from_earth = fields.CharField(max_length=10)

        earthling = Person(from_earth='yes')
        class Person(Model):
            __module__ = 'universe.venus'
            from_venus = fields.CharField(max_length=10)
        venusian = Person(from_venus='yes')

        person_classes = models.ModelRegistry.get_all(by_class="Person")
        self.assert_(isinstance(martian, person_classes))
        self.assert_(martian.__class__ in person_classes)

        self.assert_(isinstance(earthling, person_classes))
        self.assert_(earthling.__class__ in person_classes)

        self.assert_(isinstance(venusian, person_classes))
        self.assert_(venusian.__class__ in person_classes)

    def test_get_all_by_module(self):
        class Boat(Model):
            __module__ = 'america.vehicles'

        class Car(Model):
            __module__ = 'america.vehicles'

        class Plane(Model):
            __module__ = 'america.vehicles'

        kw = dict(by_module="america.vehicles")
        vehicles = models.ModelRegistry.get_all(**kw)

        self.assertEquals(len(vehicles), 3)
        self.assert_(Boat in vehicles)
        self.assert_(Car in vehicles)
        self.assert_(Plane in vehicles)

    def test_get_all_by_app_label(self):
        class BeloHorizonte(Model):
            __module__ = 'brasil.minas_gerais'

        class PortoAlegre(Model):
            __module__ = 'brasil.rio_grande_do_sul'

        class Curitiba(Model):
            __module__ = 'brasil.parana'

        kw = dict(by_app_label="minas_gerais")
        mg = models.ModelRegistry.get_all(**kw)
        self.assertEquals(len(mg), 1)
        self.assert_(BeloHorizonte in mg)
        self.assert_(PortoAlegre not in mg)
        self.assert_(Curitiba not in mg)

        kw = dict(by_app_label="rio_grande_do_sul")
        rs = models.ModelRegistry.get_all(**kw)
        self.assertEquals(len(rs), 1)
        self.assert_(PortoAlegre in rs)
        self.assert_(BeloHorizonte not in rs)
        self.assert_(Curitiba not in rs)

        kw = dict(by_app_label="parana")
        pr = models.ModelRegistry.get_all(**kw)
        self.assertEquals(len(pr), 1)
        self.assert_(Curitiba in pr)
        self.assert_(PortoAlegre not in pr)
        self.assert_(BeloHorizonte not in pr)

    def test_get_model(self):
        class BeloHorizonte(Model):
            __module__ = 'brasil.minas_gerais'
        class PortoAlegre(Model):
            __module__ = 'brasil.rio_grande_do_sul'
        class Curitiba(Model):
            __module__ = 'brasil.parana'

        self.assertEquals(models.ModelRegistry.get_model(app_label='minas_gerais',
                                                         classname='BeloHorizonte'),
                          BeloHorizonte)

    def test_get_model_raises(self):
        self.assertRaises(AttributeError,
                          models.ModelRegistry.get_model,
                          app_label='foo',
                          classname='bar')

        self.assertRaises(TypeError,
                          models.ModelRegistry.get_model,
                          app_label=123,
                          classname='bar')

        self.assertRaises(TypeError,
                          models.ModelRegistry.get_model,
                          app_label='foo',
                          classname=123)

class TestModelOperations(unittest.TestCase):
    def test_equals_raises(self):
        class Person(Model):
            name = fields.CharField(max_length=20)
            birthdate = fields.DateField(format="%d/%m/%Y")

        person1 = Person(name=u"blaj", birthdate=u'10/10/2000')
        self.assertRaises(TypeError, person1, range(10))

    def test_all_fields_equals_success(self):
        """Here I will test a common behavior: each field of both
        model objects must have the same value"""
        class Person(Model):
            name = fields.CharField(max_length=20)
            birthdate = fields.DateField(format="%d/%m/%Y")

        person1 = Person(name=u"blaj", birthdate=u'10/10/2000')
        person2 = Person(name=u"blaj", birthdate=u'10/10/2000')
        self.assertEquals(person1, person2)

    def test_all_primary_keys_equals_success(self):
        """Here I will test a special behavior: at least all
        primary_keys must me equal"""
        class Person(Model):
            id = fields.IntegerField(primary_key=True)
            name = fields.CharField(max_length=20)
            birthdate = fields.DateField(format="%d/%m/%Y")

        person1 = Person(id=1, name=u"blaj", birthdate=u'10/10/2000')
        person2 = Person(id=1, name=u"blu", birthdate=u'10/10/1988')
        self.assertEquals(person1, person2)

    def test_notequals_success(self):
        class Person(Model):
            name = fields.CharField(max_length=20)
            birthdate = fields.DateField(format="%d/%m/%Y")

        person1 = Person(name=u"blaj", birthdate=u'10/10/2000')
        person2 = Person(name=u"polly", birthdate=u'20/01/1988')
        self.assertNotEquals(person1, person2)

class TestAllFieldsSerialization(unittest.TestCase):
    def setUp(self):
        class Person(models.Model):
            id = models.IntegerField(primary_key=True)
            name = models.CharField(max_length=40)
            creation_date = models.DateTimeField(format="%Y-%m-%d %H:%M:%S")
            email = models.EmailField()
            weight = models.FloatField()
            married = models.BooleanField(positives=["true", "yes", 1],
                                          negatives=["false", "no", 0])
            childrens = models.IntegerField()
            cellphone = models.PhoneNumberField(format="(00) 0000-0000")
            biography = models.TextField()
            blog = models.URLField(verify_exists=False)

            @property
            def age(self):
                return (datetime.now().date() - self.birthdate).days / 365

        self.Person = Person

    def test_all_kinds_of_fields_serialization_to_json(self):
        dtime = datetime.now()
        json = demjson.encode({
            "Person":
            {
                "id": 1,
                "cellphone": "(21) 9988-7766",
                "name": "John Doe",
                "weight": 74.349999999999994,
                "married": False,
                "creation_date": dtime.strftime("%Y-%m-%d %H:%M:%S"),
                "blog": "http://blog.john.doe.net",
                "email": "john@doe.net",
                "biography": "blabla",
                "childrens": 2
            }
        })
        john = self.Person(id=1,
                           name=u'John Doe',
                           creation_date=dtime,
                           email=u"john@doe.net",
                           weight=74.349999999999994,
                           married=False,
                           childrens=2,
                           cellphone=u"(21) 9988-7766",
                           biography=u"blabla",
                           blog=u"http://blog.john.doe.net")

        self.assertEquals(john.serialize(to='json'), json)

    def test_all_kinds_of_fields_deserialization_to_json(self):
        dtime = datetime.now()
        json = demjson.encode({
            u"Person":
            {
                "id": 1,
                "cellphone": u"(21) 9988-7766",
                "name": u"John Doe",
                "weight": 74.349999999999994,
                "married": False,
                "creation_date": dtime.strftime("%Y-%m-%d %H:%M:%S"),
                "blog": u"http://blog.john.doe.net",
                "email": u"john@doe.net",
                "biography": u"blabla",
                "childrens": 2
            }
        })
        john1 = self.Person(id=1,
                            name=u'John Doe',
                            creation_date=dtime,
                            email=u"john@doe.net",
                            weight=74.349999999999994,
                            married=False,
                            childrens=2,
                            cellphone=u"(21) 9988-7766",
                            biography=u"blabla",
                            blog=u"http://blog.john.doe.net")
        john2 = self.Person.deserialize(json, format="json")
        self.assertEquals(john1, john2)

    def test_all_kinds_of_fields_serialization_to_xml(self):
        dtime = datetime.now()
        xml = '''
            <Person>
              <cellphone>(21) 9988-7766</cellphone>
              <name>John Doe</name>
              <weight>74.35</weight>
              <married>False</married>
              <creation_date>%s</creation_date>
              <blog>http://blog.john.doe.net</blog>
              <email>john@doe.net</email>
              <id>1</id>
              <biography>blabla</biography>
              <childrens>2</childrens>
            </Person>
        ''' % dtime.strftime("%Y-%m-%d %H:%M:%S")
        john = self.Person(id=1,
                           name=u'John Doe',
                           creation_date=dtime,
                           email=u"john@doe.net",
                           weight=74.349999999999994,
                           married=False,
                           childrens=2,
                           cellphone=u"(21) 9988-7766",
                           biography=u"blabla",
                           blog=u"http://blog.john.doe.net")
        self.assertEquals(one_line_xml(john.serialize(to='xml')), one_line_xml(xml))

    def test_all_kinds_of_fields_deserialization_to_xml(self):
        dtime = datetime.now()
        xml = '''
            <Person>
              <cellphone>(21) 9988-7766</cellphone>
              <name>John Doe</name>
              <weight>74.35</weight>
              <married>False</married>
              <creation_date>%s</creation_date>
              <blog>http://blog.john.doe.net</blog>
              <email>john@doe.net</email>
              <id>1</id>
              <biography>blabla</biography>
              <childrens>2</childrens>
            </Person>
        ''' % dtime.strftime("%Y-%m-%d %H:%M:%S")
        john1 = self.Person(id=1,
                           name=u'John Doe',
                           creation_date=dtime,
                           email=u"john@doe.net",
                           weight=74.35,
                           married=False,
                           childrens=2,
                           cellphone=u"(21) 9988-7766",
                           biography=u"blabla",
                           blog=u"http://blog.john.doe.net")
        john2 = self.Person.deserialize(xml, format='xml')
        self.assertEquals(john1, john2)

    def test_positives_serialization_to_json(self):
        dtime = datetime.now()
        json = demjson.encode({
            "Person":
            {
                "id": 1,
                "cellphone": "(21) 9988-7766",
                "name": "John Doe",
                "weight": 74.349999999999994,
                "married": True,
                "creation_date": dtime.strftime("%Y-%m-%d %H:%M:%S"),
                "blog": "http://blog.john.doe.net",
                "email": "john@doe.net",
                "biography": "blabla",
                "childrens": 2
            }
        })
        john = self.Person(id=1,
                           name=u'John Doe',
                           creation_date=dtime,
                           email=u"john@doe.net",
                           weight=74.349999999999994,
                           married="yes",
                           childrens=2,
                           cellphone=u"(21) 9988-7766",
                           biography=u"blabla",
                           blog=u"http://blog.john.doe.net")

        self.assertEquals(john.serialize(to='json'), json)

    def test_positives_serialization_to_json_with_integers(self):
        dtime = datetime.now()
        json = demjson.encode({
            "Person":
            {
                "id": 1,
                "cellphone": "(21) 9988-7766",
                "name": "John Doe",
                "weight": 74.349999999999994,
                "married": True,
                "creation_date": dtime.strftime("%Y-%m-%d %H:%M:%S"),
                "blog": "http://blog.john.doe.net",
                "email": "john@doe.net",
                "biography": "blabla",
                "childrens": 2
            }
        })
        john = self.Person(id=1,
                           name=u'John Doe',
                           creation_date=dtime,
                           email=u"john@doe.net",
                           weight=74.349999999999994,
                           married=1,
                           childrens=2,
                           cellphone=u"(21) 9988-7766",
                           biography=u"blabla",
                           blog=u"http://blog.john.doe.net")

        self.assertEquals(john.serialize(to='json'), json)


    def test_negatives_serialization_to_json(self):
        dtime = datetime.now()
        json = demjson.encode({
            "Person":
            {
                "id": 1,
                "cellphone": "(21) 9988-7766",
                "name": "John Doe",
                "weight": 74.349999999999994,
                "married": False,
                "creation_date": dtime.strftime("%Y-%m-%d %H:%M:%S"),
                "blog": "http://blog.john.doe.net",
                "email": "john@doe.net",
                "biography": "blabla",
                "childrens": 2
            }
        })
        john = self.Person(id=1,
                           name=u'John Doe',
                           creation_date=dtime,
                           email=u"john@doe.net",
                           weight=74.349999999999994,
                           married="no",
                           childrens=2,
                           cellphone=u"(21) 9988-7766",
                           biography=u"blabla",
                           blog=u"http://blog.john.doe.net")

        self.assertEquals(john.serialize(to='json'), json)

    def test_negatives_serialization_to_json_with_integers(self):
        dtime = datetime.now()
        json = demjson.encode({
            "Person":
            {
                "id": 1,
                "cellphone": "(21) 9988-7766",
                "name": "John Doe",
                "weight": 74.349999999999994,
                "married": False,
                "creation_date": dtime.strftime("%Y-%m-%d %H:%M:%S"),
                "blog": "http://blog.john.doe.net",
                "email": "john@doe.net",
                "biography": "blabla",
                "childrens": 2
            }
        })
        john = self.Person(id=1,
                           name=u'John Doe',
                           creation_date=dtime,
                           email=u"john@doe.net",
                           weight=74.349999999999994,
                           married=0,
                           childrens=2,
                           cellphone=u"(21) 9988-7766",
                           biography=u"blabla",
                           blog=u"http://blog.john.doe.net")

        self.assertEquals(john.serialize(to='json'), json)

class TestModelSpecialMethods:
    def test_has_method_fill_from_object(self):
        class Person(models.Model):
            pass
        assert hasattr(Person, 'fill_from_object'), 'A deadparrot model should have the method "fill_from_object"'

    def test_method_fill_from_object_is_callable(self):
        class Person(models.Model):
            pass
        assert callable(Person.fill_from_object), 'A deadparrot model should have the method "fill_from_object"'

    def test_fill_from_object_success_with_unicode(self):
        class Person(models.Model):
            name = models.CharField(max_length=40)
            creation_date = models.DateTimeField(format="%Y-%m-%d %H:%M:%S")
            email = models.EmailField()

        class FooBarJohn:
            name = u'John Doe'
            email = u'john@doe.net'

        john1 = Person.fill_from_object(FooBarJohn)
        john2 = Person.fill_from_object(FooBarJohn())

        assert john1.name == u'John Doe', 'john1.name should be u"John Doe", got %r' % john1.name
        assert john1.email == u'john@doe.net', 'john1.email should be u"john@doe.net", got %r' % john1.email
        assert john2.name == u'John Doe', 'john2.name should be u"John Doe", got %r' % john2.name
        assert john2.email == u'john@doe.net', 'john2.email should be u"john@doe.net", got %r' % john2.email

    def test_fill_from_object_success_with_string(self):
        class Person(models.Model):
            name = models.CharField(max_length=40)
            creation_date = models.DateTimeField(format="%Y-%m-%d %H:%M:%S")
            email = models.EmailField()

        class FooBarJohn:
            name = 'John Doe'
            email = 'john@doe.net'

        john1 = Person.fill_from_object(FooBarJohn)
        john2 = Person.fill_from_object(FooBarJohn())

        assert john1.name == u'John Doe', 'john1.name should be u"John Doe", got %r' % john1.name
        assert john1.email == u'john@doe.net', 'john1.email should be u"john@doe.net", got %r' % john1.email
        assert john2.name == u'John Doe', 'john2.name should be u"John Doe", got %r' % john2.name
        assert john2.email == u'john@doe.net', 'john2.email should be u"john@doe.net", got %r' % john2.email

    def test_fill_from_object_success_with_string_new_style_class(self):
        class Person(models.Model):
            name = models.CharField(max_length=40)
            creation_date = models.DateTimeField(format="%Y-%m-%d %H:%M:%S")
            email = models.EmailField()

        class FooBarJohn(object):
            name = 'John Doe'
            email = 'john@doe.net'

        john1 = Person.fill_from_object(FooBarJohn)
        john2 = Person.fill_from_object(FooBarJohn())

        assert john1.name == u'John Doe', 'john1.name should be u"John Doe", got %r' % john1.name
        assert john1.email == u'john@doe.net', 'john1.email should be u"john@doe.net", got %r' % john1.email
        assert john2.name == u'John Doe', 'john2.name should be u"John Doe", got %r' % john2.name
        assert john2.email == u'john@doe.net', 'john2.email should be u"john@doe.net", got %r' % john2.email

    def test_fill_from_object_success_retrieve_callable_results_string(self):
        '''If the object we are retrieving attributes from, has a
        callable with the same name as an attribute of deadparrot,
        then I try to get its value'''

        class Person(models.Model):
            name = models.CharField(max_length=40)
            email = models.EmailField()

        class FooBarJohn(object):
            name = u'John Doe'

            def email(self):
                return u'john@doe.net'

        john1 = Person.fill_from_object(FooBarJohn())
        assert john1.name == u'John Doe', 'john1.name should be u"John Doe", got %r' % john1.name
        assert john1.email == u'john@doe.net', 'john1.email should be u"john@doe.net", got %r' % john1.email

    def test_fill_from_object_success_retrieve_callable_with_params_does_not_work(self):
        '''If the callable takes parameters, I just ignore it'''

        class Person(models.Model):
            name = models.CharField(max_length=40)
            email = models.EmailField()

        class FooBarJohn(object):
            name = u'John Doe'

            def email(self, param1):
                return u'john@doe.net'

        john1 = Person.fill_from_object(FooBarJohn())
        assert john1.name == u'John Doe', 'john1.name should be u"John Doe", got %r' % john1.name
        assert john1.email == None, 'john1.email should be None, got %r' % john1.email

    def test_fill_from_object_success_none_will_be_ignored(self):
        from datetime import date, datetime
        class Person(models.Model):
            name = models.CharField(max_length=40)
            email = models.EmailField()
            age = models.IntegerField()
            birthdate = models.DateField()

        class FooBarJohn(object):
            name = None
            birthdate = date(2000, 10, 10)

            def age(self):
                delta = datetime.now().date() - self.birthdate
                return delta.days / 365

            def email(self):
                return None

        john1 = Person.fill_from_object(FooBarJohn())
        expected_age = (datetime.now().date() - date(2000, 10, 10)).days / 365

        assert john1.name == None, \
               'john1.name should be None, got %r' % john1.name
        assert john1.email == None, \
               'john1.email should be None, got %r' % john1.email
        assert john1.age == expected_age, \
               'john1.age should be %d, got %r' % (expected_age, john1.email)
        assert john1.birthdate == date(2000, 10, 10), \
               'john1.birthdate should be datetime.date(2000, 10, 10) got %r' % (datetime.now().year - 2000, john1.email)
