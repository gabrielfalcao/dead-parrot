Dead Parrot Core
=============================

Let's test it::
    >>> from deadparrot.client.models import Attribute
    >>> nc = Attribute(unicode)
    >>> nc.fill('full_name', 'John Doe')
    John Doe
    >>> nc.name
    'full_name'
    >>> nc.camel_name
    'fullName'
    >>> nc
    John Doe

Now with a class::
    >>> from deadparrot.client.models import XmlTag
    >>> from deadparrot.client.models import Attribute
    >>> from deadparrot.client.models import DateTimeAttribute
    >>> class Person(XmlTag):
    ...     name = Attribute(unicode)
    ...     age = Attribute(int)
    ...     creation_date = DateTimeAttribute("%Y/%m/%d")
    ...
    >>> xml = u"""
    ... <person name="John" age="21" creationDate="2009/03/23">
    ... </person>
    ... """
    >>> john = Person().from_xml(xml)
    >>> john.name
    u'John'
    >>> john.age
    21
    >>> john.creation_date.date()
    datetime.date(2009, 3, 23)

Now with a many classes::
    >>> xml = u"""
    ... <persons>
    ... <person name="John" age="21" creationDate="2009/03/23">
    ... </person>
    ... <person name="Mary" age="25" creationDate="2009/03/22">
    ... </person>
    ... </persons>
    ... """
    >>> people = Person.Set().from_xml(xml)
    >>> john, mary = people
    >>> john.name
    u'John'
    >>> john.age
    21
    >>> john.creation_date.date()
    datetime.date(2009, 3, 23)
    >>> mary.name
    u'Mary'
    >>> mary.age
    25
    >>> mary.creation_date.date()
    datetime.date(2009, 3, 22)
