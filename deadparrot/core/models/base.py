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

import simplejson

from attributes import Attribute
from fields import *

VALIDATE_NONE = "The model won't validate any fields"
VALIDATE_ALL = """
    The model will validate all fields, unless
    those which have the validate parameter set
    to False
"""

def build_metadata(klass, params):
    single_name = klass.__name__
    plural_name = "%ss" % single_name
    klass_meta =  type('Meta', tuple(), params)

    if not params.has_key('single_name'):
        klass_meta.single_name = single_name

    if not params.has_key('plural_name'):
        klass_meta.plural_name = plural_name

    if not params.has_key('fields_validation_policy'):
        klass_meta.fields_validation_policy = VALIDATE_ALL

    metaobj = klass_meta()
    if hasattr(metaobj, '_fields'):
        for k, v in metaobj._fields.items():
            v.name = k

    return metaobj

class ModelMeta(type):
    def __init__(cls, name, bases, attrs):
        if name not in ('ModelMeta', 'Model'):
            fields =  dict([(k, v) for k, v in attrs.items() if isinstance(v, Field)])
            metadata_params = hasattr(cls, 'Meta') and vars(cls.Meta) or {}
            metadata_params['_fields'] = fields

            cls._meta = build_metadata(cls, metadata_params)
            cls._data = {}
            for k, v in fields.items():
                cls._data[k] = v
                setattr(cls, k, None)

        super(ModelMeta, cls).__init__(name, bases, attrs)

class ModelSet(object):
    __model_class__ = None
    def __init__(self, *items):
        for i in items:
            if not isinstance(i, self.__model_class__):
                raise TypeError, \
                      "%s can only handle %s types, got %r" % \
                      (self.__class__.__name__,
                       self.__model_class__.__name__,
                       type(i))
        self.items = items

    def to_dict(self):
        dicts = [m.to_dict() for m in self.items]
        ret = {self.__model_class__._meta.plural_name.title(): dicts}
        return ret

    @classmethod
    def from_dict(cls, edict):
        if not isinstance(edict, dict):
            raise TypeError, "%s.from_dict takes a dict as parameter. " \
                  "Got %r" % (cls.__name__, type(edict))

        items = edict[cls.__model_class__._meta.plural_name]
        return cls(*[cls.__model_class__.from_dict(i) for i in items])

class Model(object):
    __metaclass__ = ModelMeta

    def __init__(self, **kw):
        for k, v in kw.items():
            if k not in self._meta._fields.keys():
                raise AttributeError, \
            "%s has no attribute %s" % (self.__class__.__name__, k)
            setattr(self, k, v)

    def _get_data(self):
        return dict([(k, self._meta._fields[k].serialize(getattr(self, k))) for k in self._data.keys()])

    def to_dict(self):
        return {self._meta.single_name: self._get_data()}

    def __setattr__(self, attr, val):
        if attr in self._data.keys():
            klassname = self.__class__.__name__
            field =self._meta._fields[attr]
            if self._meta.fields_validation_policy != VALIDATE_NONE:
                # raising the field-specific exceptions
                field.validate(val)

            val = field.convert_type(val)
            self._data[attr] = val
        super(Model, self).__setattr__(attr, val)

    @classmethod
    def from_dict(cls, data_dict):
        if not isinstance(data_dict, dict):
            raise TypeError, "%s.from_dict takes a dict as parameter. " \
                  "Got %r" % (cls.__name__, type(data_dict))
        try:
            d = data_dict[cls._meta.single_name].copy()
        except KeyError, e:
            raise TypeError, "%s.from_dict got an mismatched dict structure." \
                  "Expected {'%s': {... data ...}} like structure, got %s" % (cls,
                                                                              cls._meta.single_name,
                                                                              unicode(data_dict))
        keys = cls._meta._fields.keys()
        obj = cls()
        for k, v in d.items():
            if k in keys:
                setattr(obj, k, v)

        return obj

    @classmethod
    def Set(cls):
        klass = type('%sSet' % cls.__name__, (ModelSet, ), {'__model_class__': cls })
        return klass
