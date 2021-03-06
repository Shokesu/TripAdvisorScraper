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
Este script ejecuta el cliente web del scraper de TripAdvisor usando el framework Flask
'''

from flask import Flask, render_template, request, redirect, make_response
from os.path import dirname, join, abspath
import json
import sqlite3 as sqlite
from web.scraper import TripAdvisorScraper
from TripAdvisorScraper.config.config import GlobalConfig, Config
from TripAdvisorScraper.item_db import TripAdvisorDB



# Raíz de la aplicación flask
root_path = abspath(dirname(__file__))


# Configuración de directorios de recursos

# Directorio donde se buscarán recursos estáticos.
static_folder = join(root_path, 'static')

# Directorio donde se encuentran los templates
template_folder = join(root_path, 'templates')



class FlaskProxy(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        self.init()
        super().run(*args, **kwargs)

    def init(self):
        GlobalConfig().override(Config.load_from_file(join(dirname(__file__), 'scraper.conf.py')))


app = FlaskProxy('TripAdvisorFlaskApp',
                 static_folder=static_folder,
                 static_url_path = '/static',
                 template_folder=template_folder,
                 instance_relative_config=False,
                 root_path=root_path)


@app.route('/')
def index():
    '''
    La ruta "/" devuelve la página principal de la web
    :return:
    '''
    context = {}
    return render_template('index.html', **context)




@app.route('/start', methods = ['GET'])
def start_scraper():
    '''
    Hacer una petición sobre la ruta "/start" hacer que se ejecute el
    scraper de TripAdvisor. El usuario luego será redireccionado a la
    ruta "/view-data"
    :return:
    '''
    try:
        if not 'location' in request.args:
            raise Exception()
        location = request.args['location']
    except:
        raise Exception('Invalid parameters')

    # Empezar a escrapear datos de TripAdvisor
    location = request.args['location']
    TripAdvisorScraper().search_by_location(location)

    return redirect('/view-data')



@app.route('/view-data', methods = ['GET'])
def view_data():
    '''
    Sobre la ruta "/view-data" se sirve una página en la que el usuario
    puede visualizar de forma gráfica los datos escrapeados.
    :return:
    '''
    #if not TripAdvisorScraper().is_running():
    #    return redirect('/')
    context = {}
    context['location'] = TripAdvisorScraper().get_current_search_location()
    return render_template('view_data.html', **context)





@app.route('/data', methods = ['GET'])
def get_data():
    '''
    Una petición GET a esta ruta ("/data") devolverá información sobre los hoteles
    escrapeados en TripAdvisor.
    :return:
    '''
    try:
        with sqlite.connect(GlobalConfig().get_path('OUTPUT_SQLITE')) as db:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, name, address, latitude, longitude
                FROM hotel_geo AS geo INNER JOIN hotel_info as info ON geo.hotel_id = info.id 
                """)
            hotel_data = []
            for register in cursor.fetchall():
                id, name, address, latitude, longitude = register
                hotel_data.append({
                    'id' : id,
                    'name' : name,
                    'address' : address,
                    'latitude' : latitude,
                    'longitude' : longitude
                })

            cursor.execute('SELECT COUNT(*) FROM hotel_info')
            num_hotels, = cursor.fetchone()

            cursor.execute('SELECT COUNT(*) FROM hotel_deal')
            num_deals, = cursor.fetchone()

            cursor.execute('SELECT COUNT(*) FROM hotel_review')
            num_reviews, = cursor.fetchone()

            cursor.execute('SELECT COUNT(*) FROM hotel_geo')
            num_geolocalized_hotels, = cursor.fetchone()


    except Exception as e:
        hotel_data = []
        num_hotels = 0
        num_geolocalized_hotels = 0
        num_deals = 0
        num_reviews = 0

    return json.dumps({ 'hotel-data' : hotel_data,
                        'meta' : {
                            'num_hotels' : num_hotels,
                            'num_geolocalized_hotels' : num_geolocalized_hotels,
                            'num_deals' : num_deals,
                            'num_reviews' : num_reviews
                        },
                        'scraper_finished' : not TripAdvisorScraper().is_running() })



@app.route('/logs', methods = ['GET'])
def get_log():
    '''
    Sobre la ruta "/logs" se sirve el log del scraper.
    :return:
    '''
    logs = ['./scraper --search-by-location="{}"'.format(TripAdvisorScraper().get_current_search_location())]
    try:
        with open(join(dirname(__file__), 'log', 'scraper.log'), 'r') as fh:
            logs += fh.read().split('\n')
    except:
        pass

    return json.dumps(logs)


@app.route('/get-json-data', methods = ['GET'])
def get_json():
    '''
    Sobre la ruta "/get-json-data" se obtienen los datos escrapeados en formato JSON
    :return:
    '''
    try:
        with TripAdvisorDB(db_path = GlobalConfig().get_path('OUTPUT_SQLITE')) as db:
            data = db.get_everything()
    except:
        data = []

    response = make_response(json.dumps(data))
    response.headers['Content-Disposition'] = 'attachment; filename=tripadvisor.json'
    return response


@app.route('/get-sqlite-data', methods = ['GET'])
def get_sqlite():
    '''
    Sobre la ruta "/get-sqlite-data" se obtiene el fichero de base de datos sqlite con los
    datos escrapeados hasta el momento
    :return:
    '''
    try:
        with open(GlobalConfig().get_path('OUTPUT_SQLITE'), 'rb') as fh:
            data = fh.read()
    except:
        return 'Error fetching sqlite file database'

    response = make_response(data)
    response.headers['Content-Disposition'] = 'attachment; filename=tripadvisor.db'
    return response

if __name__ == '__main__':
    '''
    Para iniciar el servidor Flask, ejecutar este script
    '''
    app.run()


