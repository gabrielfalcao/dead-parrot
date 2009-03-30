#!/usr/bin/env python
# -*- coding: utf-8; -*-
from attributes import Attribute
from fields import *

def build_metadata(klass, params):
    single_name = klass.__name__
    plural_name = "%ss" % single_name
    klass_meta =  type('Meta', tuple(), params)

    if not params.has_key('single_name'):
        klass_meta.single_name = single_name

    if not params.has_key('plural_name'):
        klass_meta.plural_name = plural_name

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
            if not metadata_params.has_key("validate_none"):
                metadata_params['validate_none'] = False

            cls._meta = build_metadata(cls, metadata_params)
            cls._data = {}
            for k, v in fields.items():
                cls._data[k] = v
                setattr(cls, k, None)

        super(ModelMeta, cls).__init__(name, bases, attrs)

class Model(object):
    __metaclass__ = ModelMeta

    def _get_data(self):
        return dict([(k, self._meta._fields[k].serialize(v)) for k, v in self._data.items()])

    def to_dict(self):
        return {self._meta.single_name: self._get_data()}

    def __setattr__(self, attr, val):
        if attr in self._data.keys():
            klassname = self.__class__.__name__
            field =self._meta._fields[attr]
            if not self._meta.validate_none:
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
    def Set(cls, items=None):
        klass = type('%sSet' % cls.__name__, (ModelSet,), {'model_klass': cls})
        return items and klass(items) or klass
