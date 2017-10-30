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

import sqlite3
from os.path import dirname, join
from TripAdvisorScraper.logger import Logger
from TripAdvisorScraper.config.config import GlobalConfig

class TripAdvisorDB(Logger):
    '''
    Esta clase se encarga de gestionar la base de datos sqlite3 en la que se almacenan
    los items scrapeados de Trip Advisor.
    '''
    def __init__(self):
        '''
        Inicializa la instancia. En el constructor se abre la conexión con la base de
        datos.
        '''

        Logger.__init__(self, GlobalConfig().get_path('OUTPUT_SQLITE_LOG'))

        self.log.debug('Connecting to TripAdvisor sqlite database...')
        self.db = sqlite3.connect(join(dirname(__file__), 'data', 'tripadvisor.db'))

        self.item_handlers = {
            'TripAdvisorHotelReview': lambda item:self.insert_item(item, 'hotel_review'),
            'TripAdvisorHotelInfo': lambda item:self.insert_item(item, 'hotel_info'),
            'TripAdvisorHotelDeals': lambda item:self.insert_item(item, 'hotel_deal'),
            'TripAdvisorHotelGeolocation': lambda item:self.insert_item(item, 'hotel_geo')
            }

    def __getattr__(self, item):
        return getattr(self.db, item)


    def execute(self, query, params):
        self.log.debug('Executing SQL:\n{}\nWith this params: {}\n'.format(query, ', '.join(["'{}:{}'".format(type(param).__name__, str(param)) for param in params])))
        self.db.execute(query, params)

    def executescript(self, sql_script, *args, **kwargs):
        self.log.debug('Executing SQL:\n{}\n'.format(sql_script))
        self.db.executescript(sql_script, *args, **kwargs)

    def _drop_tables(self):
        '''
        Elimina todas las tablas de la base de datos.
        :return:
        '''
        self.executescript(
            """
            DROP TABLE IF EXISTS hotel_deal;
            DROP TABLE IF EXISTS hotel_review;
            DROP TABLE IF EXISTS hotel_geo;
            DROP TABLE IF EXISTS hotel_info;
            """
        )
        self.commit()

    def _create_tables(self):
        '''
        Crea todas las tablas para almacenar los items en la base de datos.
        :return:
        '''
        self.executescript(
            """
            CREATE TABLE hotel_info (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                amenities TEXT,
                phone_number TEXT
            );
            CREATE TABLE hotel_geo (
                hotel_id TEXT PRIMARY KEY,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                FOREIGN KEY (hotel_id) REFERENCES hotel_info(id)
            );
            CREATE TABLE hotel_review (
                hotel_id TEXT NOT NULL,
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                rating INT NOT NULL,
                text TEXT NOT NULL,
                date TEXT NOT NULL,
                UNIQUE(hotel_id, review_id),
                FOREIGN KEY (hotel_id) REFERENCES hotel_info(id)
            );
            CREATE TABLE hotel_deal (
                hotel_id TEXT NOT NULL,
                deal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_name TEXT NOT NULL,
                price INT NOT NULL,
                UNIQUE(hotel_id, deal_id),
                FOREIGN KEY (hotel_id) REFERENCES hotel_info(id)
            );
            """)
        self.commit()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()
        return False

    def close(self):
        '''
        Este método cierra la conexión con la base de datos.
        :return:
        '''
        self.log.debug('Shutting down sqlite connection database...')
        self.db.close()

    def reset(self):
        '''
        Este método recrea todas las tablas de la base de datos necesarias para almacenar
        la información de los items. (Se pierde toda la información)
        :return:
        '''
        self._drop_tables()
        self._create_tables()

    def insert_item(self, item, table_name):
        field_names = [field_name for field_name in item.fields.keys() if not item.get(field_name) is None]
        field_values = [item.get(field_name) for field_name in field_names]
        self.execute(
            'INSERT INTO {} ({}) VALUES ({});'.format(
                table_name,
                ', '.join(['"{}"'.format(field_name) for field_name in field_names]),
                ', '.join(['?'] * len(field_names))),
            field_values)
        self.commit()


    def save_item(self, item):
        '''
        Almacena un item en la base de datos.
        :param item:
        :return:
        '''
        if not item is None and item.__class__.__name__ in self.item_handlers:
            handler = self.item_handlers[item.__class__.__name__]
            handler(item)


    def get_everything(self):
        cursor = self.cursor()
        def fetch_all(query, attrs, params = None):
            query = query.format(', '.join(attrs))
            if not params is None:
                cursor.execute(query, tuple(params))
            else:
                cursor.execute(query)

            data = []
            for register in cursor.fetchall():
                data.append(dict(zip(attrs, register)))
            return data

        def fetch_one(query, attrs, params = None):
            registers = fetch_all(query, attrs, params)
            return registers[0]



        def get_hotel_info(hotel_id):
            return fetch_one(query = 'SELECT {} FROM hotel_info WHERE id = ?;',
                             attrs = ['name', 'phone_number', 'amenities', 'address'],
                             params = [hotel_id])


        def get_hotel_reviews(hotel_id):
            return fetch_all(query = 'SELECT {} FROM hotel_review WHERE hotel_id = ?;',
                             attrs = ['title', 'rating', 'text', 'date'],
                             params = [hotel_id])

        def get_hotel_deals(hotel_id):
            return fetch_all(query = 'SELECT {} FROM hotel_deal WHERE hotel_id = ?;',
                             attrs = ['provider_name', 'price'],
                             params = [hotel_id])

        def get_hotel_geo(hotel_id):
            return fetch_one(query = 'SELECT {} FROM hotel_geo WHERE hotel_id = ?;',
                             attrs = ['latitude', 'longitude'],
                             params = [hotel_id])

        def get_hotel_ids():
            registers = fetch_all(query = 'SELECT {} FROM hotel_info;', attrs = ['id'])
            hotel_ids = [register['id'] for register in registers]
            return hotel_ids

        data = []
        hotel_ids = get_hotel_ids()
        for hotel_id in hotel_ids:
            hotel_info = get_hotel_info(hotel_id)
            hotel_deals = get_hotel_deals(hotel_id)
            hotel_reviews = get_hotel_reviews(hotel_id)
            self.log.debug('Num reviews: {}'.format(len(hotel_reviews)))

            hotel_data = {
                'info' : hotel_info,
                'reviews' : hotel_reviews,
                'deals' : hotel_deals
            }
            hotel_data['info']['geo'] = get_hotel_geo(hotel_id)
            data.append(hotel_data)
        return data