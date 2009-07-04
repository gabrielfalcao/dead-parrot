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
from deadparrot import models

def test_model_file_manager_create():
    class FooBarSerial(models.Model):
        name = models.CharField(max_length=100)
        objects = models.FileSystemModelManager(base_path=os.path.abspath('.'))
        def __unicode__(self):
            return u'<FooBarSerial(name=%r)>' % self.name

    expected = FooBarSerial(name='foo bar')
    got = FooBarSerial.objects.create(name='foo bar')

    assert expected == got, 'Expected %r, got %r' % (expected, got)
    os.remove(FooBarSerial.objects._fullpath)

def test_model_file_manager_create_many():
    class WeeWooSerial(models.Model):
        name = models.CharField(max_length=100)
        objects = models.FileSystemModelManager(base_path=os.path.abspath('.'))
        def __unicode__(self):
            return u'<WeeWooSerial(name=%r)>' % self.name

    f1 = WeeWooSerial.objects.create(name='foo one')
    f2 = WeeWooSerial.objects.create(name='foo two')
    f3 = WeeWooSerial.objects.create(name='foo three')

    expected = WeeWooSerial.Set()(f1, f2, f3)
    got = WeeWooSerial.Set().deserialize(open(WeeWooSerial.objects._fullpath).read(), 'json')
    assert expected == got, 'Expected %r, got %r' % (expected, got)
    os.remove(WeeWooSerial.objects._fullpath)

def test_model_file_manager_filter():
    class WonkaSerial(models.Model):
        name = models.CharField(max_length=100)
        age = models.IntegerField()
        objects = models.FileSystemModelManager(base_path=os.path.abspath('.'))
        def __unicode__(self):
            return u'<WonkaSerial(name=%r)>' % self.name

    w1 = WonkaSerial.objects.create(name='name1', age=10)
    w2 = WonkaSerial.objects.create(name='name2', age=20)
    w3 = WonkaSerial.objects.create(name='name3', age=10)
    w4 = WonkaSerial.objects.create(name='name4', age=10)
    w5 = WonkaSerial.objects.create(name='name5', age=50)

    expected = WonkaSerial.Set()(w1, w3, w4)
    got = WonkaSerial.objects.filter(age=10)
    assert expected == got, 'Expected %r, got %r' % (expected, got)
    os.remove(WonkaSerial.objects._fullpath)

def test_model_file_manager_all():
    class SaaaSerial(models.Model):
        name = models.CharField(max_length=100)
        age = models.IntegerField()
        objects = models.FileSystemModelManager(base_path=os.path.abspath('.'))
        def __unicode__(self):
            return u'<SaaaSerial(name=%r)>' % self.name

    w1 = SaaaSerial.objects.create(name='name1', age=10)
    w2 = SaaaSerial.objects.create(name='name2', age=20)
    w3 = SaaaSerial.objects.create(name='name3', age=10)
    w4 = SaaaSerial.objects.create(name='name4', age=10)
    w5 = SaaaSerial.objects.create(name='name5', age=50)

    expected = SaaaSerial.Set()(w1, w2, w3, w4, w5)
    got = SaaaSerial.objects.all()
    assert expected == got, 'Expected %r, got %r' % (expected, got)
    os.remove(SaaaSerial.objects._fullpath)

def test_model_file_manager_get():
    class XulSerial(models.Model):
        name = models.CharField(max_length=100)
        age = models.IntegerField()
        objects = models.FileSystemModelManager(base_path=os.path.abspath('.'))
        def __unicode__(self):
            return u'<XulSerial(name=%r)>' % self.name

    w1 = XulSerial.objects.create(name='name1', age=10)
    w2 = XulSerial.objects.create(name='name2', age=20)
    w3 = XulSerial.objects.create(name='name3', age=10)
    w4 = XulSerial.objects.create(name='name4', age=10)
    w5 = XulSerial.objects.create(name='name5', age=50)

    expected = w1
    got = XulSerial.objects.get(name='name1', age=10)
    assert expected == got, 'Expected %r, got %r' % (expected, got)
    os.remove(XulSerial.objects._fullpath)

def test_model_file_manager_delete():
    class ZoomSerial(models.Model):
        name = models.CharField(max_length=100)
        age = models.IntegerField()
        objects = models.FileSystemModelManager(base_path=os.path.abspath('.'))
        def __unicode__(self):
            return u'<ZoomSerial(name=%r)>' % self.name

    w1 = ZoomSerial.objects.create(name='woo', age=20)
    w2 = ZoomSerial.objects.create(name='wee', age=20)
    w3 = ZoomSerial.objects.create(name='wee', age=10)
    w4 = ZoomSerial.objects.create(name='woo', age=20)
    w5 = ZoomSerial.objects.create(name='woo', age=10)

    ZoomSerial.objects.delete(w5)
    expected = ZoomSerial.Set()(w1, w2, w3, w4)
    got = ZoomSerial.objects.all()
    assert expected == got, 'Expected %r, got %r' % (expected, got)
    os.remove(ZoomSerial.objects._fullpath)
