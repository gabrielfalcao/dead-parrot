README
======

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
   >>> Car.objects.all().serialize(to="json")
   '{"Cars": [{"Car": {"website": "None", "color": "blue", "brand": "Chevy", "id": 1}}, {"Car": {"website": "http://www.theoscarproject.org", "color": "red", "brand": "OSCar", "id": 2}}]}'
   >>> json_cars = Car.objects.all().serialize(to="json")
   >>> cars = Car.Set().deserialize(json_cars, format="json")
   >>> cars
   Car.Set([<Car of brand "Chevy">, <Car of brand "OSCar">])
