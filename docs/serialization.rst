.. _serialization:

======
Serialization
======

.. module:: deadparrot.serialization

The main feature of Dead Parrot is its well tested serialization
structure.  Dead Parrot has native support for serializing in one json
pattern and one xml pattern, but you can also implement your own
serialization plugin, specifilacy for your application, and plug wo
Dead Parrot transparently.

This documentation page will guide you how to use the native plugins,
and how to write and use custom ones.

JSON
====

testcode::

    class Musician(models.Model):
        first_name = models.CharField(max_length=50, primary_key=True)
        last_name = models.CharField(max_length=50)
        instrument = models.CharField(max_length=100)

    class Album(models.Model):
        artist = models.ForeignKey(Musician)
        name = models.CharField(max_length=100, primary_key=True)
        release_date = models.DateField()
        num_stars = models.IntegerField()
