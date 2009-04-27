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
Dead Parrot is a library that reaches both server and client
tiers, so that it can be the "seller" as the server providing a RESTful
API, and also the "customer" consuming the API.

Hands on!
=========
In the future you will be able to do several operations, and use both RESTful and SQLAlchemy manager (inclusive),
but unfortunately, for now Dead Parrot works with simple SQLAlchemy operations::

   >>> from deadparrot import models
   >>>
   >>> class Car(models.Model):
   ...     id = models.IntegerField(primary_key=True)
   ...     brand = models.CharField(max_length=20)
   ...     color = models.CharField(max_length=15)
   ...     website = models.CharField(max_length=0, validate=False)
   ...     objects = models.SQLAlchemyManager(create_schema=True)
   ...     def __unicode__(self):
   ...         return '<Car of brand "%s">' % self.brand
   ...
   >>> car1 = Car.objects.create(brand="Chevy", color="blue")
   >>> car2 = Car.objects.create(brand="OSCar", color="red", website="http://www.theoscarproject.org")
   >>> print car1.brand
   Chevy
   >>> print car1.color
   blue
   >>> car2.website
   u'http://www.theoscarproject.org'
   >>> Car.objects.all()
   Car.Set([<Car of brand "Chevy">, <Car of brand "OSCar">])
   >>> Car.objects.filter(Car.brand.like(u"%evy"))
   Car.Set([<Car of brand "Chevy">])
   >>> Car.objects.filter(Car.brand==u'OSCar').serialize(to="json")
   '{"Cars": [{"Car": {"website": "http://www.theoscarproject.org", "color": "red", "brand": "OSCar", "id": 2}}]}'
   >>> json_cars = Car.objects.all().serialize(to="json")
   >>> cars = Car.Set().deserialize(json_cars, format="json")
   >>> cars
   Car.Set([<Car of brand "Chevy">, <Car of brand "OSCar">])
   >>> car2.serialize(to="xml")
   '<Car><website>http://www.theoscarproject.org</website><color>red</color><brand>OSCar</brand><id>2</id></Car>'

TODO:
=====

* models.ForeignKey, models.OneToOneField and models.ManyToManyField are not yet supported, but they should be implemented soon.
* Implement the RESTful manager, allowing the developer to consume resources in a very django-ish way

Build dependencies:
===================

Dead Parrot builds on some very well-known python libraries.
The consequence is that in order to use it, you need those installed.
They can be obtained from the following sites:

* lxml for XML serialization: http://codespeak.net/lxml/ (in Debian: python-lxml)
* sqlalchemy >= 0.5.3: http://www.sqlalchemy.org/ (in Debian: python-sqlalchemy)
* simplejson for JSON serialization: http://pypi.python.org/pypi/simplejson/ (in Debian: python-simplejson)

.. _CherryPy: http://www.cherrypy.org/
