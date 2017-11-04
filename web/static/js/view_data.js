/*
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
*/


// Esta variable indicará si el mapa está centrado en los marcadores de los hoteles escrapeados.
var map_centered = false;

// Esta variable auxiliar se usará para almacenar las IDs de los hoteles mostrados actualmente
// en el mapa de google.
var hotel_ids = [];

// Esta variable indicará si el scraper ha finalizado o no la ejecución
scraper_finished = false;


// Este método es invocado una vez que el mapa de google se haya generado. Inicializa el mapa.
initMap = function() {
    // Indicamos el zoom y una localización arbitraria como centro del mapa por el momento.
    var map_center = {lat : 42.8127438, lng : -1.6481762};
    map = new google.maps.Map(document.getElementById('map'), {
      zoom: 0,
      center: map_center
    });


    // Cada cierto intervalo de tiempo, hacemos una request al servidor y pedimos los datos
    // de los hoteles escrapeados + metainformación

    // Este callback se ejecuta cada vez que se recibe una respuesta del servidor a nuestra petición.
    function callback(response) {

        // Obtenemos metainformación
        var meta = response['meta'];
        var num_hotels = meta['num_hotels'];
        var num_geolocalized_hotels = meta['num_geolocalized_hotels'];
        var num_deals = meta['num_deals'];
        var num_reviews = meta['num_reviews'];
        scraper_finished = response['scraper_finished'];


        // Actualizamos la tabla de información
        update_info_table(num_hotels, num_geolocalized_hotels, num_deals, num_reviews);

        // Actualizamos la tabla de información de estado
        update_status_table();


        // Obtenemos la información de los hoteles.
        var hotel_data = response['hotel-data'];


        // Añadimos marcadores al mapa por cada hotel escrapeado.
        hotel_data.forEach(function(data) {
            var name = data['name'];
            var latitude = data['latitude'];
            var longitude = data['longitude'];
            var id = data['id'];
            var address = data['address'];
            var info = '<p class="hotel_name">' + name + '</p>' + '<p class="hotel_address">' + address + '</p>';

            if(hotel_ids.indexOf(id) == -1) {
                hotel_ids.push(id);
                addNewHotel(name, latitude, longitude, info);
            }

        });

        // Comprobamos si el scraper ha finalizado. En tal caso, no hacemos más requests al servidor
        // para pedir datos.
        if(scraper_finished)
            clearInterval(get_data_interval);
    }


    function get_data() {
        $.getJSON({ url : '/data',
                    data : 't=' + Date.now(),
                    success : callback});
    }

    get_data_interval = setInterval(get_data, 2500);
}

/**
Esta función se encarga de añadir un marcador al mapa de google asociado a un hotel de TripAdvisor
escrapeado.
@param name: Es el nombre del hotel
@param latitude, longitude: Geolocalización del hotel
@param info: Es código HTML o texto plano, que se insertará en la etiqueta que aparece al clickar sobre el marcador
del hotel.
*/
function addNewHotel(name, latitude, longitude, info) {
    var coords = {lat : latitude, lng : longitude}
    var marker = new google.maps.Marker({
        position : coords,
        map : map,
        title : name
    });

    if(!map_centered)
    {
        map_centered = true;
        map.setCenter(coords);
        map.setZoom(14);
    }

    var infowindow = new google.maps.InfoWindow({
      content: info
    });

    marker.addListener('click', function() {
        infowindow.open(map, marker);
    });
}

function update_info_table(num_hotels, num_geolocalized_hotels, num_deals, num_reviews) {
    var num_deals_per_hotel = num_deals / num_hotels ? num_hotels > 0 : 0;
    var num_reviews_per_hotel = num_reviews / num_hotels ? num_hotels > 0 : 0;

    if(num_hotels > 0)
        $('#num-hotels').html('<b>' + num_hotels + '</b> (' + (num_hotels > num_geolocalized_hotels ? '<b>' + num_geolocalized_hotels + '</b>' : 'all') + ' of them geolocalized' + ')');
    else
        $('#num-hotels').html('<b>0</b>');


    if(num_deals > 0)
        $('#num-deals').html('<b>' + num_deals + '</b> (a mean of ' + num_deals_per_hotel  + ' per hotel)');
    else
        $('#num-deals').html('<b>0</b>');


    if(num_reviews > 0)
        $('#num-reviews').html('<b>' + num_reviews + '</b> (a mean of ' + num_reviews_per_hotel  + ' per hotel)');
    else
        $('#num-reviews').html('<b>0</b>');

}

function update_status_table() {
    if(!scraper_finished)
        $('#status').html('<span class="status-running-label">Running</span>');
    else
        $('#status').html('<span class="status-done-label">Done</span>');
}

// Este trozo de código añade el mapa de google a la página.
$(document).ready(function() {
    $('body').append('<script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAEu9td1J35_Gd4nxADmnaNA4kTBLzBQVY&callback=initMap"></script>');
});

