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
Este script se encarga de ejecutar el scraper de TripAdvisor, leer los ficheros de configuración
y procesa los argumentos por línea de comandos.
'''

from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.project import get_project_settings
from TripAdvisorScraper.spiders.tripadvisor_hotel_spider import TripAdvisorHotelSpider
from TripAdvisorScraper.config.config import GlobalConfig, Config
import argparse
from os import getcwd
from os.path import join, dirname, normpath, abspath

def crawl(*args):
    '''
    Este método inicia la ejecución del scraper de TripAdvisor y no retorna hasta que finaliza.
    :param args: Son las opciones que serán pasados al scraper de TripAdvisor
    e.g: crawl('--option1', '--option2=sdsd')
    :return:
    Para ver todas las opciones, ejecutar este módulo como script y escribir la opción -h
    '''

    # Parseamos los argumentos
    parser = argparse.ArgumentParser(prog = 'TripAdvisorScraper', description = 'Scraper de TripAdvisor')

    parser.add_argument('--config', nargs = '?', type=str,
                        help = 'Path to the file configuration of the scraper, relative to the current working directory or absolute path',
                        metavar = '<CONFIG FILE>',
                        dest = 'config_file')
    parser.add_argument('--search-by-terms', nargs = '+', type=str,
                        help = 'Search TripAdvisor hotels by terms',
                        metavar = 'term',
                        dest = 'terms')
    parser.add_argument('--search-by-location', nargs = '+', type=str,
                        help = 'Search TripAdvisor hotels by location (country, district, city, ...)',
                        metavar = 'location',
                        dest = 'locations')


    parser.add_argument('--debug', nargs='?',type=str,
                        help = 'Enable/Disable hotel\'s reviews scraping',
                        metavar = '<yes/no>',
                        dest = 'debug',
                        const = 'yes',
                        default = None,
                        action = 'store')

    parser.add_argument('--reviews', nargs='?',type=str,
                        help = 'Enable/Disable hotel\'s reviews scraping',
                        metavar = '<yes/no>',
                        dest = 'scrap_reviews',
                        const = 'yes',
                        default = None,
                        action = 'store')

    parser.add_argument('--deals', nargs='?', type=str,
                        help = 'Enable/Disable hotel\'s deals scraping',
                        metavar = '<yes/no>',
                        dest = 'scrap_deals',
                        const = 'yes',
                        default = None,
                        action = 'store')

    parser.add_argument('--geo', nargs='?', type=str,
                        help = 'Enable/Disable request info geolocation of TripAdvisor hotels from GoogleMaps API',
                        metavar = '<true/false>',
                        dest = 'scrap_geo',
                        const = 'yes',
                        default = None,
                        action = 'store')

    parser.add_argument('--gmaps-api-key', nargs='?', type=str,
                        help = 'Configure GoogleMaps API key',
                        metavar = '<API Key>',
                        dest = 'google_maps_api_key',
                        action = 'store')

    args = vars(parser.parse_args(args))

    # Sobrecargamos las opciones pasadas por línea de comandos a la configuración global.
    local_config = Config()

    if not args['config_file'] is None:
        try:
            config_file = abspath(normpath(join(getcwd(), args['config_file'])))
            local_config.override(Config.load_from_file(config_file))
        except:
            parser.error('Failed to load configuration file')

    if not args['debug'] is None:
        local_config.set_value('ENABLE_DEBUG', args['debug'] == 'yes')

    if not args['scrap_reviews'] is None:
        local_config.set_value('SCRAP_REVIEWS', args['scrap_reviews'] == 'yes')

    if not args['scrap_deals'] is None:
        local_config.set_value('SCRAP_DEALS', args['scrap_deals'] == 'yes')

    if not args['scrap_geo'] is None:
        local_config.set_value('SCRAP_GEO', args['scrap_geo'] == 'yes')

    if not args['google_maps_api_key'] is None:
        local_config.set_value('GOOGLE_MAPS_API_KEY', args['google_maps_api_key'])

    if local_config.is_true('SCRAP_GEO') and not local_config.is_set('GOOGLE_MAPS_API_KEY'):
        parser.error('You must specify Google Maps API Key')

    GlobalConfig().override(local_config)

    # Parseamos también opciones adicionales para el scraper
    terms = args['terms']
    locations = args['locations']

    if not ((not locations is None) != (not terms is None)):
        parser.error('You must specify only terms or locations parameter')

    if not locations is None:
        locations = ', '.join(locations)
    if not terms is None:
        terms = ' '.join(terms)


    # Ejecutamos el scraper
    process = CrawlerProcess(get_project_settings())
    process.crawl(TripAdvisorHotelSpider, terms = terms, locations = locations)
    process.start()


if __name__ == '__main__':
    '''
    La ejecución de este script, invoca el método crawl pasandole como parámetros los argumentos
    de entrada del script.
    '''
    from sys import argv

    args = argv[1:]
    crawl(*args)