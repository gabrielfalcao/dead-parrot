#!/usr/bin/env python
# -*- coding: utf-8; -*-

from datetime import datetime, date, time, timedelta

def camelize_string(string):
    camel_part =  "".join([s.title() for s in string.split("_")][1:])
    return string.split("_")[0].lower() + camel_part

class Attribute(object):
    name = None
    __value = None

    def __init__(self, vartype, name=None, value=None):
        self.vartype = vartype
        if name and value:
            self.fill(name, value)

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
        return unicode(value or self.value)

    def fill(self, name, value):
        self.name = name
        self.value = value
        return self

    def __unicode__(self):
        return unicode(self.value or "")

    def __repr__(self):
        return "<%s%s:%s%s attribute object at 0x%r>" % (str(self.vartype.__name__.title()),
                                                       self.__class__.__name__,
                                                       self.name,
                                                       self.value and "=%r" % self.value,
                                                       id(self))

class DateTimeAttribute(Attribute):
    def serialize(self, value=None):
        value = value or self.value
        return unicode(value.strftime(self.vartype))

    def convert_type(self, val):
        if isinstance(val, basestring):
            if val:
                return datetime.strptime(val, self.vartype)
            else:
                return datetime.now()
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
            if val:
                return datetime.strptime(val, self.vartype).time()
            else:
                return datetime.now().time()
        elif isinstance(val, time):
            return val
        else:
            raise TypeError, "TimeAttribute "\
                  "deals only with strings and "\
                  "datetime.time() objects. Got %r" % type(val)


class DateAttribute(DateTimeAttribute):
    def convert_type(self, val):
        if isinstance(val, basestring):
            if val:
                return datetime.strptime(val, self.vartype).date()
            else:
                return datetime.now().date()
        elif isinstance(val, date):
            return val
        else:
            raise TypeError, "DateAttribute "\
                  "deals only with strings and "\
                  "datetime.date() objects. Got %r" % type(val)
