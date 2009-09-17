# -*- coding: utf-8 -*-
import os
import cherrypy
from sponge import route
from sponge import Controller

from deadparrot import models

class Actor(models.Model):
    __module__ = 'deadparrot_tests'
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    objects = models.FileSystemModelManager(base_path=os.path.abspath('.'))
    def __unicode__(self):
        return u'Actor %r' % self.name

for actor in Actor.objects.all():
    Actor.objects.delete(actor)

Actor.objects.create(id=1, name='Eric Idle')
Actor.objects.create(id=2, name='Terry Jones')
Actor.objects.create(id=3, name='John Cleese')
Actor.objects.create(id=4, name='Graham Chapman')
Actor.objects.create(id=5, name='Michael Palin')

class ParrotController(Controller):
    @route('/', 'parrot_index')
    def index(self):
        cherrypy.response.status = 404
        return "NOT FOUND"

    @route('/:modelname', 'parrot_list_all')
    def list_all(self, modelname, **data):
        Model = models.ModelRegistry.get_model(app_label="deadparrot_tests",
                                               classname=modelname)

        cherrypy.response.headers['Content-Type'] = 'text/plain'
        if Model:
            got = Model.objects.filter(**data)
            return got.serialize('json')

        cherrypy.response.status = 404
        return "The model %s does not exist" % modelname

    @route('/:modelname/:id', 'parrot_list_all')
    def list_all(self, modelname, id, **data):
        Model = models.ModelRegistry.get_model(app_label="deadparrot_tests",
                                               classname=modelname)

        cherrypy.response.headers['Content-Type'] = 'text/plain'
        if Model:
            got = Model.objects.get(**data)
            if got:
                return got.serialize('json')

        cherrypy.response.status = 404
        return "The model %s does not exist" % modelname
