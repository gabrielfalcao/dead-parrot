#!/usr/bin/env python
# -*- coding: utf-8; -*-
from lxml import etree
from lxml.etree import XMLSyntaxError

from base import Serializer

class XMLSerializer(Serializer):
    format = "xml"
    def __init__(self, data):
        if not isinstance(data, (dict,)):
            raise TypeError, "XMLSerializer takes a" \
                  "dict as construction parameter"
        self.data = data

        rootname = data.keys()[0]
        self.root = etree.Element(rootname)

    def as_object(self):
        child = self.data[self.root.tag]

        if isinstance(child, dict):
            for k, v in child.items():
                if v is None:
                    v = ""

                if isinstance(v, dict):
                    va = self.__class__({k:v}).serialize()
                    value = etree.fromstring(va)
                    elem = etree.SubElement(self.root, k)
                    self.root.replace(elem, value)
                else:
                    etree.SubElement(self.root, k).text = unicode(v)

        elif isinstance(child, list):
            for obj in child:
                node = self.__class__(obj).as_object()
                self.root.append(node)
        else:
            raise TypeError, "XMLSerializer can handle only list and dict " \
                  "got %r" % type(child)

        return self.root

    def serialize(self):
        return etree.tostring(self.as_object())

    @classmethod
    def deserialize(cls, xml):
        xobject = etree.XML(xml)
        # I will now determine if i'm deserializing
        # a set of objects or a object
        try:
            is_object = bool(xobject[0].text.strip())
        except IndexError, e:
            return xml

        if is_object:
            # I'm deserializing a object
            values = {}
            for e in xobject.iterchildren():
                if not e.text.strip():
                    values[e.tag] = cls.deserialize(etree.tostring([x for x in e.iterchildren()][0]))
                else:
                    values[e.tag] = e.text

        else:
            # I'm deserializing a set of objects
            xml_list = [etree.tostring(x) for x in xobject.iterchildren()]
            values = [cls.deserialize(o) for o in xml_list]

        return {xobject.tag: values}
