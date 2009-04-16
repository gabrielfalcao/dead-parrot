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
from deadparrot.core.serialization.json import JSONSerializer
from deadparrot.core.serialization.xml import XMLSerializer
from deadparrot.core.serialization import Registry
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
        self.assertEquals(jserial.serialize(),
                          simplejson.dumps(self.my_dict))

    def test_deserialization(self):
        json = simplejson.dumps(self.my_dict)
        self.assertEquals(JSONSerializer.deserialize(json),
                          self.my_dict)

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

class TestSerializersRegistry(unittest.TestCase):
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

    def test_get_xml_serializer(self):
        xml_serializer = Registry.get("xml")
        self.assertEquals(xml_serializer.deserialize(self.my_xml),
                          self.my_dict)

    def test_get_json_serializer(self):
        json_serializer = Registry.get("json")
        json = simplejson.dumps(self.my_dict)
        self.assertEquals(json_serializer.deserialize(json),
                          self.my_dict)
