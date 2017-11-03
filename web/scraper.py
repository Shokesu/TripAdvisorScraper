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
Script de utilidad que facilita la interacción del backend del cliente web con
el scraper de TripAdvisor.
'''


from TripAdvisorScraper.crawl import crawl
from os.path import join, dirname
from multiprocessing import Process, Queue, Lock



class TripAdvisorScraper:
    '''
    Esta clase se encarga de ejecutar el scraper de TripAdvisor.
    Esta clase usa el patrón Singleton
    '''
    class __Singleton:
        def __init__(self):
            self.lock = Lock()
            self.current_search_location = None

        def search_by_location(self, location):
            '''
            Este método comienza a ejecutar el scraper de TripAdvisor,
            buscando hoteles por localización.
            Solo puede haber una instancia del scraper ejecutandose
            de forma simultánea.
            Si hay una instancia del scraper ejecutandose ya, este método
            finaliza al instante devolviendo el valor False.
            En caso contrario, el método NO queda bloqueado y devuelve True e inicia
            la ejecución del scraper en un proceso a parte.
            Posteriormente, podrá invocarse search_finished para comprobar si el scraper
            finalizó o no.
            :param location:
            :return:
            '''
            def __crawl(location):
                args = [
                    '--config={}'.format(join(dirname(__file__), 'scraper.conf.py')),
                    '--search-by-location=\"{}\"'.format(location)
                ]
                crawl(*args)

            def worker(lock, location):
                __crawl(location)
                lock.release()

            self.current_search_location = location
            if self.lock.acquire(False):
                queue = Queue()
                process = Process(target=worker, args=(self.lock, location))
                process.start()
                return True
            return False


        def is_running(self):
            '''
            Este método devuelve True si el scraper de TripAdvisor este ejecutandose.
            :return:
            '''
            if self.lock.acquire(False):
                self.lock.release()
                return False
            return True


        def get_current_search_info(self):
            '''
            :return: Devuelve un diccionario con información sobre el estado actual
            del scraper en ejecución. Debe haberse invocado el método search_by_location
            antes de llamar a esta función.
            '''
            return {
                'current_search_location' : self.current_search_location
            }

    instance = None
    def __init__(self):
        if TripAdvisorScraper.instance is None:
            TripAdvisorScraper.instance = TripAdvisorScraper.__Singleton()

    def __getattr__(self, item):
        return getattr(TripAdvisorScraper.instance, item)