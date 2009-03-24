.. _core:

Introdução ao core da API
=========================

O Core da WebMedia API é baseado em 3 classes: Uma classe para lidar
com atributos de tags xml, seu nome é Attribute. Na verdade essa
classe não possui nenhuma funcionalidade muito excepcional, no
entanto, ela é usada na introspecção da classe de tag xml, descrita na
próxima seção.
Vamos aos testes da classe de atributo, primeiro
testamos o preenchimento do objeto em runtime.

.. doctest::

         >>> from webmedia.core import Attribute
         >>> nc = Attribute()
         >>> nc.fill('nome_completo', 'Fulano da Silva')
         >>> nc.name
         'nome_completo'
         >>> nc.camel_name
         'nomeCompleto'
         >>> nc
         Fulano da Silva

Agora vamos testar somente na contrução.

.. doctest::

         >>> from webmedia.core import Attribute
         >>> nc = Attribute('nome_completo', 'Beltrano Fulano')
         >>> nc.name
         'nome_completo'
         >>> nc.camel_name
         'nomeCompleto'
         >>> nc
         Beltrano Fulano

Temos também uma classe para descrever uma tag xml, cada atributo da
tag deve ser um atributo da classe, e por sua vez deve ser uma
instância da classe Atributo.  Para exemplificar, uma tag hipotética
de Pessoa que possui nome completo, no XML ficaria algo como:
`<pessoa nomeCompleto="Fulano da Silva"></pessoa>`
Para representar usando a classe de tag, seria algo como.

.. doctest::

     >>> from webmedia.core import Pessoa
     >>> from xml.dom.ext.reader import Sax2
     >>> PessoaSet = Pessoa.Set()
     >>> # criando um xml falso
     >>> fake_xml = '''<?xml version="1.0" encoding="UTF-8"?>
     ... <set>
     ...     <pessoa nomeCompleto="Fulano">
     ...     </pessoa>
     ...     <pessoa nomeCompleto="Beltrano">
     ...     </pessoa>
     ...     <pessoa nomeCompleto="Cicrano">
     ...     </pessoa>
     ... </set>
     ... '''
     ...
     >>> # obtendo um DOM a partir do xml
     >>> dom = Sax2.FromXml(fake_xml).documentElement
     >>> PessoaSet(dom)
     <Pessoa.Set total=3>
