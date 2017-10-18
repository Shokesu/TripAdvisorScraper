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

class TripAdvisorHotelSpider(Spider):
    # URL Raíz de TripAdvisor
    url_root = 'https://www.tripadvisor.com'

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
        # Construimos una URL para buscar el hotel.
        url = self.build_hotel_search_query(self.query)

        yield Request(url, self.parse_hotel_search)



    def build_hotel_search_query(self, terms):
        '''
        Construye la url que devuelve una página de búsqueda donde se buscan los términos que
        se indican como parámetro
        :param terms:
        :return:
        '''
        url = '{}/Search?{}'.format(self.url_root, urlencode({'q': terms}))
        return url


    def parse_hotel_search(self, response):
        '''
        Parsea el resultado de una búsqueda en TripAdvisor. En caso de que la búsqueda tenga
        algún resultado, obtiene el primer resultado y genera una nueva request para
        scrapear los datos del hotel asociado (se invoca como callback el método parse_hotel)
        '''

        try:
            self.log.debug('Parsing hotel search')
            result = response.css('div.info.poi-info div.title::attr(onclick)')
            if len(result) == 0:
                raise ValueError()
            result =  result.re('\([ ]*\'[^\']*\'[ ]*,[ ]*\'[^\']*\'[ ]*,[ ]*\'[^\']*\'[ ]*,[ ]*[^\,]*[ ]*,[ ]*\'\/([^\']+)\'')

            if len(result) == 0:
                raise ValueError()

            # Obtenemos la URL del hotel
            hotel_url = '{}/{}'.format(self.url_root, result[0])
            self.log.debug('Search was succesful. Hotel info at {}'.format(hotel_url))

            # Parseamos información y reviews del hotel
            yield Request(hotel_url, self.parse_hotel)


        except ValueError:
            raise ValueError('No hotel found with the search terms: {}'.format(self.query))

    def parse_hotel(self, response):
        '''
        Parsea una request a la página con información de un hotel en TripAdvisor, obtiene sus
        datos y sus reviews.
        :param response:
        :return:
        '''

        return chain(self.parse_hotel_info(response), self.parse_hotel_reviews(response),
                     self.parse_near_hotels(response))


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
            review_selector = response.css('div.listContainer')
            review_selector = review_selector.xpath(
                './/div[contains(@class, "review-container")][{}]'.format(i+1))

            loader = ItemLoader(item = TripAdvisorHotelReview(), selector = review_selector)
            loader.add_css('title', 'span.noQuotes::text')
            loader.add_css('text', 'div.prw_reviews_text_summary_hsx p.partial_entry::text')
            loader.add_css('rating', 'span.ui_bubble_rating', re='class="[^\"]*bubble_(\d+)[^\"]*"')
            loader.add_value('hotel_id', hotel_id)

            loader.load_item()
            yield loader.item

        review_offset = int(response.css('div.listContainer p.pagination-details').xpath('.//b[1]//text()').extract_first()) - 1
        self.log.debug('Succesfully extracted {} reviews from offset {} to {}'.format(num_reviews, review_offset, review_offset + num_reviews - 1))


        # Procesamos las reviews de la siguiente página.


        if len(response.css('div.pagination').xpath('.//span[contains(@class, "next") and not(contains(@class, "disabled"))]')) > 0:
            review_offset = response.css('div.pagination span.next::attr(data-offset)').extract_first()
            self.log.debug('Processing next review\'s section page, with offset = {}'.format(review_offset))

            next_page_url = '{}{}{}'.format(url_match_result.group(1),
                                            'or{}-'.format(review_offset),
                                            url_match_result.group(3))
            # Realizamos la request a la siguiente página.
            yield Request(url = next_page_url, callback = self.parse_hotel_reviews)

        else:
            self.log.debug('All reviews have been extracted. Last review offset was: {}'.format(review_offset + num_reviews - 1))


    def parse_near_hotels(self, response):
        '''
        Este método analiza de la página de un hotel de TripAdvisor, los hoteles más cercanos a este y
        los scrapea
        :param response:
        :return:
        '''
        self.log.debug('Searching for nearby hotels')
        nearby_hotels = response.css('div.prw_common_btf_nearby_poi_grid.hotel div.poiInfo div.poiName::text').extract()
        self.log.debug('Founded {} nearby hotels: {}'.format(len(nearby_hotels), ', '.join(nearby_hotels)))

        # Lanzamos requests para screapear hoteles cercanos a este también...
        for nearby_hotel in nearby_hotels:
            search_terms = nearby_hotel
            yield Request(self.build_hotel_search_query(search_terms), self.parse_hotel_search)

