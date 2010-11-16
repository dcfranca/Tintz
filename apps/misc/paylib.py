# -*- coding: utf-8 -*-

import sys
import urllib2, urllib
from django.http import HttpResponse

class Pagamento(object):

    def _conectar(self, url, params):
        query_str = urllib.urlencode(params)
        req = urllib2.Request(url, query_str)
        f = urllib2.urlopen(req)
        conteudo = f.read()
        f.close()
        return conteudo

    def _enviar(self, url, params):
        retorno = self._conectar(url, params)
        if retorno.lower() == 'verificado':
            return True
        else:
            return False


class PagSeguro(Pagamento):
    def processar(self, token, params, url='https://pagseguro.uol.com.br/Security/NPI/Default.aspx'):
        if not params:
            return False
        else:
            lista = []
            for key in params.keys():
                lista.append((key,params[key]))
            lista.append(('Comando', 'validar'))
            lista.append(('Token', token))

            return self._enviar(url, lista)