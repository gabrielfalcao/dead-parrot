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

from sqlalchemy.orm import sessionmaker, mapper

from sqlalchemy import String, MetaData, ForeignKey, Unicode, UnicodeText
from sqlalchemy import Table, Column, Integer, DateTime, Date, Time, Float
from sqlalchemy import create_engine, Boolean, Numeric

from deadparrot.models.fields import *
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)

"""
>>> metadata = MetaData()
>>> users_table = Table('users', metadata,
...     Column('id', Integer, primary_key=True),
...     Column('name', String),
...     Column('fullname', String),
...     Column('password', String)
... )
"""

class ModelManager(object):
    pass

class ModelManagerBuilder(object):
    pass

class SQLAlchemyManagerBuilderBase(ModelManagerBuilder):
    def __init__(self, model,
                 create_schema=False,
                 session=Session()):
        self.model = model
        fields = []
        has_pk = False
        for n, f in model._meta._fields.items():
            if f.primary_key:
                has_pk = True
            fields.append(self._parrot_field_to_alchemy_column(n, f))

        if not has_pk:
            raise AttributeError, \
                  "The model %s does not have " \
                  "any primary keys, which is required by SQLAlchemy"

        self.metadata = MetaData()
        self.session = session
        self.table = Table(model.__name__.lower(), self.metadata, *fields)
        if create_schema:
            self.metadata.create_all(session.bind)

        self.mapper = mapper(self.model, self.table)
        self._monkey_patch_model(self.model)

    def _monkey_patch_model(self, model):
        model._sqlalchemy_manager = self
        def delete_model(this, commit=True):
            this._sqlalchemy_manager.session.delete(this)
            if commit:
                this._sqlalchemy_manager.session.commit()
        model.delete = delete_model
        return model

    @property
    def _query(self):
        return self.session.query(self.model)

    def _model_set(self, *args, **kw):
        Set = self.model.Set()
        return Set(*args, **kw)

    def _parrot_field_to_alchemy_column(self, name, field):
        if isinstance(field, (CharField,
                              URLField,
                              EmailField,
                              PhoneNumberField)):
            return Column(name, Unicode(field.max_length),
                          primary_key=field.primary_key)
        elif isinstance(field, DecimalField):
            return Column(name, Numeric,
                          primary_key=field.primary_key)
        elif isinstance(field, IntegerField):
            return Column(name, Integer,
                          primary_key=field.primary_key)
        elif isinstance(field, FloatField):
            return Column(name, Float,
                          primary_key=field.primary_key)
        elif isinstance(field, TextField):
            return Column(name, UnicodeText,
                          primary_key=field.primary_key)
        elif isinstance(field, DateTimeField):
            return Column(name, DateTime,
                          primary_key=field.primary_key)
        elif isinstance(field, (DateField, TimeField)):
            raise TypeError, \
                  "SQLAlchemy does not support datetime.date " \
                  "and datetime.time, use datetime.datetime " \
                  "instead. With deadparrot you must use " \
                  "deadparrot.models.DateTimeField to resolve " \
                  "this issue"

        elif isinstance(field, TimeField):
            return Column(name, Time,
                          primary_key=field.primary_key)
        elif isinstance(field, BooleanField):
            return Column(name, Boolean,
                          primary_key=field.primary_key)
        else:
            raise TypeError, \
                  "Unknown type of field: %r %r" % (type(field), field)

class SQLAlchemyManagerBuilder(SQLAlchemyManagerBuilderBase):
    def all(self):
        results = self._query.all()
        return self._model_set(*results)

    def create(self, *args, **kw):
        mobject = self.model(*args, **kw)
        self.session.add(mobject)
        self.session.commit()
        return mobject

    def filter(self, *args, **kw):
        results = self._query.filter(*args, **kw)
        return self._model_set(*results)

class SQLAlchemyManager(ModelManager):
    def __new__(cls, *args, **kw):
        return SQLAlchemyManagerBuilder, args, kw

