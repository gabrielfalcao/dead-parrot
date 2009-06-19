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

from datetime import datetime, date, time, timedelta

def camelize_string(string):
    camel_part =  "".join([s.title() for s in string.split("_")][1:])
    return string.split("_")[0].lower() + camel_part

class Attribute(object):
    name = None
    __value = None

    def __init__(self, vartype):
        self.vartype = vartype

    @property
    def camel_name(self):
        if self.name:
            return camelize_string(self.name)

    def convert_type(self, val):
        if self.vartype in (int, float, long):
            return self.vartype(float(val) or 0)

        elif self.vartype in (str, unicode):
            return self.vartype(val or "")
        else:
            return self.vartype(val)

    def _set_value(self, value):
        self.__value = self.convert_type(value)
    def _get_value(self):
        return self.__value
    value = property(fget=_get_value, fset=_set_value)

    def serialize(self, value=None):
        # if the type is a builtin (int, float, etc)
        # i will return him, otherway i return it stringified
        if type(value) in __builtins__.values():
            return value
        else:
            return unicode(value or self.value)

    def fill(self, name, value):
        self.name = name
        self.value = value
        return self

class DateTimeAttribute(Attribute):
    def serialize(self, value=None):
        value = value or self.value
        # sqlite quirks:
        if isinstance(value, basestring):
            value = self.convert_type(value)
        return unicode(value.strftime(self.vartype))

    def convert_type(self, val):
        if isinstance(val, basestring):
            if val:
                return datetime.strptime(val, self.vartype)

        elif isinstance(val, datetime):
            return val
        else:
            raise TypeError, "DateTimeAttribute "\
                  "deals only with strings and "\
                  "datetime.datetime() objects. "\
                  "Got %r" % type(val)

class TimeAttribute(DateTimeAttribute):
    def convert_type(self, val):
        if isinstance(val, basestring):
            return datetime.strptime(val, self.vartype).time()

        elif isinstance(val, time):
            return val
        else:
            raise TypeError, "TimeAttribute "\
                  "deals only with strings and "\
                  "datetime.time() objects. Got %r" % type(val)


class DateAttribute(DateTimeAttribute):
    def convert_type(self, val):
        if isinstance(val, basestring):
            return datetime.strptime(val, self.vartype).date()

        elif isinstance(val, date):
            return val
        else:
            raise TypeError, "DateAttribute "\
                  "deals only with strings and "\
                  "datetime.date() objects. Got %r" % type(val)
