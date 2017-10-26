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
from  .spiders.tripadvisor_hotel_spider import TripAdvisorHotelSpider
import logging



class TripAdvisorPipelineJSON:
    '''
    Esta clase permite almacenar los datos escrapeados de TripAdvisor
    en ficheros JSON
    '''

    def __init__(self):
        self.feed_files = dict([(item_type, file.replace('..', join(dirname(__file__), 'data'))) for item_type, file in {
            'TripAdvisorHotelReview' : '../tripadvisor_reviews.json',
            'TripAdvisorHotelInfo' : '../tripadvisor_info.json',
            'TripAdvisorHotelDeals' : '../tripadvisor_deals.json',
            'TripAdvisorHotelGeolocation' : '../tripadvisor_geo.json',
            'Default' : '../items.json'
        }.items()])


    def get_feed_file(self, item):
        '''
        Devuelve la ruta del fichero donde se almacenará el item que se indica como
        parámetro
        :param item:
        :return:
        '''
        feed_file = (self.feed_files[item.__class__.__name__]
                     if item.__class__.__name__ in self.feed_files
                     else self.feed_files['Default'])
        return feed_file


    def open_spider(self, spider):
        if not isinstance(spider, TripAdvisorHotelSpider):
            return
        for file_path in self.feed_files.values():
            with open(file_path, 'wb') as fh:
                pass

    def close_spider(self, spider):
        if not isinstance(spider, TripAdvisorHotelSpider):
            return


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
            with open(self.get_feed_file(item), 'a') as item_file_handler:
                print(json.dumps(dict(item)), file = item_file_handler)

        return item




class TripAdvisorPipelineDB:
    '''
    Esta clase permite almacenar los items scrapeados de TripAdvisor en una base de datos
    sqlite.
    '''
    def open_spider(self, spider):
        if not isinstance(spider, TripAdvisorHotelSpider):
            return

        self.db = TripAdvisorDB()
        self.db.reset()


    def close_spider(self, spider):
        if not isinstance(spider, TripAdvisorHotelSpider):
            return
        self.db.close()


    def process_item(self, item, spider):
        '''
        Es invocado cuando un nuevo item se escrapea y debe almacenarse en la base de datos
        :param item:
        :param spider:
        :return:
        '''
        if not item is None and isinstance(spider, TripAdvisorHotelSpider):
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

        with TripAdvisorDB() as db:
            data = db.get_everything()
            with open(join(dirname(__file__), 'data', 'tripadvisor_bulk.json'), 'w') as fh:
                fh.write(json.dumps(data))

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        return item