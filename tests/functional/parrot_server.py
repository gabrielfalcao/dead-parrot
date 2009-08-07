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
import os
import socket
import cherrypy
from deadparrot import models

class Actor(models.Model):
    name = models.CharField(max_length=100)
    objects = models.FileSystemModelManager(base_path=os.path.abspath('.'))
    def __unicode__(self):
        return u'Actor %r' % self.name

Actor.objects.create(name='Eric Idle')
Actor.objects.create(name='Terry Jones')
Actor.objects.create(name='John Cleese')
Actor.objects.create(name='Graham Chapman')
Actor.objects.create(name='Michael Palin')

class ParrotController:
    @cherrypy.expose
    def actor(self, attribute=None, value=None, action=None):
        cherrypy.response.status = 200
        if not attribute:
            if cherrypy.request.method == 'POST':
                try:
                    actor = Actor.deserialize(cherrypy.request.body.read(), 'json')
                except TypeError, e:
                    cherrypy.response.status = 500
                    return unicode(e)
                cherrypy.response.status = 201
                Actor.objects.add(actor)
                return actor.serialize('json')

        if attribute and not hasattr(Actor, attribute):
            cherrypy.response.status = 404
            return 'Invalid attribute: %s' % attribute

        if value:
            filtered = [p for p in actors.items \
                        if hasattr(p, attribute) \
                        and value in getattr(p, attribute)]
            first = filtered[0]

            if cherrypy.request.method == 'PUT':
                try:
                    actor = Actor.deserialize(cherrypy.request.body.read(), 'json')
                except TypeError, e:
                    cherrypy.response.status = 500
                    return unicode(e)

                actors.remove(first)
                actors.add(actor)
                return actor.serialize('json')

            if action == 'delete':
                actors.remove(first)
                return first.serialize('json')

            return ActorSet(*filtered).serialize('json')

        return actors.serialize('json')

def port_is_free(server, port):
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        connection.bind((server, port))
        connection.close()
        del connection
        return True
    except socket.error, e:
        if e.args[0] is 98:
            return False
        else:
            raise e

if __name__ == '__main__':
    if not port_is_free('localhost', 6060):
        print 'The port 6060 in localhost is not free, Bolacha ' \
        'functional tests can not proceed'
        raise SystemExit(1)

    cherrypy.config['server.socket_port'] = 6060
    cherrypy.quickstart(ParrotController(), '/', config={})

