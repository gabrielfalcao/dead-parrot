#!/usr/bin/env python
# -*- coding: utf-8; -*-

from lxml import etree
from datetime import datetime, date, time, timedelta
# dicionário para o registro de classes de tags
TAGS = {}

def path_join(base, *others):
    base = base.endswith("/") and base or "%s/" % base
    return "%s%s" % (base, "/".join(others))

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

    def serialize(self):
        return unicode(self.value)

    def fill(self, name, value):
        self.name = name
        self.value = value
        return self

    def __unicode__(self):
        return unicode(self.value or "")

    def __repr__(self):
        return "<%s%s:%s attribute object>" % (str(self.vartype.__name__.title()),
                                               self.__class__.__name__,
                                               self.name)

class DateTimeAttribute(Attribute):
    def serialize(self):
        return unicode(self.value.strftime(self.vartype))

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


class XmlTagText(Attribute):
    u"""Placeholder for the content of tags"""
    def __init__(self, value=None):
        super(XmlTagText, self).__init__(unicode, "_text_", value)

FIELD_CLASSES = [Attribute]

def build_metadata(klass, klass_meta=None):
    if not isinstance(klass, object):
        raise TypeError, "%r must be a new-style-class" % klass

    single_name = klass.__name__
    plural_name = "%ss" % single_name
    if not klass_meta:
        klass_meta =  type('Meta', tuple(), {'single_name': single_name,
                                             'plural_name': plural_name})

    if not hasattr(klass_meta, 'single_name'):
        klass_meta.single_name = single_name

    if not hasattr(klass_meta, 'plural_name'):
        klass_meta.single_name = plural_name

    return klass_meta()

class ModelMeta(type):
    def __init__(cls, name, bases, attrs):
        if name not in ('ModelMeta', 'Model'):
            cls._meta = build_metadata(cls, hasattr(cls, 'Meta') and cls.Meta or None)
            cls._fields =  dict([(k, v) for k, v in attrs.items() if isinstance(v, Attribute)])
            cls._data = {}
            for k, v in cls._fields.items():
                v.name = k
                setattr(cls, k, v)

        super(ModelMeta, cls).__init__(name, bases, attrs)

class ModelSet(object):
    set = []
    model_klass = None
    def __init__(self, model_klass, items):
        if not isinstance(items, (list, tuple)):
            klassname = self.__class__.__name__
            raise TypeError, "%s needs a list or "\
                  "tuple of %s objects. Got a %r" % (klassname,
                                                     klassname[:-3],
                                                     type(items))
        self.model_klass = model_klass
        self.set = list(items)

    def __getslice__(self, *args, **kw):
        return self.set.__getslice__(*args, **kw)

    def __setslice__(self, *args, **kw):
        return self.set.__setslice__(*args, **kw)

    def __getitem__(self, *args, **kw):
        return self.set.__getitem__(*args, **kw)

    def __setitem__(self, *args, **kw):
        return self.set.__setitem__(*args, **kw)

    def __len__(self):
        return len(self.set)

    def __nonzero__(self):
        return len(self.set) > 0

    def to_dict(self):
        return {self.model_klass._meta.plural_name: [m.to_dict() for m in self.set]}

class Model(object):
    __metaclass__ = ModelMeta

    def _get_data(self):
        return dict([(k, v.__class__(v.vartype, k, getattr(self, k)).serialize()) for k, v in self._fields.items()])

    def to_dict(self):
        return {self._meta.single_name: self._get_data()}

    @classmethod
    def Set(cls, items):
        return type('%sSet' % cls.__name__, (ModelSet,), {})(cls, items)
