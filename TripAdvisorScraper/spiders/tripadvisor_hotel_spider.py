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

import scrapy
from scrapy import Spider, Request
from scrapy_splash import SplashRequest
from scrapy.loader import ItemLoader
from urllib.parse import urlencode
from scrapy.selector import Selector
from itertools import chain
from hashlib import sha256
from re import match
from TripAdvisorScraper.items import TripAdvisorHotelInfo, TripAdvisorHotelReview
import logging
from os.path import dirname, join
from datetime import datetime
from .requests import *

class TripAdvisorHotelSpider(Spider):
    # Nombre de nuestra araña
    name = 'TripAdvisorHotelSpider'



    def __init__(self, q):
        '''
        Inicializa esta instancia.
        :param: q Es la query para buscar el hotel a scrapear (sin codificiar)
        '''
        super().__init__()

        self.query = q

        log_file_path = join(dirname(dirname(__file__)), 'log', 'tripadvisor_hotels.log')
        log_file_handler = logging.FileHandler(log_file_path)
        self.log = logging.getLogger(__name__)
        self.log.addHandler(log_file_handler)



    def start_requests(self):
        '''
        Este método es invocado cuando la araña empieza ha hacer las
        requests.
        :return: Devuelve un generador, que genera instancias de la
        clase scrapy.Request
        '''
        yield TripAdvisorRequests.search_hotels_by_terms(terms = self.query, callback = self.parse_hotel_search)


    def parse_hotel_search(self, response):
        '''
        Parsea el resultado de una búsqueda en TripAdvisor. Por cada resultado (hotel encontrado)
        genera una nueva request.
        '''

        try:
            self.log.debug('Parsing hotel search')
            result = response.css('div.info.poi-info div.title::attr(onclick)')
            if len(result) == 0:
                raise ValueError()
            result =  result.re('\([ ]*\'[^\']*\'[ ]*,[ ]*\'[^\']*\'[ ]*,[ ]*\'[^\']*\'[ ]*,[ ]*[^\,]*[ ]*,[ ]*\'\/([^\']+)\'')

            if len(result) == 0:
                raise ValueError()

            for entry in result:
                path, params = match('^(.*)\?(.*)$', entry).groups()

                # Obtenemos la URL del hotel
                self.log.debug('Search was succesful. Hotel info at {}'.format(TripAdvisorRequests.get_resource_url(path)))

                # Parseamos información y reviews del hotel
                yield TripAdvisorRequests.get_hotel_page(path = path, params = params, callback = self.parse_hotel)

        except ValueError:
            raise ValueError('No hotel found with the search terms: {}'.format(self.query))

        # Parseamos la siguiente página de resultados


    def parse_hotel(self, response):
        '''
        Parsea una request a la página con información de un hotel en TripAdvisor, obtiene sus
        datos y sus reviews.
        :param response:
        :return:
        '''

        return chain(self.parse_hotel_info(response), self.parse_hotel_reviews(response),


    def parse_hotel_info(self, response):
        '''
        Parsea la información de un hotel en TripAdvisor
        :return:
        '''
        loader = ItemLoader(item=TripAdvisorHotelInfo(), response=response)

        loader.add_css('name', '#HEADING::text')
        loader.add_css('phone_number', 'div.phone span:not(.ui_icon)::text')
        loader.add_css('amenities', 'div.amenitiesColumn div.detailsMid div.highlightedAmenity::text', re = '^[ ]*(.+)[ ]*$')

        loader.add_css('address', 'div.address span.street-address::text', re = '^[ ]*(.+)[ ]*$')
        loader.add_css('address', 'div.address span.locality::text', re = '^[ ]*(.+),[ ]*$')
        loader.add_css('address', 'div.address span.country-name::text', re = '^[ ]*(.+)[ ]*$')

        hasher = sha256()
        hasher.update(response.url.encode())
        loader.add_value('id', hasher.hexdigest())

        loader.load_item()

        self.log.debug('Succesfully info extracted from "{}" hotel'.format(loader.item['name']))

        yield loader.item


    def parse_hotel_reviews(self, response):
        '''
        Parsea las reviews de un hotel.
        :param response:
        :return:
        '''
        url_match_result = match(('^(.*\/{})(or\d+\-)?(.*)$'.format('{0}' * 4)).format('[^-]+\-'), response.url)
        url = url_match_result.group(1) + url_match_result.group(3)

        hasher = sha256()
        hasher.update(url.encode())
        hasher.hexdigest()
        hotel_id = hasher.hexdigest()

        # Procesamos las reviews de la página
        num_reviews = len(response.css('div.listContainer div.review-container').extract())
        for i in range(0, num_reviews):
            try:
                review_selector = response.css('div.listContainer')
                review_selector = review_selector.xpath(
                    './/div[contains(@class, "review-container")][{}]'.format(i+1))

                loader = ItemLoader(item = TripAdvisorHotelReview(), selector = review_selector)
                loader.add_css('title', 'span.noQuotes::text')
                loader.add_css('text', 'div.prw_reviews_text_summary_hsx p.partial_entry::text')
                loader.add_css('rating', 'span.ui_bubble_rating', re='class="[^\"]*bubble_(\d+)[^\"]*"')
                loader.add_value('hotel_id', hotel_id)

                date = review_selector.css('span.ratingDate::attr(title)').extract_first()
                result = match('^[ ]*([^ ]+)[ ]+(\d+)[ ]*\,[ ]*([^ ]+)[ ]*$', date)
                month_str, day, year = result.groups()
                month_str = month_str.lower()
                month = dict(zip(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                  'september', 'october', 'november', 'december'], range(0, 12)))[month_str]

                loader.add_value('date', datetime(year = int(year), month = month, day = int(day)).date().isoformat())



                loader.load_item()
                yield loader.item
            except:
                pass

        review_offset = int(response.css('div.listContainer p.pagination-details').xpath('.//b[1]//text()').extract_first()) - 1
        self.log.debug('Succesfully extracted {} reviews from offset {} to {}'.format(num_reviews, review_offset, review_offset + num_reviews - 1))


        # Procesamos las reviews de la siguiente página.


        if len(response.css('div.pagination').xpath('.//span[contains(@class, "next") and not(contains(@class, "disabled"))]')) > 0:
            review_offset = response.css('div.pagination span.next::attr(data-offset)').extract_first()
            self.log.debug('Processing next review\'s section page, with offset = {}'.format(review_offset))

            next_page_url = '{}{}{}'.format(url_match_result.group(1),
                                            'or{}-'.format(review_offset),
                                            url_match_result.group(3))
            result = match('^https?\:\/\/[^\/]+\/([^\?]+)(\?(.*))?$', next_page_url)
            path = result.group(1)
            params = result.group(3)

            # Realizamos la request a la siguiente página.
            yield TripAdvisorRequests.get_hotel_page(path = path, params = params, callback = self.parse_hotel_reviews)

        else:
            self.log.debug('All reviews have been extracted. Last review offset was: {}'.format(review_offset + num_reviews - 1))

