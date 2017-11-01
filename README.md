# Descripción
Esta pequeña libería permite scrapear datos de hoteles de la página Web TripAdvisor (https://www.tripadvisor.com/) usando
las librerías Scrapy y Splash.

# Instalación
Una forma de instalación es la siguiente:
- Clona este repositorio en local:
```
git clone https://github.com/Shokesu/TripAdvisorScraper.git
```
- Instala dependencias de la librería usando el fichero requeriments.txt

```
cd TripAdvisorScraper
pip install -r requeriments.txt
```
Si quieres instalar las dependencias en un entorno virtual, puedes usar el comando `virtualenv`.
Hay que asegurarse que el interprete python del entorno virtual tenga la versión 3 o superior.
Ejecutar esté código antes de instalar los requerimientos:
```
venv -p /usr/bin/python3 my_venv
source my_venv/bin/activate
```


# Uso
Se facilita un script en bash "scraper.sh" al que se le pueden pasar argumentos por línea de comandos.
El siguiente código muestra ayuda y todas las opciones que pueden indicarse:
```
cd TripAdvisorScraper
./scraper.sh -h
```

Por ejemplo, queremos scrapear hoteles que satisfagan el siguiente criterio de búsqueda por términos "Hotel Blanca Navarra"
```
./scraper.sh --search-by-terms="Hotel Blanca Navarra"
```
O scrapear hoteles indicando su localización...
```
./scraper.sh --search-by-location="Pamplona, Navarra, Spain"
```

Los datos que se irán obteniendo, se almacenarán en distintos ficheros (JSON, SQLITE), en el directorio data/

- "data/tripadvisor_info.json" Almacena información relativa a los hoteles en formato JSON
- "data/tripadvisor_reviews.json" Almacenas las reviews de los hoteles en formato JSON
- "data/tripadvisor_deals.json" Almacena las deals de los hoteles en formato JSON
- "data/tripadvisor_geo.json" Almacena información de geolocalización de hoteles en formato JSON
- "data/tripadvisor.db" Contiene toda la información scrapeada (es un fichero de base de datos sqlite)
- "data/tripadvisor_bulk.json" Almacena toda la información scrapeada de forma estructurada en formato JSON

Las rutas de estos ficheros se pueden customizar usando ficheros de configuración.




# Configuración del Scraper
Los ficheros de configuración sirven para modificar algunos parámetros del scraper.
Para especificar un fichero de configuración, se puede usar la opción --config en la línea de comandos.
```
./scraper.sh --search-by-location="Madrid, Spain" --config my_config.conf.py
```
Los ficheros de configuración son scripts en python.

e.g:
El scraper extrae información de los hoteles, sus reviews, geolocalizaciòn y ofertas por defecto.
Si por ejemplo queremos obtener solo reviews, podríamos crear la siguiente configuración:
``` 
SCRAP_REVIEWS = True
SCRAP_GEO = False
SCRAP_DEALS = False
```
Las parámetros indicados en la configuración que se pasa como parámetro al scraper, reemplazan los valores por
defecto.

Para ver un listado completo de todos los parámetros de configuración, ver el fichero
https://github.com/Shokesu/TripAdvisorScraper/blob/master/TripAdvisorScraper/config/default.conf.py



