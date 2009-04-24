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

from deadparrot import models

class TestForeignKey(unittest.TestCase):
    def _test_relation_with_class_object(self):
        class Cage(Model):
            id = models.IntegerField(primary_key=True)
            color = models.CharField(max_length=30)

        class Parrot(Model):
            id = models.IntegerField(primary_key=True)            
            name = models.CharField(max_length=40, primary_key=True)
            is_dead = models.BooleanField()
            cage = models.ForeignKey(Cage)

        pollys_cage = Cage(id=1, color=u'black')
        polly = Person(id=1, first_name=u"Polly", is_dead=True, cage=Cage(color=u'black'))
        self.assertEquals(polly.cage, pollys_cage)
