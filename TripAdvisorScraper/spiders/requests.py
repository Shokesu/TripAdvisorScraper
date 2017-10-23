

from scrapy import Request
from urllib.parse import urlencode


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
    def request(cls, path, callback = None, params = None):
        '''
        Instancia una request para obtener el recurso sobre el endpoint indicado, dado los parámetros
        especificados.
        :param path:
        :param callback Será el callback de la request
        :param params: Son los parámetros a añadir a la url de la request
        :return:
        '''
        return Request(url = cls.get_resource_url(path, params), callback = callback)


    @classmethod
    def search_hotels_by_terms(cls, terms, callback):
        '''
        Instancia una request sobre una página de búsqueda de hoteles.
        :param terms: Es un texto que indica los términos de búsqueda
        :param callback:
        :return:
        '''
        return cls.request(path = 'Search', callback = callback, params = {'q' : terms})



    @classmethod
    def get_hotel_page(cls, *args, **kwargs):
        '''
        Instancia una request a la página con la información de un hotel y sus reviews
        :return:
        '''
        return cls.request(*args, **kwargs)