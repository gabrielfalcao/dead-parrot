#!/usr/bin/env python
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

REGISTRY_DICT = {}

class SerializerMeta(type):
    def __init__(cls, name, bases, attrs):
        if name not in ('SerializerMeta', 'Serializer'):
            if not attrs.has_key('format'):
                raise AttributeError, \
                      "%s does not has the attribute 'format'" % name

            REGISTRY_DICT[attrs['format']] = cls
        super(SerializerMeta, cls).__init__(name, bases, attrs)

class Serializer(object):
    __metaclass__ = SerializerMeta
