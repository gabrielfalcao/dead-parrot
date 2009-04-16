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
import simplejson

from re import sub as resub
from urllib2 import URLError

from deadparrot.core import models
from deadparrot.core.models import fields
from deadparrot.core.serialization import JSONSerializer
from deadparrot.core.serialization import XMLSerializer
from deadparrot.core.models import Model

from datetime import date, time, datetime
from decimal import Decimal

class TestJSONSerializer(unittest.TestCase):
    my_dict = {
        'Person': {
            'wage': u'4500.00',
            'cellphone': u'(21) 9900-1234'
        }
    }
    def test_serialization(self):
        jserial = JSONSerializer(self.my_dict)
        self.assertEquals(jserial.serialize(), simplejson.dumps(self.my_dict))

    def test_deserialization(self):
        json = simplejson.dumps(self.my_dict)
        self.assertEquals(JSONSerializer.deserialize(json), self.my_dict)

    def test_fail_construct(self):
        self.assertRaises(TypeError, JSONSerializer, 0)
        self.assertRaises(TypeError, JSONSerializer, "")
        self.assertRaises(TypeError, JSONSerializer, None)
        self.assertRaises(TypeError, JSONSerializer, "sadasd")

def one_line_xml(string):
    string = "".join(string.splitlines())
    string = resub("[>]\s+[<]", "><", string)
    string = string.strip()
    return string

class TestXMLSerializer(unittest.TestCase):
    my_dict = {
        'Person': {
            'wage': u'4500.00',
            'cellphone': u'(21) 9900-1234'
        }
    }
    my_xml = """
    <Person>
       <wage>4500.00</wage>
       <cellphone>(21) 9900-1234</cellphone>
    </Person>
    """
    def test_fail_construction(self):
        self.assertRaises(TypeError, XMLSerializer, None)
        self.assertRaises(TypeError, XMLSerializer, "")
        self.assertRaises(TypeError, XMLSerializer, 0)

    def test_serialization(self):
        xserial = XMLSerializer(self.my_dict)
        xml = one_line_xml(self.my_xml)
        self.assertEquals(one_line_xml(xserial.serialize()), xml)

    def test_deserialization(self):
        xserial = XMLSerializer.deserialize(self.my_xml)
        self.assertEquals(xserial, self.my_dict)

# class TestSerializationJSON(unittest.TestCase):
#     def setUp(self):
#         class Person(Model):
#             first_name = fields.CharField(max_length=40)
#             last_name = fields.CharField(max_length=40)
#             birthdate = fields.DateField(format="%d/%m/%Y")
#             wakeup_at = fields.TimeField(format="%H:%M:%S")
#             creation_date = fields.DateTimeField(format="%Y-%m-%d %H:%M:%S")
#             wage = fields.DecimalField(max_digits=6, decimal_places=2)
#             email = fields.EmailField()
#             favorite_phrase = fields.CharField(max_length=0, validate=False)
#             weight = fields.FloatField()
#             married = fields.BooleanField(positives=["true", "yes"],
#                                           negatives=["false", "no"])
#             childrens = fields.IntegerField()
#             cellphone = fields.PhoneNumberField(format="(00) 0000-0000")
#             biography = fields.TextField()
#             blog = fields.URLField(verify_exists=False)

#             @property
#             def full_name(self):
#                 return u"%s %s" % (self.first_name, self.last_name)

#             def __unicode__(self):
#                 return "%s, son of %s" % (self.full_name, self.father.full_name)

#             class Meta:
#                 fields_validation_policy = models.VALIDATE_NONE

#         self.PersonClass = Person

#     def test_field_fail(self):
#         my_json = simplejson.dumps({
#             'Person': {
#                 'wage': u'4500.00',
#                 'cellphone': u'(21) 9900-1234',
#                 'first_name': u'John',
#                 'last_name': u'Doe',
#                 'childrens': 2,
#                 'weight': 80.0,
#                 'wakeup_at': u'08:15:00',
#                 'married': True,
#                 'birthdate': u'10/10/1970',
#                 'creation_date': u'2009-04-11 09:36:49',
#                 'blog': u'http://blogs.somecorp.com/johndoe',
#                 'favorite_phrase': u'TDD rockz!',
#                 'email': u'johndoe@somecorp.com',
#                 'biography': u'A pretty much clever dude'
#             }
#         })
#         john = self.PersonClass()
#         john.first_name = u"John"
#         john.last_name = u"Doe"
#         john.birthdate = date(1970, 10, 10)
#         john.wakeup_at = time(8, 15, 0)
#         john.creation_date = datetime.now()
#         john.wage = "4500.00"
#         john.email = "johndoe@somecorp.com"
#         john.favorite_phrase = u"TDD rockz!"
#         john.weight = 80
#         john.married = True
#         john.childrens = 2
#         john.cellphone = "(21) 9900-1234"
#         john.biography = u"A pretty much clever dude"
#         john.blog = "http://blogs.somecorp.com/johndoe"
#         self.assertEquals(john.serialize(to='json'),
#                           simplejson.dumps(my_json))
