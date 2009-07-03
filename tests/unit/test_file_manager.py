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
import re
from pmock import *

from deadparrot.models.base import Model
from deadparrot.models.fields import CharField
from deadparrot.models import managers

from utils import assert_raises, FakeGetter
from nose import with_setup

def test_model_file_manager_class_exists():
    msg1 = 'deadparrot.models should have the class FileSystemManager'
    assert hasattr(managers, 'FileSystemModelManager'), msg1
    msg2 = 'deadparrot.managers.FileSystemManager should have the class FileSystemManager'
    assert issubclass(managers.FileSystemModelManager, managers.ModelManager), msg2

def test_model_file_manager_construction_without_basepath_raises():
    def make_class():
        class Parrot(Model):
            objects = managers.FileSystemModelManager()

    assert_raises(TypeError, make_class, exc_pattern='__setup__.. takes exactly 2 arguments .1 given.')

def test_model_file_manager_construction_with_basepath_nonstring_raises():
    def make_class_number():
        class Parrot(Model):
            objects = managers.FileSystemModelManager(base_path=10)

    def make_class_list():
        class Parrot(Model):
            objects = managers.FileSystemModelManager(base_path=[])

    assert_raises(TypeError, make_class_number, exc_pattern='FileSystemModelManager "base_path" parameter should be string, got %r' % 10)
    assert_raises(TypeError, make_class_list, exc_pattern='FileSystemModelManager "base_path" parameter should be string, got %s' % re.escape(repr([])))

def test_file_manager_checks_basepath_existence_raises():
    from deadparrot.models.base import Model
    from deadparrot.models import managers

    my_path = '/my/invalid/path'

    class os_mock:
        path = Mock()

    def make_class():
        class FooBarFSModel(Model):
            objects = managers.FileSystemModelManager(base_path=my_path)

    os_module = managers.os
    managers.os = os_mock

    os_mock.path.expects(once()).exists(eq(my_path)).will(return_value(False))

    assert_raises(OSError, make_class, exc_pattern=r'The path %s does not exist' % my_path)
    os_mock.path.verify()

    managers.os = os_module

def test_model_file_manager_gets_filename_based_on_model_name():
    from deadparrot.models.base import Model
    from deadparrot.models import managers

    path_mock = Mock()

    exists_func = managers.os.path.exists
    my_path = '/my/path'
    path_mock.expects(once()).exists(eq(my_path)).will(return_value(True))
    managers.os.path.exists = path_mock.exists

    class FooBarFSModelWee(Model):
        objects = managers.FileSystemModelManager(base_path=my_path)

    managers.os.path.exists = exists_func

    msg = 'FooBarFSModelWee.objects._filename should be FooBarFSModelWee.json, ' \
          'got %r' % FooBarFSModelWee.objects._filename

    assert FooBarFSModelWee.objects._filename == 'FooBarFSModelWee.json', msg
    path_mock.verify()

def test_model_file_manager_gets_fullpath_based_on_model_name_and_basepath():
    from deadparrot.models.base import Model
    from deadparrot.models import managers

    path_mock = Mock()

    exists_func = managers.os.path.exists
    my_path = '/my/path'
    path_mock.expects(once()).exists(eq(my_path)).will(return_value(True))
    managers.os.path.exists = path_mock.exists

    class FooBarFSModelWee(Model):
        objects = managers.FileSystemModelManager(base_path=my_path)

    managers.os.path.exists = exists_func

    msg = 'FooBarFSModelWee.objects._filename should be /my/path/FooBarFSModelWee.json, ' \
          'got %r' % FooBarFSModelWee.objects._filename

    assert FooBarFSModelWee.objects._fullpath == '/my/path/FooBarFSModelWee.json', msg
    path_mock.verify()


def test_model_file_manager_has_method_create():
    class os_mock:
        path = Mock()

    os_module = managers.os
    managers.os = os_mock
    managers.os.path.expects(once()).exists(eq('/home/wee')).will(return_value(True))

    class Wee(Model):
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    classname = Wee.objects.__class__.__name__
    assert hasattr(Wee.objects, 'create'), '%s should have the method "create"' % classname
    assert callable(Wee.objects.create), '%s.create should be callable' % classname
    managers.os = os_module

os_module = managers.os
def setup_fake_os():
    managers.os = FakeGetter()

def teardown_fake_os():
    managers.os = os_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_create_uses_codecs_utf8():
    codecs_mock = Mock()
    file_mock = Mock()

    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    class Wee(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    foobar = Wee(name='foo bar')
    expected_json = Wee.Set()(*[foobar]).serialize('json')
    codecs_mock.expects(once()).open(eq('/home/wee/Wee.json'),
                                     eq('a'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(Wee.Set()().serialize('json')))
    file_mock.expects(once()).write(eq(expected_json))
    file_mock.expects(once()).close()

    got = Wee.objects.create(name='foo bar')
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()
    managers.codecs = codecs_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_create_uses_codecs_utf8_works_with_empty_string():
    codecs_mock = Mock()
    file_mock = Mock()

    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    class Wee(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    foobar = Wee(name='foo bar')
    expected_json = Wee.Set()(*[foobar]).serialize('json')
    codecs_mock.expects(once()).open(eq('/home/wee/Wee.json'),
                                     eq('a'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(''))
    file_mock.expects(once()).write(eq(expected_json))
    file_mock.expects(once()).close()

    got = Wee.objects.create(name='foo bar')
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()
    managers.codecs = codecs_module
