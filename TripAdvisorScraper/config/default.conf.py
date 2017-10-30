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
Esta es la configuración por defecto del scraper de TripAdvisor. Los campos que se especifiquen
en el fichero de configuración que se pase como parámetro al scraper, sustiuirán a los de este.
'''



# CONFIGURACIÓN DE ESCRAPEO


# Activa/Desactiva el escrapeo de las reviews de los hoteles
SCRAP_REVIEWS = True

# Activa/Desactiva el escrapeo de las geolocalizaciones de los hoteles
SCRAP_GEO = True

# Indica la clave API a usar para obtener las geolocalizaciones de los hoteles
# a partir de la información scrapeada de los hoteles (dirección fisica del hotel)
# Esta variable solo es necesaria si SCRAP_GEO está a True
# GOOGLE_MAPS_API_KEY = ''

# Activa/Desactiva el escrapeado de las deals (ofertas) de los hoteles
SCRAP_DEALS = True


# Indica el número máximo de reviews a scrapear por hotel (Si no se especifica, se intentan
# scrapear todas)
# MAX_REVIEWS_PER_HOTEL = 20

# Indica el número máximo de deals a scrapear por hotel (Si no se especifica, se intentan
# scrapear todas)
# MAX_DEALS_PER_HOTEL = 10

# Indica el número máximo de hoteles a escrapear (Si no se especifíca, se intentan
# scrapear todos)
# MAX_HOTELS = 30




# CONFIGURACIÓN DE SALIDA DE DATOS

'''
Las rutas de los ficheros son relativas al directorio padre de este fichero de configuración.
Pueden especificarse rutas relativas y absolutas.
'''

# Si se especifica, la información de las reviews escrapeadas se introducirán en el fichero
# que se indica en esta variable en formato JSON
OUTPUT_REVIEWS_JSON = '../data/tripadvisor_reviews.json'

# Si se especifica, la información de las deals  escrapeadas se introducirán en el fichero
# que se indica en esta variable en formato JSON
OUTPUT_DEALS_JSON = '../data/tripadvisor_deals.json'


# Si se especifica, la información de los hoteles se introducirá en el fichero
# que se indica en esta variable en formato JSON
OUTPUT_HOTEL_INFO_JSON = '../data/tripadvisor_info.json'


# Si se especifica, la información relativa a la geolocalización de los hoteles escrapeados
#se introducirán en el fichero que se indica en esta variable en formato JSON
OUTPUT_HOTEL_GEO_JSON = '../data/tripadvisor_geo.json'


# Si se indica, toda la información guardada se almacenará en una base de datos sqlite, cuya
# ruta se indica en esta variable
OUTPUT_SQLITE = '../data/tripadvisor.db'




# CONFIGURACIÓN DE LOGS Y DEPURACIÓN DEL SCRAPER

# Si se indica, se generarán mensajes de depuración que aparecerán en los logs
ENABLE_DEBUG = False


# Si se indica, los mensajes de depuración y de información del scraper irán a este fichero.
OUTPUT_SCRAP_LOG = '../log/tripadvisor_scrap.log'


# Si se especifica, los mensajes de depuración del módulo encargado de almacenar los datos escrapeados
# en sqlite, irán a este fichero.
OUTPUT_SQLITE_LOG = '../log/tripadvisor_sqlite.log'
