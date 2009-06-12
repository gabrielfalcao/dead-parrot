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

from utils import one_line_xml

from deadparrot import models

class Cage(models.Model):
    id = models.IntegerField(primary_key=True)
    color = models.CharField(max_length=30, blank=False)

class Parrot(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40, primary_key=True)
    is_dead = models.BooleanField(negatives=['false'],
                                  positives=['true'])
    cage = models.ForeignKey(Cage)

class TestRelationShipBase(unittest.TestCase):
    def test_set_from_model(self):
        p = Parrot(id=1,
                   name=u"Polly",
                   is_dead=True,
                   cage=Cage(id=1))
        self.assertEquals(p.cage._from_model, Parrot)

    def test_set_to_model(self):
        p = Parrot(id=1,
                   name=u"Polly",
                   is_dead=True,
                   cage=Cage(id=1))

        self.assertEquals(p.cage._to_model, Cage)

class TestForeignKey(unittest.TestCase):
    def test_relation_with_class_object(self):
        pollys_cage = Cage(id=1, color=u'black')
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))
        self.assertEquals(polly.cage, pollys_cage)

    def test_relation_with_class_string(self):
        pollys_cage = Cage(id=1, color=u'black')
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))
        self.assertEquals(polly.cage, pollys_cage)

    def test_relation_with_class_and_app_label_string(self):
        pollys_cage = Cage(id=1, color=u'black')
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))
        self.assertEquals(polly.cage, pollys_cage)

    def test_relation_with_module_name(self):
        pollys_cage = Cage(id=1, color=u'black')
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))
        self.assertEquals(polly.cage, pollys_cage)

    def test_relation_has_from_model_class_as_attribute(self):
        pollys_cage = Cage(id=1, color=u'black')
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))
        self.assertEquals(polly.cage, pollys_cage)
        self.assertEquals(polly.cage._from_model, Parrot)


    def test_relation_has_to_model_class_as_attribute(self):
        pollys_cage = Cage(id=1, color=u'black')
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))
        self.assertEquals(polly.cage, pollys_cage)
        self.assertEquals(polly.cage._to_model, Cage)

class TestForeignKeySerialization(unittest.TestCase):
    unevaluated_xml = """
    <Parrot>
      <is_dead>True</is_dead>
      <cage>
        <Cage>
          <id>1</id>
        </Cage>
      </cage>
      <id>1</id>
      <name>Polly</name>
    </Parrot>
    """
    evaluated_xml = """
    <Parrot>
      <is_dead>True</is_dead>
      <cage>
        <Cage>
          <color>black</color>
          <id>1</id>
        </Cage>
      </cage>
      <id>1</id>
      <name>Polly</name>
    </Parrot>
    """
    unevaluated_json = simplejson.dumps({
        'Parrot': {
            'is_dead': True,
            'id': 1,
            'name': u'Polly',
            'cage': {
                'Cage': {
                    'id': 1
                 }
            }
        }
    })
    evaluated_json = simplejson.dumps({
        'Parrot': {
            'is_dead': True,
            'id': 1,
            'name': u'Polly',
            'cage': {
                'Cage': {
                    'id': 1,
                    'color': u'black'
                 }
            }
        }
    })

    def test_to_xml_unevaluated(self):
        pollys_cage = Cage(id=1, color=u'black')
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))
        self.assertEquals(one_line_xml(polly.serialize(to='xml')),
                          one_line_xml(self.unevaluated_xml))

    def test_to_xml_evaluated(self):
        pollys_cage = Cage(id=1, color=u'black')
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1, color=u'black'))
        self.assertEquals(one_line_xml(polly.serialize(to='xml')),
                          one_line_xml(self.evaluated_xml))

    def test_to_json_unevaluated(self):
        pollys_cage = Cage(id=1, color=u'black')
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))
        self.assertEquals(polly.serialize(to='json'),
                          self.unevaluated_json)

    def test_to_json_evaluated(self):
        pollys_cage = Cage(id=1, color=u'black')
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1, color=u'black'))
        self.assertEquals(polly.serialize(to='json'),
                          self.evaluated_json)

    def test_from_xml_unevaluated(self):
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))

        xml_polly = Parrot.deserialize(self.unevaluated_xml, format='xml')
        self.assertEquals(xml_polly, polly)
