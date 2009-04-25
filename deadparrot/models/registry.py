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

# the global registry, by module, app_label and classes
_REGISTRY = {}
# the module-based registry: module -> classes
_MODULE_REGISTRY = {}
# the app_label-based registry: app_label -> classes
_APP_REGISTRY = {}


class ModelRegistry(object):
    @classmethod
    def get_all(cls, by_class=None, by_module=None, by_app_label=None):
        if by_class:
            if not isinstance(by_class, basestring):
                raise TypeError, "ModelRegistry.get_all "\
                      "by_class parameter takes a string "\
                      "as parameter, got %r" % by_class
            ret = []
            for module, app_dict in _REGISTRY.items():
                for app_label, classdict in app_dict.items():
                    for classname, klass in classdict.items():
                        if classname == by_class:
                            ret.append(klass)

            return tuple(ret)

        if by_module:
            if not isinstance(by_module, basestring):
                raise TypeError, "ModelRegistry.get_all "\
                      "by_module parameter takes a string "\
                      "as parameter, got %r" % by_module
            ret = []
            for modname, classdict in _MODULE_REGISTRY.items():
                if modname == by_module:
                    ret.extend(classdict.values())
            return ret

        if by_app_label:
            if not isinstance(by_app_label, basestring):
                raise TypeError, "ModelRegistry.get_all "\
                      "by_app_label parameter takes a string "\
                      "as parameter, got %r" % by_app_label

            ret = []
            for modname, classdict in _APP_REGISTRY.items():

                if modname == by_app_label:
                    ret.extend(classdict.values())
            return ret

    @classmethod
    def get_model(cls, app_label, classname):
        if not isinstance(app_label, basestring):
            raise TypeError, "ModelRegistry.get_model takes the parameter" \
                  "app_label as string. Got %r" % app_label

        if not isinstance(classname, basestring):
            raise TypeError, "ModelRegistry.get_model takes the parameter" \
                  "classname as string. Got %r" % classname

        classdict = _APP_REGISTRY.get(app_label)
        if not classdict:
            raise AttributeError, "The app_label %s is not "\
                  "within Dead Parrot's registry." \
                " Are you sure you've imported it ?" % app_label

        return classdict.get(classname)
