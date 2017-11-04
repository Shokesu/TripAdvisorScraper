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

/**
Este script implementa la lógica de los botones para descargar los datos escrapeados
*/


$(document).ready(function() {
    $('#download-all-data').click(function() {
        $('#download-data-panel-info').html('<p>Get all scraped data from TripAdvisor</p>');
    });

    $('#download-data').click(function() {
        $('#download-data-panel-info').html('<p>Get current avaliable scraped data from TripAdvisor</p>');
    });
});


(function(){
    var $content = $('.modal_info').detach();

    $('.open_button').on('click', function(e){
        modal.open({
            content: $content,
            width: 540,
            height: 270,
        });
        $content.addClass('modal_content');
        $('.modal, .modal_overlay').addClass('display');
        $('.open_button').addClass('load');
    });
}());

var modal = (function(){
    var $close = $('<button role="button" class="modal_close" title="Close"><span></span></button>');
    var $content = $('<div class="modal_content"/>');
    var $modal = $('<div class="modal"/>');
    var $window = $(window);

    $modal.append($content, $close);

    $close.on('click', function(e){
        $('.modal').addClass('conceal');
        $('.modal, .modal_overlay').removeClass('display');
        $('.open_button').removeClass('load');
        e.preventDefault();
        modal.close();
    });

    return {
        center: function(){
            var top = Math.max($window.height() - $modal.outerHeight(), 0) / 2;
            var left = Math.max($window.width() - $modal.outerWidth(), 0) / 2;
            $modal.css({
            top: top + $window.scrollTop(),
            left: left + $window.scrollLeft(),
            });
        },
        open: function(settings){
            $content.empty().append(settings.content);

            $modal.css({
            width: settings.width || 'auto',
            height: settings.height || 'auto'
            }).appendTo('body');

            modal.center();
            $(window).on('resize', modal.center);
        },
        close: function(){
            $content.empty();
            $modal.detach();
            $(window).off('resize', modal.center);
        }
    };
}());