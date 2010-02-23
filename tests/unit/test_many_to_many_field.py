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

from deadparrot import models
from nose.tools import assert_equals
from utils import assert_raises

class TestManyToManyField:
    def test_not_lazy_not_referenced(self):
        class DummyModelFk1(models.Model):
            pass

        fk = models.ManyToManyField(DummyModelFk1)
        assert not fk.is_lazy
        assert not fk.is_self_referenced

    def test_lazy_not_referenced(self):
        class DummyModelFk2(models.Model):
            pass

        fk = models.ManyToManyField('DummyModelFk2')
        assert fk.is_lazy
        assert not fk.is_self_referenced

    def test_lazy_and_self_referenced(self):
        fk = models.ManyToManyField('self')
        assert fk.is_lazy
        assert fk.is_self_referenced

    def test_resolve_sucess(self):
        class DummyModelFk3(models.Model):
            pass

        fk = models.ManyToManyField('DummyModelFk3')
        assert fk.from_model is None
        assert fk.is_lazy
        fk.resolve()
        assert fk.to_model is DummyModelFk3
        assert not fk.is_lazy

    def test_resolve_fail_unknown_class(self):
        fk = models.ManyToManyField('dasdDSdsa2er3')
        assert_raises(AttributeError, fk.resolve)

    def test_auto_resolve_with_model_objects(self):
        class TestM2MSlave1(models.Model):
            id = models.IntegerField(primary_key=True)

        class TestM2MMaster1(models.Model):
            id = models.IntegerField(primary_key=True)
            slaves = models.ManyToManyField(TestM2MSlave1)

        fk = TestM2MMaster1._meta._relationships['slaves']
        assert fk.from_model is TestM2MMaster1
        assert fk.to_model is TestM2MSlave1

    def test_value_is_a_model_set_manager(self):
        class TestM2MSlave2(models.Model):
            id = models.IntegerField(primary_key=True)

        class TestM2MMaster2(models.Model):
            id = models.IntegerField(primary_key=True)
            slaves = models.ManyToManyField(TestM2MSlave2)

        master = TestM2MMaster2()
        message = 'TestM2MMaster2.slaves should be a models.ModelSetManager,' \
                  ' once this attribute was created through a models.ManyToManyField. Got %r'
        assert isinstance(master.slaves, models.ModelSetManager), message % master.slaves

    def test_model_set_manager_manages_correct_model(self):
        class TestM2MSlave3(models.Model):
            id = models.IntegerField(primary_key=True)

        class TestM2MMaster3(models.Model):
            id = models.IntegerField(primary_key=True)
            slaves = models.ManyToManyField(TestM2MSlave3)

        master = TestM2MMaster3()
        assert master.slaves.model == TestM2MSlave3, 'The ModelSetManager in TestM2MMaster3().slaves should manage the model Testm2mslave3. But actually it manages %r' % master.slaves.model

    def test_filling_model_with_m2m(self):

        class TestM2MSlave4(models.Model):
            id = models.IntegerField(primary_key=True)

        class TestM2MMaster4(models.Model):
            id = models.IntegerField(primary_key=True)
            slaves = models.ManyToManyField(TestM2MSlave4)

        master = TestM2MMaster4(id=1, slaves=[TestM2MSlave4(id=999)])
        assert_equals(master.slaves.as_modelset()[0].id, 999)

class TestManyToManyFieldMetaSerialization:
    unevaluated_dict = {
        'Parrot': {
            'is_dead': True,
            'id': 1,
            'name': u'Polly',
            'cages': {
                'Cages': [
                    {
                        'Cage': {
                            'id': 1
                        }
                    },
                    {
                        'Cage': {
                            'id': 2
                        }
                    }
                ]
            }
        }
    }

    evaluated_dict = {
        'Parrot': {
            'is_dead': True,
            'id': 1,
            'name': u'Polly',
            'cages': {
                'Cages': [
                    {
                        'Cage': {
                            'id': 1,
                            'color': u'black'
                        }
                    },
                    {
                        'Cage': {
                            'id': 2,
                            'color': u'black'
                        }
                    }
                ]
            }
        }
    }

    def test_as_dict_unevaluated(self):
        class Cage(models.Model):
            id = models.IntegerField(primary_key=True)
            color = models.CharField(max_length=30, blank=False)

        class Parrot(models.Model):
            id = models.IntegerField(primary_key=True)
            name = models.CharField(max_length=40, primary_key=True)
            is_dead = models.BooleanField(negatives=['false'],
                                          positives=['true'])
            cages = models.ManyToManyField(Cage)

        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cages=[Cage(id=1), Cage(id=2)])

        assert_equals(polly.to_dict(), self.unevaluated_dict)

    def test_as_dict_evaluated(self):
        class Cage(models.Model):
            id = models.IntegerField(primary_key=True)
            color = models.CharField(max_length=30, blank=False)

        class Parrot(models.Model):
            id = models.IntegerField(primary_key=True)
            name = models.CharField(max_length=40, primary_key=True)
            is_dead = models.BooleanField(negatives=['false'],
                                          positives=['true'])
            cages = models.ManyToManyField(Cage)

        polly = Parrot(id=1,
                       name=u"Polly",
                       is_dead=True,
                       cages=[Cage(id=1, color='black'), Cage(id=2, color='black')])

        assert_equals(polly.to_dict(), self.evaluated_dict)
