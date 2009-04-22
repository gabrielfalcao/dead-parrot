What is the Dead Parrot ?
=========================

Is a RESTful framework based in the declarative approach of Django
models, in which you describe a class and it's fields, to be
serialized/deserialized in many formats (for now, xml and json).

The project have been concepted to allow the developer to write their
own format-style or serializer, deal with data validation and so on,
without even needing the whole Django stack.

I't have also been concepted to offer a standalone web server, based on cherrypy, to serve the resources,
and to consume that resources through a client layer, that's also based in the Django queryset manager.

Why "Dead Parrot"
=================

In tribute to one of my favorites Monty Python's sketch. In the sketch
a customer try to exchange his parrot, that have been bought dead, and
then he argue with the seller.

Dead Parrot means to become a library to reach both server and client
requisites, so it can be the "seller" as server providing a RESTful
API, and can also be the "customer" consuming the API.

Hands on!
=========
In the future you will be able to do many operations, and use both RESTful and SQLAlchemy manager (inclusive),
but unfortunately, for now Dead parrot works with simple SQLAlchemy operations::

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

* For now Dead Parrot does not support models.ForeignKey,
models.OneToOneField and models.ManyToManyField, but I intend to
implement it in a few days.
* Implement the RESTful manager, allowing the developer to consume
  resources in a very django-ish way

Build dependencies:
===================

Dead Parroy lays in some very known python libraries, and you got to
install them in order to start playing with the framework:

* lxml for XML serialization: http://codespeak.net/lxml/ (in Debian: python-lxml)
* sqlalchemy >= 0.5.3: http://www.sqlalchemy.org/ (in Debian: python-sqlalchemy)
* simplejson for JSON serialization: http://pypi.python.org/pypi/simplejson/ (in Debian: python-simplejson)
