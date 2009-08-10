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
from mox import Mox
from pmock import *

from deadparrot.models.base import Model
from deadparrot.models.fields import CharField
from deadparrot.models import managers

from utils import assert_raises, FakeGetter
from nose import with_setup

os_module = managers.os
def setup_fake_os():
    managers.os = FakeGetter()

def teardown_fake_os():
    managers.os = os_module

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

def test_model_file_manager_has_method_add():
    class os_mock:
        path = Mock()

    os_module = managers.os
    managers.os = os_mock
    managers.os.path.expects(once()).exists(eq('/home/wee')).will(return_value(True))

    class Wee(Model):
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    classname = Wee.objects.__class__.__name__
    assert hasattr(Wee.objects, 'add'), '%s should have the method "add"' % classname
    assert callable(Wee.objects.add), '%s.add should be callable' % classname
    managers.os = os_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_create_instantiate_object_and_add():
    mocker = Mox()
    class Chuah(Model):
        uuid = CharField(max_length=36)
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    Chuah.objects.add = mocker.CreateMockAnything()
    Chuah.objects.add(Chuah(uuid='aabbccdd'))
    mocker.ReplayAll()
    Chuah.objects.create(uuid='aabbccdd')
    mocker.VerifyAll()

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_add_uses_codecs_utf8():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/wee')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/wee/Wee.json')).will(return_value(False))
    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Wee(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    foobar = Wee(name='foo bar')
    expected_json = Wee.Set()(*[foobar]).serialize('json')

    codecs_mock.expects(once()).open(eq('/home/wee/Wee.json'),
                                     eq('w'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).write(eq(''))
    file_mock.expects(once()).close()

    codecs_mock.expects(once()).open(eq('/home/wee/Wee.json'),
                                     eq('r'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(Wee.Set()().serialize('json')))
    file_mock.expects(once()).close()

    codecs_mock.expects(once()).open(eq('/home/wee/Wee.json'),
                                     eq('w'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).write(eq(expected_json))
    file_mock.expects(once()).close()

    got = Wee.objects.add(Wee(name='foo bar'))
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_has_method_filter():
    class Wee(Model):
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    classname = Wee.objects.__class__.__name__
    assert hasattr(Wee.objects, 'filter'), '%s should have the method "filter"' % classname
    assert callable(Wee.objects.filter), '%s.filter should be callable' % classname

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_filter_raises_wrong_param():
    class Woo(Model):
        objects = managers.FileSystemModelManager(base_path='/home/woo')
        def __unicode__(self):
            return '<FooBar(name=%r)>' % self.name

    assert_raises(TypeError, Woo.objects.filter, blabla='x', exc_pattern=r'blabla is not a valid field in %r' % Woo)

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_filter_returns_empty_set_when_wrong_json_format():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/woo')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(True))
    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Woo(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/woo')
        def __unicode__(self):
            return '<FooBar(name=%r)>' % self.name

    foobar = Woo.Set()()

    read_json = '{[{fh3onc8c3:"""""]}]'

    codecs_mock.expects(once()).open(eq('/home/woo/Woo.json'),
                                     eq('r'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(read_json))
    file_mock.expects(once()).close()

    got = Woo.objects.filter(name='foo bar')
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_filter_when_file_exists():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/woo')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(True))
    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Woo(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/woo')
        def __unicode__(self):
            return '<FooBar(name=%r)>' % self.name

    foobar = Woo.Set()(Woo(name='foo bar'))

    read_set = Woo.Set()(Woo(name='foo bar'), Woo(name='john doe'))
    read_json = read_set.serialize('json')

    codecs_mock.expects(once()).open(eq('/home/woo/Woo.json'),
                                     eq('r'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(read_json))
    file_mock.expects(once()).close()

    got = Woo.objects.filter(name='foo bar')
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_filter_when_file_does_not_exist():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/woo')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(False))
    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Woo(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/woo')

    foobar = Woo.Set()()

    got = Woo.objects.filter(name='foo bar')
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_has_method_all():
    class Wee(Model):
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    classname = Wee.objects.__class__.__name__
    assert hasattr(Wee.objects, 'all'), '%s should have the method "all"' % classname
    assert callable(Wee.objects.all), '%s.all should be callable' % classname

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_all_when_file_exists():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/woo')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(True))
    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Woo(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/woo')
        def __unicode__(self):
            return '<FooBar(name=%r)>' % self.name

    read_set = Woo.Set()(Woo(name='foo bar'), Woo(name='john doe'))
    read_json = read_set.serialize('json')

    codecs_mock.expects(once()).open(eq('/home/woo/Woo.json'),
                                     eq('r'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(read_json))
    file_mock.expects(once()).close()

    got = Woo.objects.all()
    assert got == read_set, 'Expected %r, got %r' % (read_set, got)

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_all_returns_empty_set_when_wrong_json_format():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/woo')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(True))
    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Woo(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/woo')
        def __unicode__(self):
            return '<FooBar(name=%r)>' % self.name

    foobar = Woo.Set()()

    read_json = '{[{fh3onc8c3:"""""]}]'

    codecs_mock.expects(once()).open(eq('/home/woo/Woo.json'),
                                     eq('r'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(read_json))
    file_mock.expects(once()).close()

    got = Woo.objects.all()
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_all_when_file_does_not_exist():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/woo')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(False))
    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Woo(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/woo')

    foobar = Woo.Set()()

    got = Woo.objects.all()
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_has_method_get():
    class Wee(Model):
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    classname = Wee.objects.__class__.__name__
    assert hasattr(Wee.objects, 'get'), '%s should have the method "get"' % classname
    assert callable(Wee.objects.get), '%s.get should be callable' % classname

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_get_when_file_exists():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/woo')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(True))
    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Woo(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/woo')
        def __unicode__(self):
            return '<FooBar(name=%r)>' % self.name

    foobar = Woo(name='foo bar')

    read_set = Woo.Set()(Woo(name='foo bar'), Woo(name='john doe'))
    read_json = read_set.serialize('json')

    codecs_mock.expects(once()).open(eq('/home/woo/Woo.json'),
                                     eq('r'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(read_json))
    file_mock.expects(once()).close()

    got = Woo.objects.get(name='foo bar')
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_get_returns_empty_set_when_wrong_json_format():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/woo')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(True))
    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Woo(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/woo')
        def __unicode__(self):
            return '<FooBar(name=%r)>' % self.name

    foobar = None

    read_json = '{[{fh3onc8c3:"""""]}]'

    codecs_mock.expects(once()).open(eq('/home/woo/Woo.json'),
                                     eq('r'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(read_json))
    file_mock.expects(once()).close()

    got = Woo.objects.get(name='foo bar')
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_get_when_file_does_not_exist():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/woo')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(False))
    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Woo(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/woo')

    foobar = None

    got = Woo.objects.get(name='foo bar')
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_get_raises_wrong_param():
    class Woo(Model):
        objects = managers.FileSystemModelManager(base_path='/home/woo')
        def __unicode__(self):
            return '<FooBar(name=%r)>' % self.name

    assert_raises(TypeError, Woo.objects.get, blabla='x', exc_pattern=r'blabla is not a valid field in %r' % Woo)

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_has_method_delete():
    class Wee(Model):
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    classname = Wee.objects.__class__.__name__
    assert hasattr(Wee.objects, 'delete'), '%s should have the method "delete"' % classname
    assert callable(Wee.objects.delete), '%s.delete should be callable' % classname

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_method_delete_takes_model_or_modelset():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/wee/Wee.json')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/wee')).will(return_value(True))

    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Wee(Model):
        objects = managers.FileSystemModelManager(base_path='/home/wee')

    assert_raises(TypeError, Wee.objects.delete, None,
                  exc_pattern=r'delete\(\) takes a Wee as parameter, got None')

    assert_raises(TypeError, Wee.objects.delete, 5,
                  exc_pattern=r'delete\(\) takes a Wee as parameter, got 5')

    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

@with_setup(setup_fake_os, teardown_fake_os)
def test_model_file_manager_delete():
    codecs_mock = Mock()
    file_mock = Mock()
    path_mock = Mock()

    path_mock.expects(once()).exists(eq('/home/woo')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(True))
    path_mock.expects(once()).exists(eq('/home/woo/Woo.json')).will(return_value(True))

    os_path_module = managers.os.path
    codecs_module = managers.codecs
    managers.codecs = codecs_mock
    managers.os.path = path_mock

    class Woo(Model):
        name = CharField(max_length=100)
        objects = managers.FileSystemModelManager(base_path='/home/woo')
        def __unicode__(self):
            return '<FooBar(name=%r)>' % self.name

    w1 = Woo(name='foo bar')
    w2 = Woo(name='john doe')
    read_set = Woo.Set()(w1, w2)
    read_json = read_set.serialize('json')
    foobar = Woo.Set()(w2)
    write_json = foobar.serialize('json')
    codecs_mock.expects(once()).open(eq('/home/woo/Woo.json'),
                                     eq('r'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(write_json))
    file_mock.expects(once()).close()

    codecs_mock.expects(once()).open(eq('/home/woo/Woo.json'),
                                     eq('w'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).write(eq(write_json))
    file_mock.expects(once()).close()

    codecs_mock.expects(once()).open(eq('/home/woo/Woo.json'),
                                     eq('r'),
                                     eq('utf-8')).will(return_value(file_mock))
    file_mock.expects(once()).read().will(return_value(read_json))
    file_mock.expects(once()).close()

    Woo.objects.delete(w1)
    got = Woo.objects.all()
    assert got == foobar, 'Expected %r, got %r' % (foobar, got)

    path_mock.verify()
    file_mock.verify()
    codecs_mock.verify()

    managers.codecs = codecs_module
    managers.os.path = os_path_module

