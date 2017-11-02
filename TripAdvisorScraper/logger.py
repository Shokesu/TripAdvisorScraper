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

import logging
from TripAdvisorScraper.config.config import GlobalConfig

class Logger:
    '''
    Esta clase permite imprimir mensajes a un fichero de log
    Las clases que extiendan de esta tendrán los métodos de la clase
    logging.Logger disponibles.
    e.g:
    class Foo(Logger):
        def __init__(self):
            super().__init__(file_path = ...)


    f = Foo()
    f.debug('....')

    El logger comprobará la variable de configuración global "ENABLE_DEBUG".
    Si esta activa, los mensajes de depuración se imprimirán en los ficheros de log.
    En caso contario, los métodos debug(), info(), warning(), ..., serán ignorados.
    '''

    def __init__(self, file_path):
        self.log = logging.getLogger(file_path)
        self.log.setLevel(logging.DEBUG)

        self.log.propagate = GlobalConfig().is_true('ENABLE_DEBUG') and GlobalConfig().is_true('OUTPUT_DEBUG_INFO_TO_STDOUT')

        if GlobalConfig().is_true('ENABLE_DEBUG'):
            try:
                log_file_handler = logging.FileHandler(file_path)
                self.log.addHandler(log_file_handler)
            except:
                pass

    def __getattr__(self, item):
        return getattr(self.log, item)