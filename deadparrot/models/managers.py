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
import os
import codecs

from deadparrot.models.fields import *
from os.path import join

class ObjectsManager(object):
    def __init__(self, model, *args, **kw):
        self.model = model
        self.__setup__(*args, **kw)

    def __setup__(self, *args, **kw):
        pass

class ModelManager(object):
    manager = ObjectsManager
    def __new__(cls, *args, **kw):
        return (cls.manager, args, kw)

class FileObjectsManager(ObjectsManager):
    def __setup__(self, base_path):
        if not isinstance(base_path, basestring):
            raise TypeError('FileSystemModelManager "base_path" parameter should be string, got %r' % base_path)

        if not os.path.exists(base_path):
            raise OSError('The path %s does not exist' % base_path)
        self.base_path = base_path

    @property
    def _filename(self):
        return "%s.json" % self.model.__name__

    @property
    def _fullpath(self):
        return join(self.base_path, self._filename)

    def create(self, **kw):
        model = self.model(**kw)

        fobj = codecs.open(self._fullpath, 'w+', 'utf-8')
        json = fobj.read() or self.model.Set()().serialize('json')

        modelset = self.model.Set().deserialize(json, 'json')

        modelset.add(model)

        fobj.write(modelset.serialize('json'))
        fobj.close()

        return model

class FileSystemModelManager(ModelManager):
    manager = FileObjectsManager
