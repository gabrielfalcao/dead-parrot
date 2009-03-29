#!/usr/bin/env python
# -*- coding: utf-8; -*-
from attributes import *

class FieldValidationError(Exception):
    pass

class Field(Attribute):
    must_validate = True
    vartype = None
    def __init__(self, *args, **kw):
        validate = kw.pop('validate', True)
        if not isinstance(validate, bool):
            raise TypeError, u"%s.validate param must be a bool" \
                  " (True or False), got %r (%r)" % \
                  (self.__class__.__name__,
                   type(validate), validate)

        self.must_validate = validate
        super(Field, self).__init__(self.vartype, *args, **kw)


class CharField(Field):
    max_length = None
    vartype = unicode
    def __init__(self, *args, **kw):
        max_length = kw.pop('max_length', None)
        if not isinstance(max_length, int):
            raise TypeError, u"%s.max_length param must be a int" \
                  " got a %r (%r)" % \
                  (self.__class__.__name__,
                   type(max_length), max_length)

        self.max_length = max_length
        super(CharField, self).__init__(*args, **kw)

    def validate(self, value):
        if not isinstance(value, self.vartype):
            raise TypeError, \
                  u"%s must be unicode for CharField compatibility" % value

        if self.validate and len(value) > self.max_length:
            raise FieldValidationError, \
                  u"%s have %d characters, " \
                  "but the CharField %s supports "\
                  "at maximum %d characters" % (value,
                                                len(value),
                                                self.name,
                                                self.max_length)


class DateTimeField(CharField, DateTimeAttribute):
    format = "%Y-%m-%d %H:%M:%S"
    def __init__(self, *args, **kw):
        format = kw.pop('format', "%Y-%m-%d %H:%M:%S")
        kw['max_length'] = len(format)
        if not isinstance(format, basestring):
            raise TypeError, u"%s.max_length param must be a string" \
                  " got a %r (%r)" % \
                  (self.__class__.__name__,
                   type(format), format)

        self.format = format
        super(DateTimeField, self).__init__(*args, **kw)
