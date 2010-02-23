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

class TestAutoForeignKey:
    def test_set_from_model_through_model_name(self):
        class TotallyNewNameClassFromModel(models.Model):
            id = models.IntegerField(primary_key=True)
            name = models.CharField(max_length=40, primary_key=True)
            mother = models.ForeignKey('TotallyNewNameClassFromModel')

        p = TotallyNewNameClassFromModel(id=2,
                   name='Polly',
                   mother=TotallyNewNameClassFromModel(id=1, name="Polly's mom"))

        assert p.mother._from_model is TotallyNewNameClassFromModel, \
               'The model should be %r got %r' % (TotallyNewNameClassFromModel, p.mother._from_model)

    def test_set_to_model_through_model_name(self):
        class TotallyNewNameClassToModel(models.Model):
            id = models.IntegerField(primary_key=True)
            name = models.CharField(max_length=40, primary_key=True)
            mother = models.ForeignKey('TotallyNewNameClassToModel')

        p = TotallyNewNameClassToModel(id=2,
                    name='Polly',
                    mother=TotallyNewNameClassToModel(id=1, name="Polly's mom"))

        assert p.mother._to_model is TotallyNewNameClassToModel, \
               'The model should be %r got %r' % (TotallyNewNameClassToModel, p.mother._to_model)

    def test_set_from_model_through_self(self):
        class Software(models.Model):
            name = models.CharField(max_length=40, primary_key=True)
            os = models.ForeignKey('self')

        s = Software(name='GNOME', os=Software(name="GNU/Linux"))

        assert s.os._from_model is Software
