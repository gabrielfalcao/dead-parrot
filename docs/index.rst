.. _index:

=========================
Dead Parrot Documentation
=========================

You will notice that this documentation is pretty close to the `Django documentation <http://docs.djangoproject.com/en/dev>`_,
it is totally intentional, once Dead Parrot approaches much like Django does, specially about the model-driven behavior.

What is this library for
========================

Is a RESTful framework based in the declarative approach of Django
models, in which you describe a class and it's fields, to be
serialized/deserialized in many formats (for now, xml and json).

The project have been concepted to allow the developer to write their
own format-style or serializer, deal with data validation and so on,
without even needing the whole Django stack.

I't have also been concepted to offer a standalone web server, based on cherrypy, to serve the resources,
and to consume that resources through a client layer, that's also based in the Django queryset manager.

The model layer
===============

    * **Models:**
      :ref:`Model syntax <model-syntax>` |
      :ref:`Serialization <serialization>`

    * **Model managers:**
      :ref:`FileSystem model manager <fs-modelmanager>` |

Thoughts
========

In a nutshell you will be able consume RESTful resources with something near to::

   >>> from deadparrot import models
   >>>
   >>> class Car(models.Model):
   ...     brand = models.CharField(max_length=20)
   ...     color = models.CharField(max_length=15)
   ...     website = models.CharField(max_length=0, validate=False)
   ...     objects = models.RESTfulManager(base_url="http://localhost:9090/api", resource="/car")
   ...
   >>> car = Car.objects.get(uuid="49a17b42-209c-4a86-b9e0-41c4ca134d0e")
   >>> print car.brand
   OSCar
   >>> print car.color
   red
   >>> print car.website
   !http://www.theoscarproject.org/

