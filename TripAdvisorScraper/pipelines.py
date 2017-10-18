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



from TripAdvisorScraper.items import *

from os.path import join, dirname
import json


class TripAdvisorPipelineJSON:
    '''
    Esta clase permite almacenar los datos escrapeados de TripAdvisor
    en ficheros JSON
    '''

    def __init__(self):
        pass

    def get_feed_file_for_item(self, item):
        '''
        Este método devuelve la ruta del fichero donde debe almacenarse el item
        que se indica como parámetro.
        :param item:
        :return:
        '''
        feed_files_dir = join(dirname(__file__), 'data')

        if isinstance(item, TripAdvisorHotelReview):
            return join(feed_files_dir, 'tripadvisor_reviews.json')
        elif isinstance(item, TripAdvisorHotelInfo):
            return join(feed_files_dir, 'tripadvisor_hotels_info.json')
        return join(feed_files_dir, 'items.json')



    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        '''
        Es invocado cuando un nuevo item se escrapea y debe almacenarse en su fichero
        JSON correspondiente.
        :param item:
        :param spider:
        :return:
        '''
        # Almacenamos el item en su fichero correspondiente
        with open(self.get_feed_file_for_item(item), 'a') as item_file_handler:
            print(json.dumps(dict(item)), file = item_file_handler)