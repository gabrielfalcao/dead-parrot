#!/usr/bin/env python
# -*- coding: utf-8; -*-

from lxml import etree
from datetime import datetime, timedelta
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
    value = None

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
            return self.vartype(val or 0)

        elif self.vartype in (str, unicode):
            return self.vartype(val or "")
        else:
            return self.vartype(val)

    def fill(self, name, value):
        self.name = name
        self.value = self.vartype(value)
        return self

    def __unicode__(self):
        return unicode(self.value or "")

    def __repr__(self):
        return unicode(self.value or "")

class DateTimeAttribute(Attribute):
    def convert_type(self, val):
        if val:
            return datetime.strptime(val, self.vartype)
        else:
            return datetime.now()

class XmlTagText(Attribute):
    u"""Placeholder for the content of tags"""
    def __init__(self, value=None):
        super(XmlTagText, self).__init__(unicode, "_text_", value)

class XmlTagSet(object):
    __evaluated__ = False
    __tag_class__ = None
    path = '/set/%s'
    set = None
    nodes = None
    subsets = None
    sdoc = None
    node = None

    @classmethod
    def from_xml(cls, xml):
        return cls(etree.XML(xml))

    def __init__(self, doc=None, lazy=False, path=""):
        classname = self.__class__.__name__.lower()[:-3]
        self.cls = self.__class__
        self.path = path or "/%s/%s" % (classname + "s", classname)
        self.sdoc = doc
        self.node = doc
        if not lazy:
            self.evaluate()

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

    def __repr__(self):
        basename = self.__class__.__name__
        second = self.__evaluated__ and 'total=%d' % len(self.set) or "evaluated=False"
        return "<%s.Set %s>" % (basename[:-3], second)

    def as_list(self):
        return list(self)

    def evaluate(self, document=None, is_subnode=False):
        if self.__evaluated__:
            return False

        self.nodes = self.sdoc.xpath(self.path)
        self.set = [self.klass.from_node(node) for node in self.nodes]
        self.__evaluated__ = True
        return True

    @property
    def klass(self):
        return self.__tag_class__

class XmlModelError(Exception):
    pass

class XmlTagMeta(type):
    def __init__(cls, name, bases, attrs):
        if name not in ('XmlTag', 'Midia'):
            TAGS[name] = cls
        super(XmlTagMeta, cls).__init__(name, bases, attrs)

class XmlTagLazy(object):
    __tag_class__ = None
    pk_field = None
    pk_value = None
    vartype = None

    def __init__(self, value):
        try:
            self.pk_value = self.vartype(value)
        except (ValueError, TypeError), e:
            if not value and self.vartype is int:
                self.pk_value = 0
            else:
                self.pk_value = value

    def __repr__(self):
        return "<%sLazy %s=%r>" % (self.__tag_class__.__name__,
                                   self.pk_field,
                                   self.pk_value)

class LazyConstructor(object):
    def __init__(self, lazyklass, tagklass):
        self.lazyklass = lazyklass
        self.tagklass = tagklass

    def __call__(self, data):
        return self.lazyklass(self.tagklass, data)

class TagGetter(object):
    class types:
        Lazy = "Lazy"
        Text = "Text"
        Set = "Set"
        NodeSet = "NodeSet"

    def __init__(self, tagname, tag_type=None, **params):
        self.tagname = tagname
        self.params = params

        if tag_type is not None and tag_type not in dir(TagGetter.types):
            raise TypeError("%s is an inexistent tag_type, choices are: %s" % (tag_type,
                                                                               ", ".join([x for x in dir(types) if not x.startswith("_")])))
        self.tag_type = tag_type

    def get(self):
        try:
            tag = TAGS[self.tagname]
            if self.tag_type:
                tag = getattr(tag, self.tag_type)(**self.params)

            return tag
        except KeyError:
            raise AttributeError("The tag %s does not exist\n" \
                                 "Tip: did you import the respective module ?" % self.tagname)

class XmlTag(object):
    __metaclass__ = XmlTagMeta
    _text_ = ""
    __nonzero = False
    subsets = None
    node = None

    def _set_text(self, value):
        self._text_ = unicode(value)

    def _get_text(self):
        return XmlTagText(self._text_ or (self.node is not None and self.node.text))
    text = property(_get_text, _set_text)

    def __init__(self, **kw):
        self.cls = self.__class__
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def __unicode__(self):
        return self.text

    def to_xml(self):
        return etree.tostring(self.node)

    @classmethod
    def from_xml(cls, xml):
        doc = etree.XML(xml)
        return cls.from_node(doc)

    @classmethod
    def from_node(klass, node):
        this = klass()
        if not isinstance(node, etree._Element):
            raise TypeError("Tag.fill_from_node needs" \
                            " a xml.dom.Element instance as argument, " \
                            "got %s" % (str(type(node))))

        this.fill_from_node(node)
        return this

    @classmethod
    def Lazy(cls, pk, of_type):
        return type("%sLazy" % cls.__name__,
                    (XmlTagLazy,),
                    {'__tag_class__': cls,
                     'pk_field': pk,
                     'vartype': of_type})

    @staticmethod
    def Text():
        return XmlTagText

    @classmethod
    def Set(cls):
        mset =  type("%sSet" % cls.__name__,
                     (XmlTagSet,),
                     {'__tag_class__': cls})
        return mset

    @classmethod
    def NodeSet(cls):
        mset = cls.Set()
        return mset()

    @property
    def set(self):
        mset = type("%sSet" % self.__class__.__name__,
                    (XmlTagSet,),
                    {'__tag_class__': self.__class__})
        return mset

    def _attributes_of_type(self, *typ):
        for name in dir(self):
            if not name.startswith("_"):
                attr = getattr(self, name)
                if isinstance(attr, tuple(typ)):
                    yield attr

    def _get_tag_getters(self, kind=None):
        """returns the object attributes that
        are a XmlTag"""
        for tgetter in self._attributes_of_type(TagGetter,):
            if tgetter.tag_type == kind:
                yield tgetter

    def _get_solid_tags(self):
        """returns the object attributes that
        are a XmlTag"""
        solid = list(self._attributes_of_type(XmlTag,))
        solid.extend([g.get() for g in self._get_tag_getters(kind=None)])
        return solid

    def __nonzero__(self):
        return self.__nonzero

    @property
    def __tagname__(self):
        return self.__class__.__name__.lower()

    def fill_from_node(self, node):
        if not isinstance(node, etree._Element):
            raise TypeError("Tag.fill_from_node needs" \
                            " a xml.dom.Element instance as argument, " \
                            "got %s" % (str(type(node))))

        if self.__tagname__ == node.tag:
            self.__nonzero = True

        self.node = node
        for name, attr in self.camel_attrs():
            setattr(self, name, attr.convert_type(node.get(name)))

        # filling the textual tags:
        # Example: <descricao></descricao>
        for xtag in self._get_solid_tags():
            tagname = xtag.__class__.__name__.lower()
            try:
                value = node.xpath(tagname)[0].text
            except IndexError:
                value = ""
            getattr(self, tagname).text = value
            setattr(self, tagname, value)

        # filling the pk value of lazy tags:
        for lname in dir(self):
            lattr = getattr(self, lname)

            # evaluating TagGetters
            if isinstance(lattr, TagGetter):
                lattr = lattr.get()

            # populating XmlTagTexts
            if lattr is XmlTagText:
                setattr(self, '_text_', node.text)
                self.__dict__[lname] = XmlTagText(node.text)

            # getting the tagsets
            if isinstance(lattr, type) and \
                   XmlTagSet in lattr.__bases__ and \
                   lattr.__tag_class__ != self.__class__ :
                ppath = "%s/%s" % (lname, lname[:-1])
                self.__dict__[lname] = lattr(node, path=ppath)

            # populating the Lazy tags
            if isinstance(lattr, type) and XmlTagLazy in lattr.__bases__:
                id_attribute_name = "%s_id" % lname
                value = node.get(id_attribute_name)
                self.__dict__[lname] = lattr(value)
                setattr(self, id_attribute_name, value)

        self.subsets = {}
        for tagname, tagclass in TAGS.items():
            if isinstance(self, tagclass):
                continue

            tagname = tagname.lower()
            self.subsets[tagname] = []
            for attrname in dir(self):
                if isinstance(getattr(self, attrname), XmlTagSet):
                    getattr(self, attrname).evaluate(node, is_subnode=True)
                    self.subsets[tagname].append(getattr(self, attrname))

    def camel_attrs(self):
        return [(name, attr) for name, attr in [(x, getattr(self, x)) for x in dir(self)] \
                if isinstance(attr, Attribute)]

class XMLSerializer(object):
    def __init__(self, obj):
        pass
