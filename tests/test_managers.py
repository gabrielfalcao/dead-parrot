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

from datetime import datetime, date

from deadparrot import models

# TODO: test serialization/deserialization of values that came from SQLAlchemy

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

            objects = models.SQLAlchemyManager(create_schema=True)

            @property
            def age(self):
                return (datetime.now().date() - self.birthdate).days / 365

        self.Person = Person

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
        john.delete()

    def test_get_all(self):
        test = self.Person.objects.create(name="Test")
        self.assertEquals(len(self.Person.objects.all()), 1)

    def test_delete(self):
        p = self.Person.objects.create(name="Blah")
        self.assertEquals(len(self.Person.objects.all()), 1)
        p.delete()
        self.assertEquals(len(self.Person.objects.all()), 0)

    def test_filter(self):

        self.assertEquals(len(self.Person.objects.all()), 0)
        john = self.Person.objects.create(name="John Doe")
        mary = self.Person.objects.create(name="Mary Doe")

        people = self.Person.objects.filter(self.Person.name.like('%Doe%'))
        self.assertEquals(len(people), 2)
        self.assert_(john in people)
        self.assert_(mary in people)
        john.delete()
        mary.delete()
