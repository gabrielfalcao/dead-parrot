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

from utils import assert_raises

from deadparrot import models

class TestRelationShipBaseInternals:
    def test_set_from_model_fail_when_not_deadparrot_model(self):
        rl = models.RelationShip()
        assert_raises(TypeError, rl.set_from_model, object())
        assert_raises(TypeError, rl.set_from_model, "")
        assert_raises(TypeError, rl.set_from_model, None)
        assert_raises(TypeError, rl.set_from_model, {})
        assert_raises(TypeError, rl.set_from_model, [])
        assert_raises(TypeError, rl.set_from_model, ())

    def test_set_from_model_success(self):
        class MyModelRSBaseZero(models.Model):
            pass

        rl = models.RelationShip()
        rl.set_from_model(MyModelRSBaseZero)
        assert rl.from_model is MyModelRSBaseZero, \
               'rl.from_model should be %r, got %r' % (MyModelRSBaseZero,
                                                       rl.from_model)

    def test_set_to_model_fail_when_not_deadparrot_model(self):
        rl = models.RelationShip()
        assert_raises(TypeError, rl.set_to_model, object())
        assert_raises(TypeError, rl.set_to_model, "")
        assert_raises(TypeError, rl.set_to_model, None)
        assert_raises(TypeError, rl.set_to_model, {})
        assert_raises(TypeError, rl.set_to_model, [])
        assert_raises(TypeError, rl.set_to_model, ())

    def test_set_to_model_success(self):
        class MyModelRSBaseOne(models.Model):
            pass

        rl = models.RelationShip()
        rl.set_to_model(MyModelRSBaseOne)
        assert rl.to_model is MyModelRSBaseOne, \
               'rl.to_model should be %r, got %r' % (MyModelRSBaseOne,
                                                     rl.to_model)

    def test_set_as_lazy_fail_when_not_not_bool(self):
        rl = models.RelationShip()
        assert_raises(TypeError, rl.set_lazy, None)
        assert_raises(TypeError, rl.set_lazy, object())
        assert_raises(TypeError, rl.set_lazy, {})
        assert_raises(TypeError, rl.set_lazy, [])
        assert_raises(TypeError, rl.set_lazy, ())

    def test_set_as_lazy_success(self):
        rl1 = models.RelationShip()
        rl1.set_lazy(True)
        rl2 = models.RelationShip()
        rl2.set_lazy(False)

        assert rl1.is_lazy is True
        assert rl2.is_lazy is False

    def test_set_as_self_referenced_fail_when_not_not_bool(self):
        rl = models.RelationShip()
        assert_raises(TypeError, rl.set_self_referenced, None)
        assert_raises(TypeError, rl.set_self_referenced, object())
        assert_raises(TypeError, rl.set_self_referenced, {})
        assert_raises(TypeError, rl.set_self_referenced, [])
        assert_raises(TypeError, rl.set_self_referenced, ())

    def test_set_as_self_referenced_success(self):
        rl1 = models.RelationShip()
        rl1.set_self_referenced(True)
        rl2 = models.RelationShip()
        rl2.set_self_referenced(False)

        assert rl1.is_self_referenced is True
        assert rl2.is_self_referenced is False
