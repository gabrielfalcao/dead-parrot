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
import sys
import traceback

def one_line_xml(string):
    string = "".join(string.splitlines())
    string = re.sub("[>]\s+[<]", "><", string)
    string = string.strip()
    return string

def ignore_it(why):
    def wrapp(func):
        err = 'WARNING: %r is being ignored because "%s"\n' % (func, why)
        sys.stderr.write("===========================================\n")
        sys.stderr.write(err)
        sys.stderr.write("===========================================\n")
    return wrapp

def assert_raises(exception, callable, *args, **kwargs):
    if "exc_args" in kwargs:
        exc_args = kwargs["exc_args"]
        del kwargs["exc_args"]
    else:
        exc_args = None
    if "exc_pattern" in kwargs:
        exc_pattern = kwargs["exc_pattern"]
        if isinstance(exc_pattern, basestring):
            exc_pattern = re.compile(exc_pattern)

        del kwargs["exc_pattern"]
    else:
        exc_pattern = None

    argv = [repr(a) for a in args]\
           + ["%s=%r" % (k,v)  for k,v in kwargs.items()]
    callsig = "%s(%s)" % (callable.__name__, ", ".join(argv))

    try:
        callable(*args, **kwargs)
    except exception, exc:
        if exc_args is not None:
            assert exc.args != exc_args, \
                        "%s raised %s with unexpected args: "\
                        "expected=%r, actual=%r"\
                        % (callsig, exc.__class__, exc_args, exc.args)
        if exc_pattern is not None:
            assert exc_pattern.search(str(exc)), \
                            "%s raised %s, but the exception "\
                            "does not match '%s': %r"\
                            % (callsig, exc.__class__, exc_pattern.pattern,
                               str(exc))
    except Exception, e:
        assert False, "%s raised an unexpected exception type: "\
                  "expected=%s, actual=%s"\
                  % (callsig, exception, traceback.format_exc(e))
    else:
        assert False, "%s did not raise %s" % (callsig, exception)

class FakeGetter(object):
    def __call__(self, *args, **kw):
        return self

    def __getattr__(self, attr):
        if not attr.startswith('_') and not attr.endswith('_'):
            return self
        else:
            return super(FakeGetter, self).__getattr__(attr)

