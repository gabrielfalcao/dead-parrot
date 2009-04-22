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

from deadparrot.serialization import Registry
from deadparrot.models.attributes import Attribute
from deadparrot.models.managers import *
from deadparrot.models.fields import *

VALIDATE_NONE = "The model won't validate any fields"
VALIDATE_ALL = """
    The model will validate all fields, unless
    those which have the validate parameter set
    to False
"""

# the global registry, by module, app_label and classes
_REGISTRY = {}
# the module-based registry: module -> classes
_MODULE_REGISTRY = {}
# the app_label-based registry: app_label -> classes
_APP_REGISTRY = {}

def build_metadata(klass, params):
    verbose_name = klass.__name__
    verbose_name_plural = "%ss" % verbose_name
    klass_meta =  type('Meta', tuple(), params)

    module_name = klass.__module__
    if "." in module_name:
        module_name = module_name.split(".")[-1]

    klass_meta.app_label = module_name

    if not params.has_key('verbose_name'):
        klass_meta.verbose_name = verbose_name

    if not params.has_key('verbose_name_plural'):
        klass_meta.verbose_name_plural = verbose_name_plural

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
            # handling fields
            fields =  dict([(k, v) for k, v in attrs.items() \
                            if isinstance(v, Field)])
            metadata_params = hasattr(cls, 'Meta') and \
                              vars(cls.Meta) or {}
            metadata_params['_fields'] = fields

            cls._meta = build_metadata(cls, metadata_params)
            cls._data = {}
            for k, v in fields.items():
                cls._data[k] = v
                setattr(cls, k, None)

            # registering the class in my dicts
            if not _APP_REGISTRY.get(cls._meta.app_label):
                _APP_REGISTRY[cls._meta.app_label] = {}
            _APP_REGISTRY[cls._meta.app_label][cls.__name__] = cls
            if not _MODULE_REGISTRY.get(cls.__module__):
                _MODULE_REGISTRY[cls.__module__] = {}
            _MODULE_REGISTRY[cls.__module__][cls.__name__] = cls

            if not _REGISTRY.get(cls.__module__):
                _REGISTRY[cls.__module__] = {}

            if not _REGISTRY[cls.__module__].get(cls._meta.app_label):
                _REGISTRY[cls.__module__][cls._meta.app_label] = {}

            gdict = _REGISTRY[cls.__module__][cls._meta.app_label]
            gdict[cls.__name__] = cls

            # handling managers
            manager_classes = dict([(k, v) for k, v in attrs.items() \
                                    if isinstance(v, tuple) and \
                                    len(v) == 3 and \
                                    issubclass(v[0], ModelManagerBuilder)])
            for k, manager_tup in manager_classes.items():
                manager_klass, args, kw = manager_tup
                setattr(cls, k, manager_klass(model=cls, *args, **kw))

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

    def __getitem__(self, *a, **kw):
        return self.items.__getitem__(*a, **kw)
    def __setitem__(self, *a, **kw):
        return self.items.__setitem__(*a, **kw)
    def __getslice__(self, *a, **kw):
        return self.items.__getslice__(*a, **kw)
    def __setslice__(self, *a, **kw):
        return self.items.__setslice__(*a, **kw)
    def __nonzero__(self):
        return bool(self.items)
    def __len__(self):
        return len(self.items)

    def to_dict(self):
        dicts = [m.to_dict() for m in self.items]
        ret = {self.__model_class__._meta.verbose_name_plural.title(): dicts}
        return ret

    @classmethod
    def from_dict(cls, edict):
        if not isinstance(edict, dict):
            raise TypeError, "%s.from_dict takes a dict as parameter. " \
                  "Got %r" % (cls.__name__, type(edict))

        items = edict[cls.__model_class__._meta.verbose_name_plural]
        return cls(*[cls.__model_class__.from_dict(i) for i in items])

    def serialize(self, to):
        serializer = Registry.get(to)
        return serializer(self.to_dict()).serialize()

    @classmethod
    def deserialize(cls, data, format):
        serializer = Registry.get(format)
        my_dict = serializer.deserialize(data)
        return cls.from_dict(my_dict)

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
        return {self._meta.verbose_name: self._get_data()}

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
                  "Got %r:%r" % (cls.__name__,
                                 type(data_dict),
                                 data_dict)
        try:
            d = data_dict[cls._meta.verbose_name].copy()
        except KeyError, e:
            raise TypeError, "%s.from_dict got an mismatched dict structure." \
                  "Expected {'%s': {... data ...}} like structure, got %s" % (cls,
                                                                              cls._meta.verbose_name,
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

    def serialize(self, to):
        serializer = Registry.get(to)
        return serializer(self.to_dict()).serialize()

    @classmethod
    def deserialize(cls, data, format):
        serializer = Registry.get(format)
        my_dict = serializer.deserialize(data)
        return cls.from_dict(my_dict)

class ModelRegistry(object):
    @classmethod
    def get_all(cls, by_class=None, by_module=None, by_app_label=None):
        if by_class:
            if not isinstance(by_class, basestring):
                raise TypeError, "ModelRegistry.get_all "\
                      "by_class parameter takes a string "\
                      "as parameter, got %r" % by_class
            ret = []
            for module, app_dict in _REGISTRY.items():
                for app_label, classdict in app_dict.items():
                    for classname, klass in classdict.items():
                        if classname == by_class:
                            ret.append(klass)

            return tuple(ret)

        if by_module:
            if not isinstance(by_module, basestring):
                raise TypeError, "ModelRegistry.get_all "\
                      "by_module parameter takes a string "\
                      "as parameter, got %r" % by_module
            ret = []
            for modname, classdict in _MODULE_REGISTRY.items():
                if modname == by_module:
                    ret.extend(classdict.values())
            return ret

        if by_app_label:
            if not isinstance(by_app_label, basestring):
                raise TypeError, "ModelRegistry.get_all "\
                      "by_app_label parameter takes a string "\
                      "as parameter, got %r" % by_app_label

            ret = []
            for modname, classdict in _APP_REGISTRY.items():

                if modname == by_app_label:
                    ret.extend(classdict.values())
            return ret

    @classmethod
    def get_model(cls, app_label, classname):
        if not isinstance(app_label, basestring):
            raise TypeError, "ModelRegistry.get_model takes the parameter" \
                  "app_label as string. Got %r" % app_label

        if not isinstance(classname, basestring):
            raise TypeError, "ModelRegistry.get_model takes the parameter" \
                  "classname as string. Got %r" % classname

        classdict = _APP_REGISTRY.get(app_label)
        if not classdict:
            raise AttributeError, "The app_label %s is not "\
                  "within Dead Parrot's registry." \
                " Are you sure you've imported it ?" % app_label

        return classdict.get(classname)
