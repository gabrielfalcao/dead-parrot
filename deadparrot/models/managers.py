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

from couchdb import Server

__all__ = ['ModelManager', 'FileSystemModelManager','CouchDBModelManager']

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

class CouchDBManager (ObjectsManager):
    __db_name = 'dead_parrot'

    def __setup__(self, base_uri, db_name=None):
        self.__svr = Server(base_uri)
        if db_name is not None:
            self.__db_name = db_name

        self.__db = self.get_or_create_db()

    @property
    def model_name(self):
        return unicode(self.model._meta.verbose_name)

    def get_or_create_db(self):
        if self.__db_name not in self.__svr['_all_dbs'].info():
            return self.__svr.create(self.__db_name)
        return self.__svr[self.__db_name]

    def create(self, **kw):

        ModelSetClass = self.model.Set()
        model = self.model(**kw)
        modelset = ModelSetClass()
        document = dict()
        document['type'] = self.model_name
        document['body'] = model.to_dict()
        self.__db.create(document)

        modelset.add(model)

        return model

    def all(self):
        ModelSetClass = self.model.Set()
        all_docs_function = "function(doc) { if (doc.type == '%s') emit(doc._id, doc.body); }" % self.model_name
        view = self.__db.query(all_docs_function)
        modelset = ModelSetClass()

        if view.total_rows > 0:
            for row in view.rows:
                modelset.add(self.model.from_dict(row.value))
        return modelset

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
        ModelSetClass = self.model.Set()

        model = self.model(**kw)
        if not os.path.exists(self._fullpath):
            f = codecs.open(self._fullpath, 'w', 'utf-8')
            f.write('')
            f.close()

        fobj = codecs.open(self._fullpath, 'r', 'utf-8')
        json = fobj.read()
        fobj.close()

        try:
            modelset = ModelSetClass.deserialize(json, 'json')
        except ValueError:
            modelset = ModelSetClass()

        modelset.add(model)

        fobj = codecs.open(self._fullpath, 'w', 'utf-8')
        fobj.write(modelset.serialize('json'))
        fobj.close()

        return model

    def filter(self, **params):
        for key in params.keys():
            if not key in self.model._meta._fields.keys():
                raise TypeError('%s is not a valid field in %r' % (key, self.model))

        modelset = self.all()
        removed = []
        for obj in modelset:
            for k, v in params.items():
                if getattr(obj, k) != v:
                    if obj not in removed:
                        modelset.remove(obj)
                        removed.append(obj)

        return modelset

    def all(self):
        ModelSetClass = self.model.Set()
        if not os.path.exists(self._fullpath):
            return ModelSetClass()

        fobj = codecs.open(self._fullpath, 'r', 'utf-8')
        json = fobj.read()
        fobj.close()

        try:
            modelset = ModelSetClass.deserialize(json, 'json')
        except ValueError:
            modelset = ModelSetClass()

        return modelset

    def get(self, **params):
        for key in params.keys():
            if not key in self.model._meta._fields.keys():
                raise TypeError('%s is not a valid field in %r' % (key, self.model))

        modelset = self.all()
        removed = []
        for obj in modelset:
            for k, v in params.items():
                if getattr(obj, k) != v:
                    if obj not in removed:
                        modelset.remove(obj)
                        removed.append(obj)

        return modelset and modelset[0] or None

    def delete(self, obj):
        if not isinstance(obj, self.model):
            raise TypeError('delete() takes a %s as parameter, got %r' % (self.model.__name__, obj))

        modelset = self.all()
        newset = self.model.Set()()

        for model in modelset:
            if model.to_dict() != obj.to_dict():
                newset.add(model)

        f = codecs.open(self._fullpath, 'w', 'utf-8')
        f.write(newset.serialize('json'))
        f.close()

class FileSystemModelManager(ModelManager):
    manager = FileObjectsManager

class CouchDBModelManager (ModelManager):
    manager = CouchDBManager


