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
import sys
from re import sub as resub

def one_line_xml(string):
    string = "".join(string.splitlines())
    string = resub("[>]\s+[<]", "><", string)
    string = string.strip()
    return string

def ignore_it(why):
    def wrapp(func):
        err = 'WARNING: %r is being ignored because "%s"\n' % (func, why)
        sys.stderr.write("===========================================\n")
        sys.stderr.write(err)
        sys.stderr.write("===========================================\n")  
    return wrapp
