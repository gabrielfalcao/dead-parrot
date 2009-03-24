.. _api:

Documentação da API python-webmedia
===================================

A globo.com possui internamente um sistema de serviços
RESTful baseado em XML, onde é possível obter toda a mídia da empresa
através de uma API concisa e poderosa. Basicamente, usando os serviços
de webmedia, é possível desde obter dados sobre vídeos através de
palavras-chave, até os vídeos mais acessados sobre um determinado
assunto.  Esta é a documentação + testes de uma implementação em
Python de cliente para a API de WebMedia.

Primeiramente, vêm os testes sobre como se preparar para lidar com o
conteúdo do XML, o ideal é trabalhar com código mais interativo o
possível, com uma utilização razoável de orientação a objetos +
conceitos de padronização de código python, também conhecido como
"Fazer código pythônico".

Primeiramente é necessário obter as mídias, quero obter os primeiros
30 vídeos que estejam no assunto "música".
.. testcode::

   >>> import webmedia
   >>> api = webmedia.Api()
   >>> api.videos_por_assunto(u"música").obter(30)
   <Midia.Set total=30>
   >>> videos1 = api.videos_por_assunto(u"música").obter(30)
   >>> len(videos1) == 30
   True
   >>> isinstance(videos1[0], webmedia.Midia)
   True
