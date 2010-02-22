What is the Dead Parrot ?
=========================

Dead Parrot is a RESTful framework with the declarative approach of Django
Models in mind. Describing a class and its fields, you can tailor the
serialization/deserialization of your model in several formats, including xml and json.

The project has been conceived to allow for custom-tailored format-styles and/or
serializers, model-aware data validation and other extensibility points. One key goal
for the project is removing the dependency that current tools have on the large Django stack.

Dead Parrot uses a much thinner layer to serve and consume its resources.
A standalone web server, based on the CherryPy_ project is included to serve resources,
as well as a client layer based in the Django queryset manager.

Why "Dead Parrot"
=================

It's a tribute to one of my favorite Monty Python's sketch. In the sketch
a customer tries to exchange his parrot, that have been bought dead, and
then he argues with the seller.

Goals
=====

* Provide a plugin-based pool of serializers, so you write yout model
  once, but deals with {de}serialization in many formats.

* Dead Parrot is a library that reaches both server and client tiers,
  so that it can be the "seller" as the server providing a RESTful
  API, and also the "customer" consuming the API.

* Dead Parrot also means to support database access through
  SQLAlchemy, but for the programmer, it will be transparent, and
  will feel like coding in Django.

Release plans
=============

As long as Dead Parrot is also a Monty Python's sketch, its release
names are sentences spoken by the actors, the odd numbered releases
are "the customer" phrases, and the even ones are from "the seller".

* Release HelloPolly (0.1) - Support all django-like model fields, serialization/deserialization on xml/json
* Release JustResting (0.2) - Embed a CherryPy serving RESTful resources, with a model-like declarative approach to resources, also support a django-like self-consuming its resources.
* Release PassedOn (0.3) - Support SQLAlchemy querying.

Build dependencies:
===================

Dead Parrot builds on some very well-known python libraries.
The consequence is that in order to use it, you need those installed.
They can be obtained from the following sites:

* lxml for XML serialization: http://codespeak.net/lxml/
* simplejson for JSON serialization: http://pypi.python.org/pypi/simplejson/

Or, to install those in Debian/Ubuntu::

    aptitude install python-lxml
    aptitude install python-simplejson

Hands On!
=========
What about doing some serialization ? ::

   >>> from deadparrot import models
   >>>
   >>> class Car(models.Model):
   ...     brand = models.CharField(max_length=20)
   ...     color = models.CharField(max_length=15)
   ...     website = models.CharField(max_length=0, validate=False)
   ...     def __unicode__(self):
   ...         return '<Car of brand "%s">' % self.brand
   ...
   >>> car1 = Car(brand="Chevy", color="blue")
   >>> car2 = Car(brand="OSCar", color="red", website="http://www.theoscarproject.org")
   >>> print car1.brand
   Chevy
   >>> print car1.color
   blue
   >>> car2.website
   u'http://www.theoscarproject.org'
   >>> json_cars = '{"Cars": [{"Car": {"website": "http://www.theoscarproject.org", "color": "red", "brand": "OSCar", "id": 2}}]}'
   >>> cars = Car.Set().deserialize(json_cars, format="json")
   >>> cars
   Car.Set([<Car of brand "OSCar">])
   >>> car2.serialize(to="xml")
   '<Car><color>red</color><website>http://www.theoscarproject.org</website><brand>OSCar</brand></Car>'

Building
========
* In GNU/Linux: make build
* In other systems: python setup.py test && python setup.py build

.. _CherryPy: http://www.cherrypy.org/
