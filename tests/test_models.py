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

class TestAttributes(unittest.TestCase):
    def test_unicode(self):
        from deadparrot.client.models import Attribute
        nc = Attribute(unicode)
        nc.fill('full_name', 'John Doe')
        self.assertEquals(nc.name, 'full_name')
        self.assertEquals(nc.camel_name, 'fullName')
        self.assertEquals(nc.value, u'John Doe')

    def test_float(self):
        from deadparrot.client.models import Attribute
        nc = Attribute(float)
        nc.fill('weight', '120.53')
        self.assertEquals(nc.name, 'weight')
        self.assertEquals(nc.camel_name, 'weight')
        self.assertEquals(nc.value, 120.53)

    def test_int(self):
        from deadparrot.client.models import Attribute
        nc = Attribute(int)
        nc.fill('age', '21.53')
        self.assertEquals(nc.name, 'age')
        self.assertEquals(nc.camel_name, 'age')
        self.assertEquals(nc.value, 21)

    def test_datetime(self):
        from deadparrot.client.models import DateTimeAttribute
        from datetime import datetime
        nc = DateTimeAttribute("%Y/%m/%d %H:%M:%S")
        nc.fill('creation_date', '2009/03/24 00:46:20')
        self.assertEquals(nc.name, 'creation_date')
        self.assertEquals(nc.camel_name, 'creationDate')
        self.assertEquals(nc.value.date(), datetime(2009, 3, 24).date())
