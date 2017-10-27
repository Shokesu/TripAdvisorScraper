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

'''
Este script define una serie de métodos y clases para ayudar a cargar contenido dinámico
de una página ejecutando javascript y usando el módulo splash.

El contenido dinámico puede obtenerse interactuando con el DOM de la página (como un usuario
normal) y realizando acciones sobre este (clickear o escribir en un elemento)

Se proveen las siguientes clases de utilidad, que representan posibles acciones en la página:

- Wait(x) : Para x segundos
- SendText(selector, text) : Escribe un texto a un elemento de tipo input indicando su selector 
- Click(selector) : Clickea en un elemento indicando su selector
- AllElementsReady([selector1, selector2, ...]) : Espera hasta que al menos un elemento que encaje
    con cada selector existan en el DOM de la página
- ElementReady(selector) = AllElementsReady([selector])


Ejemplo para crear un script:
actions = Wait(2) + Click('#first-element') + ElementReady('#new-element-appeared') +
    SendText('#first-element', 'New element appeared!')
    
Este script hace lo siguiente:
- Espera dos segundos
- clickea en el elemento con el selector "#first-element",
- Espera a que "#new-element-appeared" exista en el DOM
- Se envía el texto "New element appeared!" al elemento con el selector "#first-element"


Para ejecutar la request con el script...
yield splash_request(url = ..., callback = ..., actions = actions)

'''


from os.path import dirname, join
from scrapy_splash import SplashRequest






def stringify(values):
    '''
    Método de utilidad para convertir valores que serán hardcodeados dentro de trozos de
    código LUA o JS, a formato String (escapando los caracteres " y ' si los valores son strings)
    '''
    def _stringify(value):
        if value is None:
            return None
        if isinstance(value, str):
            return '"{}"'.format(value.replace('"', '\\"').replace("'", "\\'"))
        return str(value)

    if values is None:
        return None
    if not isinstance(values, list):
        value = values
        return _stringify(value)
    return [_stringify(value) for value in values]


class Code:
    '''
    Representa un trozo de código.
    '''
    def __init__(self, body = ''):
        self.body = str(body)

    def get_body(self):
        return self.body

    def __str__(self):
        return self.get_body()

    def __add__(self, other):
        '''
        Concatena dos trozos de código.
        :param other:
        :return:
        '''
        return Code('{}\n{}'.format(self.get_body(), other.get_body()))



class NoEscape(Code):
    '''
    Se usar para encapsular cadenas de caracteres que no deben ser escapadas (por ejemplo
    para indicar nombres de variables en el código JS o LUA)
    '''
    def __init__(self, something):
        self.something = something

    def __str__(self):
        return str(self.something)



class JSFunctionCode(Code):
    '''
    Representa el código de la definición de una clase en Javascript.
    '''
    def __init__(self, name, body = '', params = [], return_value = None):
        '''
        Inicializa la instancia
        :param name: Será el nombre del método
        :param body: Será el trozo de código dentro del método
        :param params: Un listado con los argumentos del método
        '''
        return_value = stringify(return_value)
        code = ('function {} ({}) {{\n' \
               '{}\n' \
               '}}').format(name, ', '.join([str(param) for param in params]),
                            body if return_value is None else '{}\nreturn {};'.format(body, return_value))
        super().__init__(code)



class JSFunctionCallCode(Code):
    '''
    Es una clase que representa una llamada a un método JS
    '''
    def __init__(self, name, args = []):
        '''
        Inicializa la instancia
        :param name: Es el nombre del método invocado
        :param args: Son los argumentos que deben indicarse.
        '''
        args = stringify(args)
        code = '{}({});'.format(name, ', '.join(args))
        super().__init__(code)


class JSObjectMethodCallCode(Code):
    '''
    Representa la llamada un método de clase en JS
    '''
    def __init__(self, object, method, args = []):
        '''
        Inicializa la instancia
        :param object: Es una instancia de una clase
        :param method: Es el nombre método de clase a invocar
        :param args: Son los argumentos que se indicarán en la llamada
        '''
        args = stringify(args)
        code = '{}.{}({});'.format(object, method, ', '.join(args))
        super().__init__(code)


class JSCodeWrapper:
    '''
    Esta clase permite encapsular código javascript para poder escribirlo en un script
    lua como una cadena de caracteres.
    '''
    def __init__(self, code):
        '''
        Inicializa la instancia
        :param code: Es el código a encapsular.
        '''
        self.wrapper = '[[{}]]'.format(code)

    def __str__(self):
        return self.wrapper


class LuaFunctionCode(Code):
    '''
    Representa la definición de un método en LUA
    '''
    def __init__(self, name, body = '', params = [], return_value = None):
        '''
        Inicializa la instancia
        :param name: Es el nombre del método
        :param body: Es el código del cuerpo del método.
        :param params: Son los argumentos que recibirá el método.
        '''
        return_value = stringify(return_value)
        code = ('function {} ({})\n' \
               '{}\n' \
               'end').format(name, ', '.join([str(param) for param in params]),
                             body if return_value is None else '{}\nreturn {}'.format(body, return_value))
        super().__init__(code)


class LuaObjectMethodCallCode(Code):
    '''
    Representa una llamada a un método de clase en LUA
    '''
    def __init__(self, object, method, args = [], surround_with_assert = True):
        '''
        Inicializa la instancia
        :param object: Es el nombre del objeto
        :param method: Es el nombre del método de clase
        :param args: Son los parámetros a indicar como argumentos-
        :param surround_with_assert: Si es True, la llamada se encapsulará en una sentencia
        del tipo assert(...)
        '''
        args = stringify(args)
        code = '{}:{}({})'.format(object, method, ', '.join(args))
        if surround_with_assert:
            code = 'assert({})'.format(code)

        super().__init__(code)



class SplashWaitForResumeCode(LuaObjectMethodCallCode):
    '''
    Permite generar una llamada al método de clase splash:wait_for_resume, pasandole como
    parámetro un código en JS
    '''
    def __init__(self, js_code, timeout = None):
        js_code = JSFunctionCode(name = 'main', params = ['splash'],
                                     body = js_code)
        js_snippet = JSCodeWrapper(js_code)

        args = [NoEscape(js_snippet)]
        if not timeout is None:
            args.append(timeout)

        super().__init__(object = 'splash', method = 'wait_for_resume', args = args)


class DOMEventListenerCode(SplashWaitForResumeCode):
    '''
    Esta clase se encarga de generar el código en LUA para un script con el objetivo de
    pausar la ejecución del mismo hasta que un evento en el DOM de la web ocurra.
    '''
    def __init__(self, selectors = [], timeout = None):
        self.selectors = stringify(selectors)


        callback_method_name = '__callback'
        registration_method_name = '__register'
        register_callback_code = self.get_register_callback_code(NoEscape(callback_method_name))

        js_code = JSFunctionCode(name = registration_method_name,
                                 body = register_callback_code) +\
                  JSFunctionCode(name = callback_method_name,
                                 body = JSObjectMethodCallCode(object = 'splash', method = 'resume')) +\
                  JSFunctionCallCode(name = registration_method_name)

        super().__init__(js_code, timeout)

    def get_selectors(self):
        return self.selectors

    def get_register_callback_code(self, callback_method_name):
        return ''




class ElementsReady(DOMEventListenerCode):
    '''
    Esta clase genera código para que la ejecución de un script se pausé y se resuma cuando un
    conjunto de elementos están disponibles en el DOM
    '''
    def __init__(self, selectors = []):
        '''
        Inicializa la instancia.
        :param selectors: Es un conjunto de selectores para jQuery
        Si el script ejecuta el código generado, la ejecución se pausará hasta que al menos un
        elemento que encaje con cada selector indicado esté disponible en el DOM
        '''
        super().__init__(selectors)

    def get_register_callback_code(self, callback_method_name):
        return JSFunctionCallCode(name = 'allElementsAvaliable',
                                  args = [NoEscape('[{}]'.format(', '.join(self.get_selectors()))), callback_method_name])


class ElementReady(ElementsReady):
    '''
    Es igual que ElementsReady, pero solo se especifica un selector.
    '''
    def __init__(self, selector):
        super().__init__([selector])



class InputElementHasValue(DOMEventListenerCode):
    '''
    Esta clase genera código para un script. Al ser ejecutado tal código, pausa la ejecución
    hasta que un elemento (de tipo input), tenga el valor indicado como parámetro.
    '''
    def __init__(self, selector, value):
        '''
        Inicializa la instancia.
        :param selector: Es el selector del elemento
        :param value: Es el valor que debe tener el elemento antes de que la ejecución del script
        se reaunde
        '''
        self.value = value
        super().__init__([selector])

    def get_value(self):
        return self.value

    def get_register_callback_code(self, callback_method_name):
        return JSFunctionCallCode(name = 'onInputHasValue',
                                  args = [NoEscape(self.get_selectors()[0]), self.get_value(), callback_method_name])



class Click(Code):
    '''
    Es una clase que sirve para generar código que de ser ejecutado, se simulará un click sobre
    un elemento del DOM. Después de ejecutar el código generado, se garantiza que se haya clickeado
    sobre el elemento indicado (en caso contrario, la ejecución queda pausada)
    '''
    def __init__(self, selector):
        '''
        Inicializa la instancia
        :param selector: Es el selector del elemento
        '''
        code = ElementReady(selector) +\
               LuaObjectMethodCallCode(object = LuaObjectMethodCallCode(object = 'splash', method = 'select', args = [selector]),
                                       method = 'mouse_click')
        super().__init__(code)


class SendText(Code):
    '''
    Es una clase que sirve para generar código que de ser ejecutado, escribe sobre un elemento del
    DOM (de tipo input)
    La ejecución queda pausada hasta garantizar que el elemento sobre el que se ha escrito, tiene
    el valor indicado como parámetro.
    '''
    def __init__(self, selector, text):
        '''
        Inicializa la instancia
        :param selector: Es el selector del elemento
        :param text: Es el texto ha escribir en el elemento
        '''
        code = ElementReady(selector) +\
               LuaObjectMethodCallCode(object = LuaObjectMethodCallCode(object = 'splash', method = 'select', args = [selector]),
                                       method = 'send_text', args = [text]) +\
               InputElementHasValue(selector = selector, value = text)

        super().__init__(code)


class Wait(Code):
    '''
    Clase que genera un código que para la ejecución del mismo al ejecutarse durante un periódo
    de tiempo específico.
    '''
    def __init__(self, amount):
        code = LuaObjectMethodCallCode(object = 'splash', method = 'wait', args = [amount])
        super().__init__(code)



class LuaSplashScript(Code):
    '''
    Genera un script en lua que ejecuta una serie de acciones sobre el DOM de la página que procesará,
    antes de servirla.
    e.g:
    actions = Click('#first-element') + SendText('#second-element', 'some-value')
    script = LuaSplashScript(actions)
    '''
    def __init__(self, actions = None):
        '''
        Inicializa la instancia.
        :param actions: Son las acciones a realizar por el script.
        '''

        if actions is None:
            actions = Code()

        main_method_body = LuaObjectMethodCallCode(object = 'splash', method = 'go', args = [NoEscape('splash.args.url')]) +\
                           LuaObjectMethodCallCode(object = 'splash', method = 'runjs', args = [NoEscape('splash.args.jquery')]) + \
                           LuaObjectMethodCallCode(object = 'splash', method = 'runjs', args = [NoEscape('splash.args.scrap_utils')]) +\
                           actions

        code = LuaFunctionCode(name = 'main', params = ['splash'],
                               body = main_method_body,
                               return_value = LuaObjectMethodCallCode(object = 'splash', method = 'html', surround_with_assert = False))

        # Formatear las cadenas de caracteres.

        super().__init__(code)


def splash_request(url, callback, actions = None):
    '''
    Realiza una petición a la página cuya url se indica como parámetro y devuelve una instancia
    de la clase Request como valor de retorno.
    Pero antes de servir la página, pueden ejecutarse una serie de acciones como un usuario:
    clickear en un elemento, escribir en un input, ... e.t.c
    Se genera un script en LUA a partir de una secuencia de acciones, que a su vez ejecuta JS
    para interactuar con el DOM.

    e.g:
        splash_request('https://google.com', callback = parse,
        actions = Click('#search-bar') + SendText('#search-bar', 'Why pigs dont fly?'))

    :param url: Es la url de la página
    :param callback: Es un callback que scrapeará la página
    :param actions: Es un listado de acciones a realizar antes de servir la página. Permite crear
    un usuario virtual que pueda interactuar con la web para cargar contenido dinámico.
    '''

    def read_js_script(path):
        with open(join(dirname(dirname(__file__)), 'static', 'js', path)) as fh:
            return fh.read()

    code = LuaSplashScript(actions)

    return SplashRequest(callback=callback,
                         endpoint='execute',
                         args={
                             'lua_source': str(code),
                             'url': url,
                             'scrap_utils': read_js_script('scrap_utils.js'),
                             'jquery': read_js_script('jquery.min.js')
                         })