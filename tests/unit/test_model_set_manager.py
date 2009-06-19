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

from nose.tools import *
from deadparrot import models

def test_model_set_manager_construct_fails_with_no_params():
    assert_raises(TypeError, models.ModelSetManager)

def test_model_set_manager_construct_fails_without_receiving_model_as_param():
    should_raise_assertion = "Constructing a ModelSetManager with any thing " \
                             "different of a models.Model should raise a " \
                             "TypeError"
    expected_error_message = 'ModelSetManager takes a models.Model subclass ' \
                             'as construction parameter, got None'
    unexpected_error_message_assertion = 'Unexpected message when expecting ' \
                                         'TypeError: "%s"'

    try:
        wrong_manager = models.ModelSetManager(None)
        assert False, should_raise_assertion
    except TypeError, e:
        assert unicode(e) == expected_error_message, \
        unexpected_error_message_assertion % e

def test_model_set_manager_has_model_attribute():
    class ModelSetModelTest1(models.Model):
        pass

    manager = models.ModelSetManager(ModelSetModelTest1)
    assert hasattr(manager, 'model'), \
           'ModelSetManager should have the attribute "model"'

def test_model_set_manager_model_attribute_should_be_the_managed_model():
    class ModelSetModelTest2(models.Model):
        pass

    manager = models.ModelSetManager(ModelSetModelTest2)
    assert manager.model is ModelSetModelTest2, \
           'manager.model should be ModelSetModelTest2. Got %r' % manager.model

def test_model_set_manager_should_have_attribute_objects():
    class ModelSetModelTest3(models.Model):
        pass

    manager = models.ModelSetManager(ModelSetModelTest3)
    assert hasattr(manager, 'objects'), \
           'manager.model should have the attribute "objects"'

def test_model_set_manager_objects_attribute_should_be_a_dict():
    class ModelSetModelTest4(models.Model):
        pass

    manager = models.ModelSetManager(ModelSetModelTest4)
    assert isinstance(manager.objects, dict), \
           'manager.objects should be a list, but is a %r' % type(manager.objects)


class ModelSetModelTestMethods(models.Model):
    pass


def test_model_set_manager_has_method_add():
    methods_test_manager = models.ModelSetManager(ModelSetModelTestMethods)
    assert hasattr(methods_test_manager, 'add'), 'models.ModelSetManager should have the method "add"'
    assert callable(methods_test_manager.add), 'models.ModelSetManager.add should be callable'

def test_model_set_manager_add_fails_when_param_is_not_correspondent_model():
    should_raise_assertion = "calling ModelSetManager.add with any parameter " \
                             "different its managed model's instance " \
                             "should raise a TypeError"
    expected_error_message = 'ModelSetManager.add takes a instance of %r ' \
                             'as parameter, got None'
    unexpected_error_message_assertion = 'Unexpected message when expecting ' \
                                         'TypeError: "%s"'

    manager = models.ModelSetManager(ModelSetModelTestMethods)

    try:
        manager.add(None)
        assert False, should_raise_assertion
    except TypeError, e:
        assert unicode(e) == expected_error_message % ModelSetModelTestMethods, \
        unexpected_error_message_assertion % e

def test_model_set_manager_method_add_takes_a_model_instance_as_parameter():
    methods_test_manager = models.ModelSetManager(ModelSetModelTestMethods)
    assert hasattr(methods_test_manager, 'add'), 'models.ModelSetManager should have the method "add"'
    assert callable(methods_test_manager.add), 'models.ModelSetManager.add should be callable'

def test_model_set_manager_add_include_object_in_its_objects():
    add_method_manager = models.ModelSetManager(ModelSetModelTestMethods)
    model1 = ModelSetModelTestMethods()
    model2 = ModelSetModelTestMethods()
    model3 = ModelSetModelTestMethods()

    message1 = '%s should be in add_method_manager, ' \
               'onde it was added through ModelSetManager.add method'

    message2 = 'The length of objects should be %d, but is %d'
    add_method_manager.add(model1)
    assert model1 in add_method_manager.objects.values(), message1 % 'model1'
    assert len(add_method_manager.objects) == 1, message2 % (1, len(add_method_manager.objects))
    add_method_manager.add(model2)
    assert model2 in add_method_manager.objects.values(), message1 % 'model2'
    assert len(add_method_manager.objects) == 2, message2 % (2, len(add_method_manager.objects))
    add_method_manager.add(model3)
    assert model3 in add_method_manager.objects.values(), message1 % 'model3'
    assert len(add_method_manager.objects) == 3, message2 % (3, len(add_method_manager.objects))

def test_model_set_manager_add_replaces_when_model_is_same():
    add_method_manager = models.ModelSetManager(ModelSetModelTestMethods)
    model1 = ModelSetModelTestMethods()

    message1 = '%s should be in add_method_manager, ' \
               'onde it was added through ModelSetManager.add method'
    message2 = 'The length of objects should be %d, but is %d'
    message3 = "The model1 should be replaced in " \
               "add_method_manager.objects, but was just appended"

    add_method_manager.add(model1)
    assert len(add_method_manager.objects) == 1, message2 % (1, len(add_method_manager.objects))
    add_method_manager.add(model1)
    assert len(add_method_manager.objects) == 1, message3
