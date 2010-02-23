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
from deadparrot.serialization import Registry
from deadparrot.serialization.plugins.json import JSONSerializer
from deadparrot.serialization.plugins.xml import XMLSerializer
from deadparrot.serialization.plugins.base import Serializer

from utils import one_line_xml

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
                          demjson.encode(self.my_dict))

    def test_deserialization(self):
        json = demjson.encode(self.my_dict)
        self.assertEquals(JSONSerializer.deserialize(json),
                          self.my_dict)

    def test_fail_construct(self):
        self.assertRaises(TypeError, JSONSerializer, 0)
        self.assertRaises(TypeError, JSONSerializer, "")
        self.assertRaises(TypeError, JSONSerializer, None)
        self.assertRaises(TypeError, JSONSerializer, "sadasd")

class TestXMLSerializer(unittest.TestCase):
    my_dict = {
        'Person': {
            'wage': u'4500.00',
            'cellphone': u'(21) 9900-1234'
        }
    }
    missing_dict = {
        'Person': {
            'wage': u'4500.00',
            'cellphone': None
        }
    }
    my_xml = """
    <Person>
       <wage>4500.00</wage>
       <cellphone>(21) 9900-1234</cellphone>
    </Person>
    """
    missing_xml = """
    <Person>
       <wage>4500.00</wage>
       <cellphone></cellphone>
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

    def test_serialization_missing(self):
        xserial = XMLSerializer(self.missing_dict)
        xml = one_line_xml(self.missing_xml)
        self.assertEquals(one_line_xml(xserial.serialize()), xml)

    def test_deserialization(self):
        xserial = XMLSerializer.deserialize(self.my_xml)
        self.assertEquals(xserial, self.my_dict)

    def test_fail_as_object(self):
        xml = XMLSerializer({'blah': set(range(10))})
        self.assertRaises(TypeError, xml.as_object)

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
        json = demjson.encode(self.my_dict)
        self.assertEquals(json_serializer.deserialize(json),
                          self.my_dict)

    def test_fail_get_unknown(self):
        try:
            Registry.get('invalid-meh')
        except NotImplementedError, e:
            assert unicode(e) == "The format 'invalid-meh' was not implemented " \
                   "as a serializer plugin for DeadParrot", \
                   'Unexpected exception message %r' % unicode(e)

        self.assertRaises(NotImplementedError, Registry.get, 'blabows')

    def test_registry_requires_implementation(self):
        """
        When someone implements a serialization plugin,
        the class must have the attribute "format", which
        is a string to identify the plugin in the registry
        """
        def make_class():
            class FakeSerializer(Serializer):
                pass

        self.assertRaises(AttributeError, make_class)
