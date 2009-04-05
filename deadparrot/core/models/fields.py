#!/usr/bin/env python
# -*- coding: utf-8; -*-
import re
from attributes import *
from decimal import Decimal, InvalidOperation

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

        if self.must_validate and len(value) > self.max_length:
            raise FieldValidationError, \
                  u"%s have %d characters, " \
                  "but the CharField %s supports "\
                  "at maximum %d characters" % (value,
                                                len(value),
                                                self.name,
                                                self.max_length)


class DateTimeField(CharField, DateTimeAttribute):
    vartype = "%Y-%m-%d %H:%M:%S"

    def __init__(self, *args, **kw):
        vartype = kw.pop('format', self.vartype)

        if not isinstance(vartype, basestring):
            raise TypeError, u"%s.format param must be a string" \
                  " got a %r (%r)" % \
                  (self.__class__.__name__,
                   type(vartype), vartype)

        kw['max_length'] = len(vartype)
        # considering that %Y have 4 chars, lets add 2+ to the max_length
        if "%Y" in vartype:
            kw['max_length'] += 2


        self.vartype = vartype
        super(DateTimeField, self).__init__(*args, **kw)

    def validate(self, value):
        klassname = self.__class__.__name__
        if datetime.now().strftime(self.vartype) == self.vartype:
            raise FieldValidationError, \
                  u'"%s" is not a valid datetime format, ' % value

class DateField(DateTimeField, DateAttribute):
    vartype = "%Y-%m-%d"

class TimeField(DateTimeField, TimeAttribute):
    vartype = "%H:%M:%S"

class DecimalField(Field):
    max_digits = 0
    decimal_places = 0
    vartype = Decimal

    def __init__(self, *args, **kw):
        for param in 'max_digits', 'decimal_places':
            val = kw.pop(param, 0)

            if isinstance(val, int):
                setattr(self, param, val)
            else:
                raise TypeError, u"%s.%s param must be a int" \
                      " got a %r (%r)" % \
                      (self.__class__.__name__, param,
                       type(val), val)

        super(DecimalField, self).__init__(*args, **kw)

    def validate(self, value):
        if not isinstance(value, basestring):
            raise TypeError, \
                  u"%s must be a string for DecimalField " \
                  "compatibility" % value
        try:
            floated_value = float(Decimal(value))
        except InvalidOperation:
            raise FieldValidationError, 'the string "%s" is ' \
                  "not a valid decimal number" % value

        to_validate = u"%.*f" % (self.decimal_places, floated_value)
        if (len(to_validate) - 1) != self.max_digits:
            raise FieldValidationError, "%s do not have %d max " \
                  "digits and %d decimal places" % (value,
                                                    self.max_digits,
                                                    self.decimal_places)

class EmailField(CharField):
    vartype = unicode
    def __init__(self, *args, **kw):
        kw['max_length'] = 255
        super(EmailField, self).__init__(*args, **kw)

    def validate(self, value):
        if not isinstance(value, basestring):
            raise TypeError, \
                  u"%s must be a string(ish) type " \
                  "for EmailField compatibility" % value

        email_regex = re.compile(r'^[a-z0-9_.-]{2,}@[\w_.-]{3,}' \
                                 '[.][a-z]{2,}([.][a-z]{2,})*', re.I)

        if not email_regex.search(value):
            raise FieldValidationError, 'The email is not valid: "%s"'% value
