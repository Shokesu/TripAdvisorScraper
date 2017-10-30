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
from .splash_utils import *
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
        :param callback: Es un callback que será invocado cuando se haya procesado la respuesta
        a la request
        :param params: Son los parámetros del recurso (Opcionales) Puede ser un diccionario
        donde cada entrada especifica un argumento en la url, o un string, en cuyo caso será añadido
        a la url directamente precedido por el símbolo ? (debe estar url-ificado)
        :return: Devuelve una url
        '''

        url = '{}/{}'.format(cls.get_root_url(), path) if not path is None else cls.get_root_url()
        if not params is None:
            url += '?{}'.format(urlencode(params) if isinstance(params, dict) else params)
        return url


    @classmethod
    def request(cls, callback, path = None, url = None, params = None, **kwargs):
        '''
        Instancia una request para obtener el recurso sobre la ruta indicada, dado los parámetros
        especificados.
        La url de la request se construye usando el parámetro "url" si se especifica.
        En caso contrario, se usa el parámetor "path" y la url será: https://www.tripadvisor.com/{path}?{params}
        :param path: Sirve para construir la ruta
        :param url: Es la url de la request.
        :param callback Será el callback de la request
        :param params: Son los parámetros a añadir a la url de la request
        :return:
        e.g:
        TripAdvisorRequests.request('Search', callback = ..., params = {'q' : 'Blanca Navarra'})
        '''
        return Request(url = cls.get_resource_url(path, params) if url is None else url, callback = callback, **kwargs)



    @classmethod
    def splash_request(cls, callback, path = None, url = None, actions = None, params = None, **kwargs):
        '''
        Es igual que TripAdvisorRequests.request(...), pero ejecutando antes las acciones que se indican
        como parámetro.
        e.g:
        action = ElementReady('#first-element') + Click('#second-element') + Wait(1)
        TripAdvisorRequests.request(url = ..., callback = ..., actions = actions)

        Se hace una petición al recurso cuya url es la indicada. Cuando se obtiene la respuesta,
        se procesan las acciones especificadas: Se espera a que un elemento con el selector
        "#first-element'" aparezca en el DOM de la página, luego se clickea en "#second-element"
        y finalmente se espera 1 segundo.
        Depués se invoca el callback pasando como parámetro la respuesta de la request procesada.
        '''
        return splash_request(url = cls.get_resource_url(path, params) if url is None else url, callback = callback,
                              actions = actions, **kwargs)



    @classmethod
    def search_hotels_by_terms(cls, terms, callback):
        '''
        Instancia una request sobre una página de búsqueda de hoteles. (Busca hoteles por términos)
        :param terms: Es un texto que indica los términos de búsqueda
        :param callback:
        :return:
        Este método es un alias de
        TripAdvisorRequests.request('Search', params = {'q' : terms})
        '''
        return cls.request(path = 'Search', callback = callback, params = {'q' : terms})



    @classmethod
    def search_hotels_by_place(cls, place, callback):
        '''
        Instancia una request sobre la página principal de TripAdvisor para buscar hoteles
        indicando un lugar (país, provincia, ciudad, ...)
        :param callback:
        :param terms: Son los términos de búsqueda para encontrar hoteles
        :param place: Puede indicarse para afinar la búsqueda o restringirla a una ciudad, país,
        provincia, distrito, ...
        :return:
        '''
        actions = \
            SendText('input.typeahead_input', place) +\
            Click('#SUBMIT_HOTELS') +\
            Wait(5)
        #CHANGE LAST WAIT {TODO}

        return cls.splash_request(actions = actions, callback = callback, enable_iframe_sandbox = True)



    @classmethod
    def request_hotels_from_search_results(cls, callback, path = None, url = None, page_number = None):
        '''
        Instancia una request sobre una página de resultados de una búsqueda de hoteles en
        TripAdvisor. e.g:
        https://www.tripadvisor.com/Hotels-g187520-Pamplona_Navarra-Hotels.html
        :param path:
        :param url:
        :param callback:
        :param page_number: Si se especifica, se clickeará de forma automática sobre el panel
        de paginación, el botón con el número indicado para actualizar el DOM y que aparezcan

        los hoteles de dicha página
        :return:
        '''
        if page_number is None or page_number == 1:
            actions = ElementReady('div.pagination .pageNum.last')
        else:
            actions = Click('div.pagination .pageNum[data-page-number="{}"]'.format(page_number))
            actions += ElementReady('div.pagination .pageNum.current[data-page-number="{}"]'.format(page_number))

        return cls.splash_request(url = url, path = path, callback = callback, actions = actions, dont_filter = True)



    @classmethod
    def get_hotel_page(cls, fetch_deals = False, *args, **kwargs):
        '''
        Instancia una request a la página con la información de un hotel y sus reviews
        e.g:
        https://www.tripadvisor.com/Hotel_Review-g187520-d233664-Reviews-Hotel_Blanca_de_Navarra-Pamplona_Navarra.html
        :param fetch_deals Es un parámetro que si se establece a True, devuelve en el DOM de la
        página, las "deals" del hotel (la request usa splash para cargar contenido dinámico de
        la página)
        :return:
        '''
        use_splash = fetch_deals

        if use_splash:
            actions = ElementsReady([
                'div.premium_offers_area.viewDealChevrons'
            ])
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




