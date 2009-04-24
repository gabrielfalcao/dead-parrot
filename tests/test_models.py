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

from deadparrot.models import fields, base
from deadparrot import models
from deadparrot.models import Model
from deadparrot.models import build_metadata
from datetime import date, time, datetime

from utils import one_line_xml

class TestBasicModel(unittest.TestCase):
    def test_build_metadata_verbose_name(self):
        class Car(Model):
            pass

        self.assertEquals(build_metadata(Car, {}).verbose_name, 'Car')
        self.assertEquals(build_metadata(Car, {}).verbose_name_plural, 'Cars')

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

    def test_to_list_operations(self):
        class Person(Model):
            name = fields.CharField(max_length=10)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                verbose_name_plural = 'People'

        person1 = Person(name=u'John Doe', birthdate=u'10/02/1988')
        person2 = Person(name=u'Mary Doe', birthdate=u'20/10/1989')
        PersonSet = Person.Set()
        people = PersonSet(person1, person2)

        # getitem
        self.assertEquals(people[0].name, u'John Doe')
        # length
        self.assertEquals(len(people), 2)
        # nonzero
        self.assertEquals(bool(people), True)
        self.assertEquals(bool(PersonSet()), False)
        # iteration
        self.assertEquals([u'John Doe', u'Mary Doe'],
                          [x.name for x in people])

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

class TestModelSetSerialization(unittest.TestCase):
    class Person(Model):
            first_name = fields.CharField(max_length=40)
            birthdate = fields.DateField(format="%d/%m/%Y")
            class Meta:
                verbose_name_plural = 'People'

    my_json = simplejson.dumps({
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
        person2 = Person(name=u"blaj", birthdate=u'10/10/2000')        
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
