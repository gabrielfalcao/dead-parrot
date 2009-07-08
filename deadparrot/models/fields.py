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

import re
import urllib2
from attributes import *
from decimal import Decimal, InvalidOperation

from deadparrot.models.registry import ModelRegistry

class FieldValidationError(Exception):
    pass

class InvalidRelationShipError(Exception):
    pass

class URLChecker(object):
    def set_url(self, url):
        self.url = url

    def is_valid(self):
        url_regex = re.compile(r'^https?:[/]{2}([\w_.-]+)+[.]\w{2,}([/]?.*)?')
        return url_regex.search(self.url) and True or False

    def does_exists(self):
        try:
            urllib2.urlopen(self.url)
            return True
        except urllib2.URLError:
            return False

class Field(Attribute):
    must_validate = True
    primary_key = False
    null = True
    blank = True
    vartype = None
    def __init__(self, *args, **kw):
        d = {'blank': 'blank', 'null': 'null', 'validate': 'must_validate'}
        for attr, setname in d.items():
            pname = kw.pop(attr, True)
            if not isinstance(pname, bool):
                raise TypeError, u"%s.%s param must be a bool" \
                  " (True or False), got %r (%r)" % \
                  (self.__class__.__name__,
                   attr,
                   type(pname),
                   pname)
            else:
                setattr(self, setname, pname)

        primary_key = kw.pop('primary_key', False)
        if not isinstance(primary_key, bool):
            raise TypeError, u"%s.primary_key param must be a bool" \
                  " (True or False), got %r (%r)" % \
                  (self.__class__.__name__,
                   type(primary_key), primary_key)

        self.primary_key = primary_key
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
        if not isinstance(value, basestring):
            raise TypeError, \
                  u"%s must be a string for CharField compatibility" % value

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
        if kw.has_key('max_length'):
            kw['max_length'] = kw.get('max_length')
        else:
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

class IntegerField(Field):
    vartype = int

    def validate(self, value):
        try:
            self.vartype(value)
        except TypeError:
            raise FieldValidationError, "The value of a %s must " \
                  "be an number (even when inside a string) " \
                  "got an %s" % (self.__class__.__name__,
                                 type(value).__name__)

class FloatField(IntegerField):
    vartype = float

class BooleanField(Field):
    negatives = []
    positives = []
    vartype = bool

    def __init__(self, *args, **kw):
        for param in 'positives', 'negatives':
            val = kw.pop(param, 0)

            if isinstance(val, (list, tuple)):
                setattr(self, param, val)

            else:
                raise TypeError, u"%s.negatives param must be a list" \
                      " or tuple. But got a %r (%r)" % \
                      (self.__class__.__name__,
                       type(val), val)

        super(BooleanField, self).__init__(*args, **kw)

    def convert_type(self, val):
        if val in self.positives:
            return True

        if val in self.negatives:
            return False

        if isinstance(val, basestring):
            val = __builtins__.get(val, val)

        return val

    def validate(self, value):
        if value in self.positives or value in self.negatives:
            return

        if not isinstance(value, bool) \
               and value not in ('True', 'False'):
            raise TypeError, \
                  u"%s must be a boolean type " \
                  "for BooleanField compatibility" % str(value)

class PhoneNumberField(CharField):
    format = "(00) 0000-0000"
    regex_format = None

    def __init__(self, *args, **kw):
        format = kw.pop('format', None)

        if not isinstance(format, basestring):
            raise TypeError, u"format param must be a string" \
                  " got a %r (%r)" % \
                  (type(format), format)

        if kw.has_key('max_length'):
            kw['max_length'] = kw.get('max_length')
        else:
            kw['max_length'] = len(format)

        self.format = format

        rfmt = re.escape(format).replace("0", r"\d")
        self.regex_format = r"(%s)" % rfmt

        super(PhoneNumberField, self).__init__(*args, **kw)

    def validate(self, value):
        if not isinstance(value, basestring):
            raise TypeError, \
                  u"%s must be a string(ish) type " \
                  "for PhoneNumberField compatibility" % value

        regex = re.compile(self.regex_format)
        if not regex.search(value):
            raise FieldValidationError, "The given value doesn't match " \
                  "'%s'. Got %s" % (self.format, value)

class TextField(Field):
    vartype = unicode

    def validate(self, value):
        if not isinstance(value, basestring):
            raise TypeError, \
                  u"%s must be a string for TextField compatibility" % repr(value)

class URLField(CharField):
    vartype = unicode

    def __init__(self, *args, **kw):
        verify_exists = kw.pop('verify_exists', True)

        # an object for checking url, for TDD reasons :)
        self.url_checker = kw.pop('url_checker', URLChecker())

        if not isinstance(verify_exists, bool):
            raise TypeError, u"%s.verify_exists param must be a bool" \
                  " (True or False), got %r (%r)" % \
                  (self.__class__.__name__,
                   type(verify_exists), verify_exists)

        if kw.has_key('max_length'):
            kw['max_length'] = kw.get('max_length')
        else:
            kw['max_length'] = 255

        self.verify_exists = verify_exists

        super(URLField, self).__init__(*args, **kw)

    def validate(self, value):
        if not isinstance(value, basestring):
            raise TypeError, \
                  u"%s must be a string(ish) type " \
                  "for URLField compatibility" % value

        self.url_checker.set_url(value)

        url_status = self.url_checker

        if not url_status.is_valid():
            raise FieldValidationError, 'The url is not valid: "%s"'% value

        if self.verify_exists and not url_status.does_exists():
            raise FieldValidationError, 'The url does not exist: "%s"'% value

class RelationShip(object):
    from_model = None
    to_model = None
    is_lazy = False
    is_self_referenced = False

    def set_model_object(self, model):

        if isinstance(model, basestring):
            self.set_lazy(True)
            # ok, it is a string, so I got to look for it in the
            # registry
            if "." in model:
                items = model.split(".")
                dots = len(items)
                if dots == 2:
                    # got the app_label
                    app_label, classname = items
                    model = ModelRegistry.get_model(app_label, classname)
                else: # more than 2 dots
                    # got the module name
                    modulename = ".".join(items[:-1])
                    classname = items[-1]
                    model = [m for m in \
                             ModelRegistry.get_all(by_module=modulename) \
                             if m.__name__ == classname][0]

            elif model == 'self':
                self.set_self_referenced(True)

        if not self.is_lazy and not hasattr(model, '__dead_parrot__'):
            raise TypeError, "%r is not a valid model" % model

        self.model = model
        if not self.is_lazy:
            self.set_to_model(model)

    def resolve(self):
        raise NotImplementedError

    def set_lazy(self, lazy):
        err = '%s.set_lazy takes a boolean as parameter, got %r'
        if not isinstance(lazy, bool):
            raise TypeError(err % (self.__class__.__name__, lazy))

        self.is_lazy = lazy

    def set_self_referenced(self, self_referenced):
        err = '%s.set_self_referenced takes a boolean as parameter, got %r'
        if not isinstance(self_referenced, bool):
            raise TypeError(err % (self.__class__.__name__, self_referenced))

        self.is_self_referenced = self_referenced

    def set_from_model(self, from_model):
        err = '%s.set_from_model takes a deadparrot.models.Model ' \
              'subclass as parameter, got %r'
        if not hasattr(from_model, '__dead_parrot__'):
            raise TypeError(err % (self.__class__.__name__, from_model))

        self.from_model = from_model

    def set_to_model(self, to_model):
        err = '%s.set_to_model takes a deadparrot.models.Model ' \
              'subclass as parameter, got %r'
        if not hasattr(to_model, '__dead_parrot__'):
            raise TypeError(err % (self.__class__.__name__, to_model))

        self.to_model = to_model

    def serialize(self, val):
        if isinstance(val, list):
            return [v.to_dict() for v in val]
        else:
            return val.to_dict()

    def resolve(self):
        model_list = ModelRegistry.get_all(by_class=self.model)
        if model_list:
            self.model = model_list[0]
        else:
            err = 'The model %r does not exist or is ' \
                  'not registered, did you import it ?'
            raise AttributeError(err % self.model)

        self.set_to_model(self.model)
        self.set_lazy(False)

class ForeignKey(RelationShip):
    def __init__(self, model):
        self.set_model_object(model)

class ManyToManyField(RelationShip):
    def __init__(self, model):
        self.set_model_object(model)

class OneToOneField(ForeignKey):
    pass
