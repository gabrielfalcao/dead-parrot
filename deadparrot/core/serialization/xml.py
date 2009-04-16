#!/usr/bin/env python
# -*- coding: utf-8; -*-
from lxml import etree

class XMLSerializer(object):
    def __init__(self, data):
        if not isinstance(data, (dict,)):
            raise TypeError, "XMLSerializer takes a" \
                  "dict as construction parameter"
        self.data = data

        rootname = data.keys()[0]
        self.root = etree.Element(rootname)

    def as_object(self):
        for k, v in self.data[self.root.tag].items():
            etree.SubElement(self.root, k).text = v

        return self.root

    def serialize(self):
        return etree.tostring(self.as_object())

    @classmethod
    def deserialize(cls, xml):
        xobject = etree.XML(xml)
        values = dict([(e.tag, e.text) for e in xobject.iterchildren()])
        name = xobject.tag
        return {name: values}

