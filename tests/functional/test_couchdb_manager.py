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
from nose.tools import assert_equals
from deadparrot import models
from utils import ignore_it
from couchdb import Server

def setup():
    try:
        global svr
        svr  = Server('http://localhost:5984/')
        del svr['dead_parrot']
    except: pass

def test_couchdb_manager_create():
    class FooBarSerial(models.Model):
        name = models.CharField(max_length=100)
        age = models.IntegerField()
        objects = models.CouchDBModelManager(base_uri='http://localhost:5984/')
        def __unicode__(self):
            return u'<FooBarSerial(name=%r)>' % self.name

    expected = FooBarSerial(name='foo bar', age=7)
    got = FooBarSerial.objects.create(name='foo bar', age=7)

    assert expected == got, 'Expected %r, got %r' % (expected, got)

def test_model_couchdb_manager_create_many():
    class WeeWooSerial(models.Model):
        name = models.CharField(max_length=100)
        age = models.IntegerField()
        objects = models.CouchDBModelManager(base_uri='http://localhost:5984/')
        def __unicode__(self):
            return u'<WeeWooSerial(name=%r)>' % self.name

    f1 = WeeWooSerial.objects.create(name='foo one', age=40)
    f2 = WeeWooSerial.objects.create(name='foo two', age=41)
    f3 = WeeWooSerial.objects.create(name='foo three', age=42)

    assert len(svr['dead_parrot']) == 3

test_model_couchdb_manager_create_many.setup = setup


def test_model_couchdb_manager_all():
    class SaaaSerial(models.Model):
        name = models.CharField(max_length=100)
        age = models.IntegerField()
        objects = models.CouchDBModelManager(base_uri='http://localhost:5984/')
        def __unicode__(self):
            return u'<SaaaSerial(name=%r,age=%s)>' % (self.name, self.age)

    w1 = SaaaSerial.objects.create(name='name1', age=10)
    w2 = SaaaSerial.objects.create(name='name2', age=20)
    w3 = SaaaSerial.objects.create(name='name3', age=10)
    w4 = SaaaSerial.objects.create(name='name4', age=10)
    w5 = SaaaSerial.objects.create(name='name5', age=50)

    expected = SaaaSerial.Set()(w1, w2, w3, w4, w5)
    got = SaaaSerial.objects.all()

    assert len(expected) == len(got)
    for item in expected: assert item in got

test_model_couchdb_manager_all.setup = setup

def test_model_couchdb_manager_all_get_only_current_model_documents():
    class SaaaSerial(models.Model):
        name = models.CharField(max_length=100)
        age = models.IntegerField()
        objects = models.CouchDBModelManager(base_uri='http://localhost:5984/')
        def __unicode__(self):
            return u'<SaaaSerial(name=%r,age=%s)>' % (self.name, self.age)

    class InnerSerial (models.Model):
        name = models.CharField(max_length=100)
        age = models.IntegerField()
        objects = models.CouchDBModelManager(base_uri='http://localhost:5984/')
        def __unicode__(self):
            return u'<InnerSerial(name=%r,age=%s)>' % (self.name, self.age)

    w1 = SaaaSerial.objects.create(name='name1', age=10)
    w2 = SaaaSerial.objects.create(name='name2', age=20)
    w3 = SaaaSerial.objects.create(name='name3', age=10)
    w4 = SaaaSerial.objects.create(name='name4', age=10)
    w5 = InnerSerial.objects.create(name='name5', age=50)
    w6 = InnerSerial.objects.create(name='name6', age=55)

    expected_saaas = SaaaSerial.Set()(w1, w2, w3, w4)
    expected_inner = InnerSerial.Set()(w5, w6)
    got_saaas = SaaaSerial.objects.all()
    got_inner = InnerSerial.objects.all()
    expected_saaas_count = 4
    assert len(got_saaas) == expected_saaas_count, 'Expected %s items, got %s items' %(expected_saaas_count, len(got_saaas))

    expected_inner_count = 2
    assert len(got_inner) == expected_inner_count, 'Expected %s items, got %s items' %(expected_inner_count, len(got_inner))

    for item in expected_saaas: assert item in got_saaas
    for item in expected_inner: assert item in got_inner


test_model_couchdb_manager_all_get_only_current_model_documents.setup = setup

#def test_model_couchdb_manager_all_deals_with_inheritance():
#    class SaaaSerial(models.Model):
#        name = models.CharField(max_length=100)
#        age = models.IntegerField()
#        objects = models.CouchDBModelManager(base_uri='http://localhost:5984/')
#        def __unicode__(self):
#            return u'<SaaaSerial(name=%r,age=%s)>' % (self.name, self.age)

#    class InnerSerial (SaaaSerial):
#        objects = models.CouchDBModelManager(base_uri='http://localhost:5984/')
#        def __unicode__(self):
#            return u'<InnerSerial(name=%r,age=%s)>' % (self.name, self.age)

#    w1 = SaaaSerial.objects.create(name='name1', age=10)
#    w2 = SaaaSerial.objects.create(name='name2', age=20)
#    w3 = SaaaSerial.objects.create(name='name3', age=10)
#    w4 = SaaaSerial.objects.create(name='name4', age=10)
#    w5 = InnerSerial.objects.create(name='name5', age=50)
#    w6 = InnerSerial.objects.create(name='name6', age=55)

#    expected_saaas = SaaaSerial.Set()(w1, w2, w3, w4)
#    expected_inner = InnerSerial.Set()(w5, w6)
#    got_saaas = SaaaSerial.objects.all()
#    got_inner = InnerSerial.objects.all()
#    expected_saaas_count = 4
#    assert len(got_saaas) == expected_saaas_count, 'Expected %s items, got %s items' %(expected_saaas_count, len(got_saaas))

#    expected_inner_count = 2
#    assert len(got_inner) == expected_inner_count, 'Expected %s items, got %s items' %(expected_inner_count, len(got_inner))

#    for item in expected_saaas: assert item in got_saaas
#    for item in expected_inner: assert item in got_inner


#test_model_couchdb_manager_all_deals_with_inheritance.setup = setup
