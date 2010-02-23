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

from deadparrot.models.base import Model
from deadparrot.models import managers

from utils import assert_raises

def test_model_rest_manager_class_exists():
    msg1 = 'deadparrot.models should have the class RESTfulManager'
    assert hasattr(managers, 'RESTfulModelManager'), msg1
    msg2 = 'deadparrot.managers.RESTfulManager should have the class RESTfulManager'
    assert issubclass(managers.RESTfulModelManager, managers.ModelManager), msg2

def test_model_rest_manager_construction_without_prefix_raises():
    def make_class():
        class Parrot(Model):
            objects = managers.RESTfulModelManager()

    assert_raises(TypeError, make_class, exc_pattern='__setup__.. takes exactly 2 arguments .1 given.')

def test_model_rest_manager_construction_with_prefix_nonstring_raises():
    def make_class_number():
        class Parrot(Model):
            objects = managers.RESTfulModelManager(prefix=10)

    def make_class_list():
        class Parrot(Model):
            objects = managers.RESTfulModelManager(prefix=[])

    assert_raises(TypeError, make_class_number, exc_pattern='RESTfulModelManager "prefix" parameter should be string, got %r' % 10)
    assert_raises(TypeError, make_class_list, exc_pattern='RESTfulModelManager "prefix" parameter should be string, got %s' % re.escape(repr([])))
