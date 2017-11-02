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

from copy import copy
from os.path import dirname, join, normpath, basename
import importlib.util
from re import match
import inspect, sys

class Config:
    '''
    Esta clase representa una configuración para el scraper.
    '''
    def __init__(self, vars = {}):
        '''
        Inicializa la instancia.
        :param vars: Es un diccionario donde los claves son los nombres de las variables,
        y los valores, los valores de cada una de ellas.
        :param root_path: Es un parámetro opcional que indica ruta raíz para procesar las
        rutas relativas especificadas en las variables de configuración. Por defecto es
        el directorio padre de este script
        '''
        self.vars = copy(vars)

    def get_value(self, var, default = None):
        '''
        Devuelve el valor de la variable cuyo nombre se indica como parámetro.
        :param default: Es el valor por defecto que se devolverá como salida si la variable no
        se ha establecido en la configuración, por defecto None
        '''
        return self.vars[var] if var in self.vars else default


    def has_value(self, var, value):
        '''
        Comprueba si una variable de configuración tiene el valor indicado como parámetro.
        has_value('var', None) devuelve True si la variable 'var' es None o bien no se ha
        establecido.

        :param var:
        :param value:
        :return:
        '''
        return self.get_value(var) == value


    def is_set(self, var):
        '''
        Comprueba si una variable configuración se ha establecido.
        :param var:
        :return:
        '''
        return var in self.vars


    def set_value(self, var, value = None):
        '''
        Establece el valor de una variable de configuración.
        :param var: Es el nobmre de la variable.
        :param value: Es el nuevo valor de la variable. (Por defecto es None)
        '''
        self.vars[var] = value

    def is_true(self, var):
        '''
        Es igual que has_value(var, True)
        :param var:
        :return:
        '''
        return self.has_value(var, True)


    def get_path(self, var, default = None):
        '''
        Devuelve la variable indicada como parámetro (ruta a un fichero) normalizada (se procesan
        rutas relativas)
        :param var:
        :param default:
        :return:
        '''
        value = self.get_value(var)
        if value is None or not isinstance(value, (str, Path)):
            return default
        return normpath(str(value))


    @staticmethod
    def load_from_file(file):
        '''
        Carga la configuración desde un fichero.
        :param file: Es la ruta del fichero de configuración absoluta o relativa al directorio
        padre de este script.
        :return: Devuelve una instancia de la clase Config.
        '''
        try:
            location = file
            config_module_name = match('^([^\.]+)(\..*)?$', basename(location)).group(1)

            spec = importlib.util.spec_from_file_location('config.{}'.format(config_module_name), location)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            return Config(dict([(key, value) for key, value in config_module.__dict__.items() if not match('^__.*__$', key)]))
        except:
            raise Exception('Failed to load configuration from file')



    def override(self, other):
        '''
        Sobrecarga otra configuración con esta. Los valores de las variables en la nueva configuración,
        sustituyen a los valores de esta configuración.
        :param other: Otra configuración (Instancia de la clase Config)
        :return:
        '''
        self.vars.update(other.vars)


    def check(self):
        '''
        Valida la configuración actual. Si la configuración actual no es válida, genera una
        excepción
        :return:
        '''
        try:
            if not (self.is_set('SEARCH_BY_TERMS') != self.is_set('SEARCH_BY_LOCATION')):
                raise Exception('You must specify "{}" or "{}", but not both or no one'.format(
                    'SEARCH_BY_TERMS', 'SEARCH_BY_LOCATION'
                ))

            if self.is_true('SCRAP_GEO') and not self.is_set('GOOGLE_MAPS_API_KEY'):
                raise Exception('You must specify a valid Google Maps API Key to scrap hotel\'s geolocation info')

        except Exception as e:
            raise ValueError('Configuration is not valid: {}'.format(str(e)))

    def __str__(self):
        return str(self.vars)




class DefaultConfig:
    '''
    Es la configuración por defecto del scraper. Usa el patrón singleton.
    La configuración por defecto esta en el fichero "default.conf.py" en este mismo directorio.
    '''

    class __Singleton(Config):
        def __init__(self):
            super().__init__()
            self.override(Config.load_from_file(join(dirname(__file__), 'default.conf.py')))

    singleton = None
    def __init__(self):
        if DefaultConfig.singleton is None:
            DefaultConfig.singleton = DefaultConfig.__Singleton()

    def __getattr__(self, item):
        return getattr(DefaultConfig.singleton, item)

    def __str__(self):
        return str(DefaultConfig.singleton)


class GlobalConfig:
    '''
    Esta clase representa la configuración global del scraper.
    Usa el patrón singleton.
    '''

    class __Singleton(Config):
        def __init__(self):
            super().__init__()
            self.override(DefaultConfig())


    singleton = None
    def __init__(self):
        if GlobalConfig.singleton is None:
            GlobalConfig.singleton = GlobalConfig.__Singleton()

    def __getattr__(self, item):
        return getattr(GlobalConfig.singleton, item)

    def __str__(self):
        return str(GlobalConfig.singleton)


class Path:
    '''
    Esta clase se usa para configurar rutas a ficheros en las variables de configuración.
    '''
    def __init__(self, file):
        root_path = dirname(inspect.getfile(sys._getframe(1)))
        self.path = normpath(join(root_path, file))

    def get_path(self):
        return self.path

    def __str__(self):
        return self.get_path()