v.. _index:

=========================
Dead Parrot Documentation
=========================

.. rubric:: Introduction.

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

In a nutshell you will be able to do something like it in the client::
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

================
SQLAlchemy usage
================
Nowadays Dead Parrot works with simple SQLAlchemy operations::

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

   >>> print car1.brand
   Chevy
   >>> print car1.color
   blue
   >>> print car2.website
   !http://www.theoscarproject.org/
   >>> Car.objects.all()
   Car.Set([<Car of brand "Chevy">, <Car of brand "OSCar">])
   >>> Car.objects.filter(Car.brand.like("%evy"))
   Car.Set([<Car of brand "Chevy">])


ForeignKey and serialization sauce
----------------------------------

   >>> from deadparrot import models
   >>> from datetime import datetime, date
   >>>
   >>> class Brand(models.Model):
   ...     id = models.IntegerField(primary_key=True)
   ...     name = models.CharField(max_length=100)
   ...     since = models.DateField()
   ...     website = models.CharField(max_length=0, validate=False)
   ...     def __unicode__(self):
   ...         return u'%s, making cars since %s' % self.name
   ...
   >>> class Car(models.Model):
   ...     id = models.IntegerField(primary_key=True)
   ...     brand = models.ForeignKey
   ...     color = models.CharField(max_length=15)
   ...     objects = models.SQLAlchemyManager(create_schema=True)
   ...     def __unicode__(self):
   ...         return '<Car of brand "%s">' % self.brand
   ...
   >>> cadillac = Brand.objects.create(name=u'Cadillac', since=date(1902, 8, 22), website=u'!http://www.cadillac.com')
   >>> oscar = Brand.objects.create(name=u'OS Car', since=date(1999, 1, 1), u'!http://www.theoscarproject.org/')
   >>> escalade = Car.objects.create(name=u'Escalade', color=u'black', brand=cadillac)
   >>> srx = Car.objects.create(name=u'SRX Luxury', color=u'black', brand=cadillac)
   >>> osmodel = Car.objects.create(brand=oscar, color="red")
   >>> Car.objects.all().serialize('xml')
