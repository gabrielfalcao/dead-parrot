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
import os
import unittest
import pmock
import sqlite3
from datetime import datetime, date
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import clear_mappers

from deadparrot import models

from utils import one_line_xml

class TestSQLAlchemyManager(unittest.TestCase):
    def setUp(self):
        class Person(models.Model):
            id = models.IntegerField(primary_key=True)
            name = models.CharField(max_length=40)
            creation_date = models.DateTimeField(format="%Y-%m-%d %H:%M:%S")
            email = models.EmailField()
            weight = models.FloatField()
            married = models.BooleanField(positives=["true", "yes"],
                                          negatives=["false", "no"])
            childrens = models.IntegerField()
            cellphone = models.PhoneNumberField(format="(00) 0000-0000")
            biography = models.TextField()
            blog = models.URLField(verify_exists=False)

            objects = models.SQLAlchemyManager(create_schema=True, engine="sqlite:///:memory:")

            @property
            def age(self):
                return (datetime.now().date() - self.birthdate).days / 365

        self.Person = Person
        
    def tearDown(self):
        for person in self.Person.objects.all():
            person.delete()
        
    def test_construction(self):
        FooModel = type('FooModel', (models.Model,), {})
        Builder, args, kw = models.SQLAlchemyManager(create_schema=False)
        self.assertRaises(AttributeError,
                          Builder, model=FooModel, *args, **kw)

        class BarModel(models.Model):
            foo = models.IntegerField(primary_key=True)

        objects = Builder(model=BarModel, *args, **kw)
        self.assert_(issubclass(Builder, models.SQLAlchemyManagerBuilder))
        self.assert_(isinstance(objects, models.SQLAlchemyManagerBuilder))

    def test_engine_setup(self):
        class House(models.Model):
            id = models.IntegerField(primary_key=True)
            address = models.TextField()
            objects = models.SQLAlchemyManager(engine="sqlite:///test.db",
                                               create_schema=True)
            
        House.objects.create(address=u'Test 1')
        House.objects.create(address=u'Test 2')
        
        connection = sqlite3.Connection('test.db')
        cursor = connection.cursor()
        
        results = list(cursor.execute('select address from house;'))
        
        self.assertEquals(results[0][0], 'Test 1')
        self.assertEquals(results[1][0], 'Test 2')
        
        os.remove('test.db')
        
    def test_create(self):
        john = self.Person.objects.create(name=u'John Doe',
                                          creation_date=datetime.now(),
                                          email=u"john@doe.net",
                                          weight=74.35,
                                          married=False,
                                          childrens=2,
                                          cellphone=u"(21) 9988-7766",
                                          biography=u"blabla",
                                          blog=u"http://blog.john.doe.net")
        self.assert_(isinstance(john, self.Person))
        self.assertEquals(john.name, u'John Doe')

    def test_get_all(self):
        test = self.Person.objects.create(name="Test")
        self.assertEquals(len(self.Person.objects.all()), 1)

    def test_get(self):
        test = self.Person.objects.create(name=u"Test")
        self.assertEquals(self.Person.objects.get(name=u"Test"), test)

    def test_delete(self):
        p = self.Person.objects.create(name="Blah")
        self.assertEquals(len(self.Person.objects.all()), 1)
        p.delete()
        self.assertEquals(len(self.Person.objects.all()), 0)

    def test_delete_raises(self):
        self.assertRaises(InvalidRequestError, self.Person(name="Blah").delete)

    def test_save(self):
        p = self.Person(name="Blah")
        self.assertEquals(len(self.Person.objects.all()), 0)
        p.save()
        self.assertEquals(len(self.Person.objects.all()), 1)
        p.delete()
        self.assertEquals(len(self.Person.objects.all()), 0)
        
    def test_filter(self):
        self.assertEquals(len(self.Person.objects.all()), 0)
        john = self.Person.objects.create(name="John Doe")
        mary = self.Person.objects.create(name="Mary Doe")

        people = self.Person.objects.filter(self.Person.name.like(u'%Doe%'))
        self.assertEquals(len(people), 2)
        self.assert_(john in people)
        self.assert_(mary in people)

    def test_filter_with_kwargs(self):
        self.assertEquals(len(self.Person.objects.all()), 0)
        john1 = self.Person.objects.create(name="John Doe", married=True)
        john2 = self.Person.objects.create(name="John Doe", married=False)
        john3 = self.Person.objects.create(name="John Doe", married=False)        

        people = self.Person.objects.filter(name=u'John Doe')
        self.assertEquals(len(people), 3)
        self.assert_(john1 in people)
        self.assert_(john2 in people)
        self.assert_(john3 in people)        

    def test_serialization_xml(self):
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
        john = self.Person.objects.create(name=u'John Doe',
                                          creation_date=dtime,
                                          email=u"john@doe.net",
                                          weight=74.35,
                                          married=False,
                                          childrens=2,
                                          cellphone=u"(21) 9988-7766",
                                          biography=u"blabla",
                                          blog=u"http://blog.john.doe.net")

        self.assertEquals(one_line_xml(john.serialize(to='xml')),
                          one_line_xml(xml))

    
    def test_deserialization_xml(self):
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
        
        john1 = self.Person.deserialize(xml, format='xml')
        john1.save()
        john2 = self.Person.objects.get(name=u'John Doe')
        self.assertEquals(john1, john2)

    def test_foreign_key(self):
        class PetShop(models.Model):
            id = models.IntegerField(primary_key=True)
            name = models.CharField(max_length=40)
            objects = models.SQLAlchemyManager(create_schema=True,
                                               engine="sqlite:///test.db")

        class Pet(models.Model):
            id = models.IntegerField(primary_key=True)
            animal = models.CharField(max_length=40)
            home = models.ForeignKey(self.Person) 
            objects = models.SQLAlchemyManager(create_schema=True,
                                               engine="sqlite:///test.db")

            def __unicode__(self):
                return unicode(u"%s of %s"% (self.animal, self.owner.name))
            
        dogstore = PetShop.objects.create(name=u'Dog Store')            
        dog1 = Pet.objects.create(animal=u'Dog', home=dogstore)
        
        rex = Pet.objects.filter(Pet.animal==u'Dog')[0]
        
        self.assert_(rex.petshop is not None)
        self.assertEquals(rex.petshop.name, u'Dog Store')
        self.assertEquals(rex.petshop, dogstore)        
