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

from deadparrot import models
from deadparrot.models import managers

def test_manager_construction_returns_a_tuple_with_3_items():
    manager = models.ModelManager()
    assert isinstance(manager, tuple), 'models.ModelManager() should return a tuple, got %s' % repr(manager)
    assert len(manager) is 3, 'The length of %s should be 3, but is %d' % (repr(managers), len(managers))

def test_manager_construction_tuple_first_item_is_a_class():
    manager = models.ModelManager()
    msg1 = 'models.ModelManager()[0] should return a class, got %s instead' % repr(manager)
    msg2 = 'models.ModelManager()[0] should be a subclass of managers.ObjectsManager, got %s instead' % repr(manager)
    assert isinstance(manager[0], type), msg1
    assert issubclass(manager[0], managers.ObjectsManager), msg2

def test_manager_construction_tuple_second_item_is_args_passed_to_manager():
    args = 'one', 2, u'three'
    manager = models.ModelManager(*args)
    msg = 'models.ModelManager()[1] should be %r, got %s instead' % (repr(args), repr(manager))
    assert manager[1] == args, msg

def test_manager_construction_tuple_third_item_is_kwargs_passed_to_manager():
    kwargs = dict(name='foo', age=20)
    manager = models.ModelManager(**kwargs)
    msg = 'models.ModelManager()[2] should be %r, got %s instead' % (repr(kwargs), repr(manager))
    assert manager[2] == kwargs, msg

def test_manager_construction_within_a_model_is_instance_of_objects_manager():
    class Parrot(models.Model):
        objects = models.ModelManager('first', 'arg', first='kwargs', second='wee')

    msg = 'Parrot.objects should be a managers.ObjectsManager instance, got %r' % Parrot.objects
    assert isinstance(Parrot.objects, managers.ObjectsManager), msg

def test_manager_within_model_has_model_attribute():
    class Parrot(models.Model):
        objects = models.ModelManager('first', 'arg', first='kwargs', second='wee')

    msg = 'Parrot.objects should have the attribute "model"'
    assert hasattr(Parrot.objects, 'model'), msg

def test_manager_within_model_attribute_model_should_be_respective_model():
    class Parrot(models.Model):
        objects = models.ModelManager('first', 'arg', first='kwargs', second='wee')

    msg = 'Parrot.objects.model should be %r, but got %r.' % (Parrot, Parrot.objects.model)
    assert Parrot.objects.model is Parrot, msg
