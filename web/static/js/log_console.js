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


/*
Este script se encarga de actualizar el panel donde pueden verse los mensajes de depuración
del scraper
*/


// Esta variable sirve para evitar añadir logs varias veces a la consola.
var current_log_message_index = 0;

$(document).ready(function() {
    // Hacemos un petición del log del scraper cada cierto intervalo de tiempo.
    function callback(logs) {
        logs.slice(current_log_message_index, logs.length).forEach(function(message) {
            debug(message);
        });

        current_log_message_index = logs.length;

        // Si el scraper ya ha finalizado, no hacemos más peticiones
        if(scraper_finished) {
            clearInterval(get_logs_interval);
        }
    }

    function get_logs() {
        $.getJSON({ url : '/logs',
                    data : 't=' + Date.now(),
                    success : callback});
    }

    get_logs_interval = setInterval(get_logs, 2500);
});

/**
Esta función añade un mensaje de depuración a la consola */
function debug(message) {
    $('#logs').append('<li>' + message + '</li>');
    elem = $('#logs').get(0);
    elem.scrollTop = elem.scrollHeight;
}