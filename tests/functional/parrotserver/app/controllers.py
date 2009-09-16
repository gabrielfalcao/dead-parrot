# -*- coding: utf-8 -*-
import os
import cherrypy
from sponge import route
from sponge import Controller

from deadparrot import models

class Actor(models.Model):
    __module__ = 'deadparrot_tests'
    name = models.CharField(max_length=100)
    objects = models.FileSystemModelManager(base_path=os.path.abspath('.'))
    def __unicode__(self):
        return u'Actor %r' % self.name
import pdb; pdb.set_trace()
Actor.objects.all().delete()

Actor.objects.create(name='Eric Idle')
Actor.objects.create(name='Terry Jones')
Actor.objects.create(name='John Cleese')
Actor.objects.create(name='Graham Chapman')
Actor.objects.create(name='Michael Palin')

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
            import pdb; pdb.set_trace()
            return got.serialize('json')

        cherrypy.response.status = 404
        return "The model %s does not exist" % modelname
