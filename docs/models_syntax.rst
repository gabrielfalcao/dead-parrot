.. _model-syntax:

======
Models
======

.. module:: deadparrot.models

A model is the way you are going to hold your data. It contains the
essential fields and behaviors of the data you're storing.  In this
case, the difference between Dead Parrot and Django is that Dead
Parrot hold the data, but were it will be persisted is just a matter
of how you are meaning to use Dead Parrot. For instance, you can get
its data serialized in xml or json, and store in a REST resource.

The basics:

    * Each model is a Python class that subclasses
      :class:`deadparrot.models.Model`.

    * Each attribute of the model represents a field that handles the data, with validation.

.. seealso::

    A companion to this document is the `official repository of model
    examples`_.

    .. _official repository of model examples: http://www.djangoproject.com/documentation/models/

Quick example
=============

This example model defines a ``Person``, which has a ``first_name`` and
``last_name``::

    from deadparrot import models

    class Person(models.Model):
        first_name = models.CharField(max_length=30)
        last_name = models.CharField(max_length=30)

``first_name`` and ``last_name`` are fields_ of the model. Each field is
specified as a class attribute, and each attribute maps to a database column.

Fields
======

The most important part of a model -- and the only required part of a model --
is the list of database fields it defines. Fields are specified by class
attributes.

Example::

    class Musician(models.Model):
        first_name = models.CharField(max_length=50)
        last_name = models.CharField(max_length=50)
        instrument = models.CharField(max_length=100)

    class Album(models.Model):
        artist = models.ForeignKey(Musician)
        name = models.CharField(max_length=100)
        release_date = models.DateField()
        num_stars = models.IntegerField()
