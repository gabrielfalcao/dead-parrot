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

from nose.tools import assert_equals
from deadparrot import models

from utils import assert_raises

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
    assert isinstance(manager.objects, list), \
           'manager.objects should be a list, but is a %r' % type(manager.objects)


class ModelSetModelTestMethods(models.Model):
    pass


def test_model_set_manager_has_method_add():
    methods_test_manager = models.ModelSetManager(ModelSetModelTestMethods)
    assert hasattr(methods_test_manager, 'add'), 'models.ModelSetManager should have the method "add"'
    assert callable(methods_test_manager.add), 'models.ModelSetManager.add should be callable'

def test_model_set_manager_add_fails_when_param_is_not_corresponcent_model():
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
    assert_raises(TypeError, methods_test_manager.add, 'blabla', exc_pattern=r"ModelSetManager.add takes a instance of %r as parameter, got 'blabla'" % methods_test_manager.model)
    assert_raises(TypeError, methods_test_manager.add, None, exc_pattern=r"ModelSetManager.add takes a instance of %r as parameter, got None" % methods_test_manager.model)

def test_model_set_manager_add_include_object_in_its_objects():
    add_method_manager = models.ModelSetManager(ModelSetModelTestMethods)
    model1 = ModelSetModelTestMethods()
    model2 = ModelSetModelTestMethods()
    model3 = ModelSetModelTestMethods()

    message1 = '%s should be in add_method_manager, ' \
               'once it was added through ModelSetManager.add method'

    message2 = 'The length of objects should be %d, but is %d'
    add_method_manager.add(model1)
    assert model1 in add_method_manager.objects, message1 % 'model1'
    assert len(add_method_manager.objects) == 1, message2 % (1, len(add_method_manager.objects))
    add_method_manager.add(model2)
    assert model2 in add_method_manager.objects, message1 % 'model2'
    assert len(add_method_manager.objects) == 2, message2 % (2, len(add_method_manager.objects))
    add_method_manager.add(model3)
    assert model3 in add_method_manager.objects, message1 % 'model3'
    assert len(add_method_manager.objects) == 3, message2 % (3, len(add_method_manager.objects))

def test_model_set_manager_add_keeps_the_adition_order():
    add_method_manager = models.ModelSetManager(ModelSetModelTestMethods)
    model1 = ModelSetModelTestMethods()
    model2 = ModelSetModelTestMethods()
    model3 = ModelSetModelTestMethods()

    add_method_manager.add(model2)
    add_method_manager.add(model1)
    add_method_manager.add(model2)
    add_method_manager.add(model3)

    assert_equals(add_method_manager.objects[0], model2)
    assert_equals(add_method_manager.objects[1], model1)
    assert_equals(add_method_manager.objects[2], model3)

def test_model_set_manager_add_replaces_when_model_is_same():
    add_method_manager = models.ModelSetManager(ModelSetModelTestMethods)
    model1 = ModelSetModelTestMethods()

    message1 = '%s should be in add_method_manager, ' \
               'once it was added through ModelSetManager.add method'
    message2 = 'The length of objects should be %d, but is %d'
    message3 = "The model1 should be replaced in " \
               "add_method_manager.objects, but was just appended"

    add_method_manager.add(model1)
    assert len(add_method_manager.objects) == 1, message2 % (1, len(add_method_manager.objects))
    add_method_manager.add(model1)
    assert len(add_method_manager.objects) == 1, message3

def test_model_set_manager_has_method_remove():
    methods_test_manager = models.ModelSetManager(ModelSetModelTestMethods)
    assert hasattr(methods_test_manager, 'remove'), 'models.ModelSetManager should have the method "remove"'
    assert callable(methods_test_manager.remove), 'models.ModelSetManager.remove should be callable'

def test_model_set_manager_remove_fails_when_param_is_not_corresponcent_model():
    should_raise_assertion = "calling ModelSetManager.remove with any parameter " \
                             "different its managed model's instance " \
                             "should raise a TypeError"
    expected_error_message = 'ModelSetManager.remove takes a instance of %r ' \
                             'as parameter, got None'
    unexpected_error_message_assertion = 'Unexpected message when expecting ' \
                                         'TypeError: "%s"'

    manager = models.ModelSetManager(ModelSetModelTestMethods)

    try:
        manager.remove(None)
        assert False, should_raise_assertion
    except TypeError, e:
        assert unicode(e) == expected_error_message % ModelSetModelTestMethods, \
        unexpected_error_message_assertion % e

def test_model_set_manager_method_remove_takes_a_model_instance_as_parameter():
    methods_test_manager = models.ModelSetManager(ModelSetModelTestMethods)
    assert hasattr(methods_test_manager, 'remove'), 'models.ModelSetManager should have the method "remove"'
    assert callable(methods_test_manager.remove), 'models.ModelSetManager.remove should be callable'

def test_model_set_manager_remove_remove_object_from_its_objects():
    remove_method_manager = models.ModelSetManager(ModelSetModelTestMethods)
    model1 = ModelSetModelTestMethods()

    message1 = '%s should be in remove_method_manager, ' \
               'once it was removed through ModelSetManager.remove method'

    message2 = 'The length of objects should be %d, but is %d'
    remove_method_manager.add(model1)
    assert model1 in remove_method_manager.objects, message1 % 'model1'
    assert len(remove_method_manager.objects) == 1, message2 % (1, len(remove_method_manager.objects))
    remove_method_manager.remove(model1)
    assert model1 not in remove_method_manager.objects, message1 % 'model1'
    assert len(remove_method_manager.objects) == 0, message2 % (2, len(remove_method_manager.objects))

def test_model_set_manager_remover_raises_when_object_not_within():
    remove_method_manager = models.ModelSetManager(ModelSetModelTestMethods)
    model = ModelSetModelTestMethods()
    try:
        remove_method_manager.remove(model)
        assert False, 'ModelSetManager.remove removing a model '\
               'that is not inside it, should raise ValueError. But did not!'
    except ValueError, e:
        assert unicode(e) == '<ModelSetModelTestMethods object> not in ' \
               '<ModelSetManager for ModelSetModelTestMethods object>', \
               'Unexpected message when expecting ValueError: "%s"' % unicode(e)


def test_model_set_manager_has_method_as_modelset():
    methods_test_manager = models.ModelSetManager(ModelSetModelTestMethods)
    assert hasattr(methods_test_manager, 'as_modelset'), 'models.ModelSetManager should have the method "as_modelset"'
    assert callable(methods_test_manager.as_modelset), 'models.ModelSetManager.as_modelset should be callable'

def test_model_set_managet_method_as_modelset_returns_a_modelset():
    methods_test_manager = models.ModelSetManager(ModelSetModelTestMethods)
    assert methods_test_manager.as_modelset().__class__.__name__ == ModelSetModelTestMethods.Set().__name__, \
           'Should return a instance of ModelSetModelTestMethods.Set() but got a %r' % methods_test_manager.as_modelset()

def test_model_set_manager_has_method_to_dict():
    methods_test_manager = models.ModelSetManager(ModelSetModelTestMethods)
    assert hasattr(methods_test_manager, 'to_dict'), 'models.ModelSetManager should have the method "to_dict"'
    assert callable(methods_test_manager.to_dict), 'models.ModelSetManager.to_dict should be callable'

def test_model_set_manager_has_method_from_dict():
    methods_test_manager = models.ModelSetManager(ModelSetModelTestMethods)
    assert hasattr(methods_test_manager, 'from_dict'), 'models.ModelSetManager should have the method "from_dict"'
    assert callable(methods_test_manager.from_dict), 'models.ModelSetManager.from_dict should be callable'

def test_model_set_manager_method_from_dict_takes_a_dict_as_parameter():
    methods_test_manager = models.ModelSetManager(ModelSetModelTestMethods)
    assert_raises(TypeError, methods_test_manager.from_dict, 'blabla', exc_pattern=r"ModelSetModelTestMethodsSet.from_dict takes a dict as parameter. Got %r" % type('blabla'))
    assert_raises(TypeError, methods_test_manager.from_dict, None, exc_pattern=r"ModelSetModelTestMethodsSet.from_dict takes a dict as parameter. Got %r" % type(None))
