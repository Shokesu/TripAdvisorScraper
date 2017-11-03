

var map_centered = false;
var hotel_ids = [];


initMap = function() {
    var map_center = {lat : 42.8127438, lng : -1.6481762};
    map = new google.maps.Map(document.getElementById('map'), {
      zoom: 0,
      center: map_center
    });

    function callback(response) {
        geo_data = response['geo-data'];
        geo_data.forEach(function(data) {
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

        scrap_finished = response['scrap_finished'];
        if(scrap_finished)
            clearInterval(get_geo_data_interval);
    }
    get_geo_data_interval = setInterval(function() {
        $.getJSON({ url : '/get-geo-data',
                    success : callback});
    }, 2000);
}


function addNewHotel(name, latitude, longitude, info) {
    coords = {lat : latitude, lng : longitude}
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

$(document).ready(function() {
    $('body').append('<script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAEu9td1J35_Gd4nxADmnaNA4kTBLzBQVY&callback=initMap"></script>');
});