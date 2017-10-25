'''
Copyright (c) 2017 Víctor Ruiz Gómez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


from scrapy import Request
from urllib.parse import urlencode
from .splash_utils import splash_request, Wait, ElementReady, SendText, Click
from os.path import dirname, join


class TripAdvisorRequests:
    '''
    Este clase es la encargada de gestionar la generacin de requests a la página
    de TripAdvisor

    '''

    # URL Raíz de TripAdvisor
    root_url = 'https://www.tripadvisor.com'

    @classmethod
    def get_root_url(cls):
        '''
        :return: Devuelve la uri raíz de tripadvisor
        '''
        return cls.root_url

    @classmethod
    def get_resource_url(cls, path, params = None):
        '''
        Construye una url para acceder al recurso del cual se especifica su ruta y parámetros

        :param path: Es la ruta del recurso
        :param callback:
        :param params: Son los parámetros del recurso (Opcionales) Puede ser un diccionario
        donde cada entrada especifica un argumento en la url, o un string, en cuyo caso será añadido
        a la url directamente precedido por el símbolo ? (debe estar url-ificado)
        :return: Devuelve una url
        '''
        url = '{}/{}'.format(cls.get_root_url(), path)
        if not params is None:
            url += '?{}'.format(urlencode(params) if isinstance(params, dict) else params)
        return url


    @classmethod
    def request(cls, path, callback, params = None):
        '''
        Instancia una request para obtener el recurso sobre la ruta indicada, dado los parámetros
        especificados.
        :param path:
        :param callback Será el callback de la request
        :param params: Son los parámetros a añadir a la url de la request
        :return:
        e.g:
        TripAdvisorRequests.request('Search', callback = ..., params = {'q' : 'Blanca Navarra'})
        '''
        return Request(url = cls.get_resource_url(path, params), callback = callback)


    @classmethod
    def splash_request(cls, path, actions, callback, params = None):
        '''
        Devuelve una request a la url indicada, pero ejecutando antes las acciones que se indican
        como parámetro.
        '''
        return splash_request(url = cls.get_resource_url(path, params), callback = callback,
                              actions = actions)



    @classmethod
    def search_hotels_by_terms(cls, terms, callback):
        '''
        Instancia una request sobre una página de búsqueda de hoteles.
        :param terms: Es un texto que indica los términos de búsqueda
        :param callback:
        :return:
        Este método es un alias de
        TripAdvisorRequests.request('Search', params = {'q' : terms})
        '''
        return cls.request(path = 'Search', callback = callback, params = {'q' : terms})



    @classmethod
    def get_hotel_page(cls, fetch_deals = False, *args, **kwargs):
        '''
        Instancia una request a la página con la información de un hotel y sus reviews
        de una página de un hotel en trip advisor
        e.g:
        https://www.tripadvisor.com/Hotel_Review-g187520-d233664-Reviews-Hotel_Blanca_de_Navarra-Pamplona_Navarra.html
        :param fetch_deals Es un parámetro que si se establece a True, devuelve en el DOM de la
        página, las "deals" del hotel (la request usa splash para cargar contenido dinámico de
        la página)
        :return:
        '''
        use_splash = fetch_deals

        if use_splash:
            actions = ElementReady('div.premium_offers_area.viewDealChevrons')
            return cls.splash_request(actions = actions, *args, **kwargs)

        return cls.request(*args, **kwargs)



class GMapRequests:
    # URL raíz de la API Google Maps
    root_url = 'https://maps.googleapis.com/maps/api/geocode/json'

    @classmethod
    def get_root_url(cls):
        return cls.root_url


    '''
    Esta clase provee una serie de métodos para hacer requests a la API de Google Maps
    '''
    @classmethod
    def search_place(cls, address, callback):
        '''
        Realiza una request a la API de Google Maps para buscar una localización o lugar.
        :param address: Es un lugar o dirección
        :param callback:
        :return:
        '''
        with open(join(dirname(dirname(__file__)), 'keys', 'gmaps_api_key.txt'), 'r') as fh:
            api_key = fh.read()
        params = {
            'address' : address,
            'key' : api_key
        }

        url = '{}?{}'.format(cls.get_root_url(), urlencode(params))

        return Request(url = url, callback = callback)




