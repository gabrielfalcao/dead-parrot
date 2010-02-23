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

from utils import assert_raises

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

class TestForeignKey(unittest.TestCase):
    def test_not_lazy_not_referenced(self):
        class DummyModelFk1(models.Model):
            pass

        fk = models.ForeignKey(DummyModelFk1)
        assert not fk.is_lazy
        assert not fk.is_self_referenced

    def test_lazy_not_referenced(self):
        class DummyModelFk2(models.Model):
            pass

        fk = models.ForeignKey('DummyModelFk2')
        assert fk.is_lazy
        assert not fk.is_self_referenced

    def test_lazy_and_self_referenced(self):
        fk = models.ForeignKey('self')
        assert fk.is_lazy
        assert fk.is_self_referenced

    def test_resolve_sucess(self):
        class DummyModelFk3(models.Model):
            pass

        fk = models.ForeignKey('DummyModelFk3')
        assert fk.from_model is None
        assert fk.is_lazy
        fk.resolve()
        assert fk.to_model is DummyModelFk3
        assert not fk.is_lazy

    def test_resolve_fail_unknown_class(self):
        fk = models.ForeignKey('dasdDSdsa2er3')
        assert_raises(AttributeError, fk.resolve)

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

    def test_raises_when_not_model(self):
        try:
            Parrot(id=1,
                   name=u"Polly",
                   is_dead=True,
                   cage='cage')
            raise AssertionError('deadparrot should not allow setting ' \
                                 'a fk value as anything, but its fk '\
                                 'model correspondent instance')
        except TypeError, e:
            assert unicode(e) == "'cage' is not a Cage instance, it is actually a <type 'str'>", \
                   'Error description does not match: %r' % unicode(e)

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
    unevaluated_json = demjson.encode({
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
    evaluated_json = demjson.encode({
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
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))
        self.assertEquals(one_line_xml(polly.serialize(to='xml')),
                          one_line_xml(self.unevaluated_xml))

    def test_to_xml_evaluated(self):
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1, color=u'black'))
        self.assertEquals(one_line_xml(polly.serialize(to='xml')),
                          one_line_xml(self.evaluated_xml))

    def test_to_json_unevaluated(self):
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1))
        self.assertEquals(polly.serialize(to='json'),
                          self.unevaluated_json)

    def test_to_json_evaluated(self):
        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cage=Cage(id=1, color=u'black'))
        self.assertEquals(polly.serialize(to='json'),
                          self.evaluated_json)

    def test_from_xml_unevaluated(self):
        xml = """
        <Computer>
          <ram>2GB</ram>
          <processor>
            <Cpu>
              <id>1</id>
            </Cpu>
          </processor>
          <id>1</id>
          <storage>500GB</storage>
        </Computer>
        """
        class Cpu(models.Model):
            id = models.IntegerField(primary_key=True)

        class Computer(models.Model):
            id = models.IntegerField(primary_key=True)
            ram = models.CharField(max_length=20)
            storage = models.CharField(max_length=20)
            processor = models.ForeignKey(Cpu)


        balarama = Computer(id=1, ram='2GB', storage='500GB', processor=Cpu(id=1))

        deserialized_balarama = Computer.deserialize(xml, format='xml')
        self.assertEquals(balarama, deserialized_balarama)
