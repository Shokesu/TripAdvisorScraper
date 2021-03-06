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



from os.path import join, dirname
import json
from .item_db import TripAdvisorDB
from .spiders.tripadvisor_hotel_spider import TripAdvisorHotelSpider
from TripAdvisorScraper.config.config import GlobalConfig
import logging



class TripAdvisorPipelineJSON:
    '''
    Esta clase permite almacenar los datos escrapeados de TripAdvisor
    en ficheros JSON
    '''

    def __init__(self):
        config = GlobalConfig()
        self.files = {
            'TripAdvisorHotelReview' : config.get_path('OUTPUT_REVIEWS_JSON'),
            'TripAdvisorHotelInfo' : config.get_path('OUTPUT_HOTEL_INFO_JSON'),
            'TripAdvisorHotelDeals' : config.get_path('OUTPUT_DEALS_JSON'),
            'TripAdvisorHotelGeolocation' : config.get_path('OUTPUT_GEO_JSON')
        }


    def get_file(self, item):
        '''
        Devuelve la ruta del fichero donde se almacenará el item que se indica como
        parámetro
        :param item:
        :return:
        '''
        feed_file = (self.files[item.__class__.__name__]
                     if item.__class__.__name__ in self.files
                     else None)
        return feed_file


    def open_spider(self, spider):
        if not isinstance(spider, TripAdvisorHotelSpider):
            return
        for file_path in self.files.values():
            if not file_path is None:
                try:
                    with open(file_path, 'wb'):
                        pass
                except:
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
        if not item is None and isinstance(spider, TripAdvisorHotelSpider):
            file = self.get_file(item)
            if not file is None:
                try:
                    with open(file, 'a') as item_file_handler:
                        print(json.dumps(dict(item)), file = item_file_handler)
                except:
                    pass
        return item




class TripAdvisorPipelineDB:
    '''
    Esta clase permite almacenar los items scrapeados de TripAdvisor en una base de datos
    sqlite.
    '''
    def open_spider(self, spider):
        if not isinstance(spider, TripAdvisorHotelSpider):
            return

        db_path = GlobalConfig().get_path('OUTPUT_SQLITE')
        try:
            if db_path is None:
                raise Exception()
            self.db = TripAdvisorDB(db_path)
            self.db.reset()
        except:
            self.db = None


    def close_spider(self, spider):
        if not isinstance(spider, TripAdvisorHotelSpider):
            return
        if not self.db is None:
            self.db.close()


    def process_item(self, item, spider):
        '''
        Es invocado cuando un nuevo item se escrapea y debe almacenarse en la base de datos
        :param item:
        :param spider:
        :return:
        '''
        if not item is None and isinstance(spider, TripAdvisorHotelSpider) and not self.db is None:
            self.db.save_item(item)

        return item


class TripAdvisorPipelineBulkJSON:
    '''
    Es un pipeline especial que sirve para almacenar los items scrapeados en un único fichero JSON.
    Los datos tendrán la siguiente estructura:
    [
        {
            'info' : {
                'name' : ...
                'phone_number' : ...
                'amenities' : ...
                'address' : ...
                'geo' : {
                    'latitude' : ...
                    'longitude' : ...
                }
            },
            'deals' : {
                'provider_name' : ...
                'price' : ...
            },
            'reviews' : {
                'title' : ...
                'text' : ...
                'rating' : ...
                'date' : ...
            }
        }
    ]

    El fichero JSON se generará cuando se hayan scrapeado todos los datos.
    '''
    def close_spider(self, spider):
        if not isinstance(spider, TripAdvisorHotelSpider):
            return

        config = GlobalConfig()
        db_path = config.get_path('OUTPUT_SQLITE')
        file_path = config.get_path('OUTPUT_BULK_JSON')
        if not db_path is None and not file_path is None:
            try:
                with TripAdvisorDB(db_path) as db:
                    data = db.get_everything()
                    with open(file_path, 'w') as fh:
                        fh.write(json.dumps(data))
            except:
                pass

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        return item