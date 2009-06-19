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

from nose.tools import *
from deadparrot import models

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
