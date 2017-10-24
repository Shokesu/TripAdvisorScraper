/**
Esta función se pone a la escucha en el DOM y comprueba cuando se añaden nuevos elementos.
:param selector Este parámetro sirve para filtrar que nuevos elementos queremos escuchar.
Si este selector por ejemplo es 'p', solo se escucharán nuevas insercciones en el DOM de elementos
que encajen con ese selector.
:param callback Es el callback que se invocará por cada insercción escuchada que encaje con el
selector. Se pasará como valor "this" como el elemento insertado.
*/
onElementInserted = function(selector, callback) {
    var mutationObserver = new MutationObserver(function(records, observer) {
        records.forEach(function(record) {
            if(record.type == 'childList') {
                var elements = Array.from(record.addedNodes);
                elements.filter(function(element) {
                    return $(element).is(selector);
                }).forEach(function(insertedElement) {
                    callback.apply(insertedElement);
                });
            }
        });
    });
    mutationObserver.observe(document.body, {'childList' : true, 'subtree' : true});
}

/**
Este método permite escuchar cambios en los atributos de algunos elementos del DOM de la página.
:param selector Permite filtrar que elementos queremos escuchar
:param attrName Indica el nombre del atributo que queremos ver si es modificado en los elementos
:param callback Es un método que será invocado cuando se haga una modificación del atributo indicado
en alguno de los elementos que encajen con el selector (se invocará una vez por cada modificación)
Se pasa "this" como valor y será el elemento cuyo atributo ha sido modificado.
*/
onAttrChanged = function(selector, attrName, callback) {
    var mutationObserver = new MutationObserver(function(records, observer) {
        records.forEach(function(record) {
            if(record.type == 'attributes' && $(record.target).is(selector) &&
            record.attributeName == attrName) {
                callback.apply(record.target, record.oldValue);
            }
        });
    });
    $(selector).each(function() {
        mutationObserver.observe(this, {'attributes' : true});
    });
}


/**
Es igual que onElementInserted, solo que también se comprueba si actualemente en el DOM existe
algún elemento que encaje con el selector indicado. En tal caso, se llama inmediatamente el callback
que se pasa como parámetro.
*/
onElementAvaliable = function(selector, callback) {
    $(selector).each(function() {
        callback.apply(this);
    });
    onElementInserted(selector, callback);
}


/**
Es igual que onElementAvaliable, solo que en vez de pasar un selector, se pasa una lista de selectores
y el callback solo se ejecuta 1 vez (cuando haya un elemento que encaje con cada uno de los selectores
indicados y que estén disponibles en el DOM).
Los selectores deben ser distintos.
*/
allElementsAvaliable = function(selectors, callback) {
    var __callback = callback;
    var ignore_call = false;
    var __callback_proxy = function() {
        if(!ignore_call)
        {
            ignore_call = true;
            __callback();
        }
    }
    var matched_selectors = []
    var callback = function() {
        var element = this;
        selectors.filter(function(selector) {
            return $(element).is(selector);
        }).forEach(function(selector) {
            if(matched_selectors.indexOf(selector) == -1)
                matched_selectors.push(selector);
        });
        if(matched_selectors.length == selectors.length)
            __callback_proxy();

    }
    onElementAvaliable(selectors.join(','), callback);
}


/**
Este método ejecuta un callback cuando se añade un manejador del evento 'click' o se establece
el atributo "onclick" sobre un elemento por cada selector que se especifique como parámetro.
Los selectores deben ser distintos.
*/
allElementsClickHandled = function(selectors, callback) {
    var ignore_call = false;
    var callback_proxy = function() {
        if(!ignore_call)
        {
            ignore_call = true;
            callback();
        }
    }

    var matched_selectors = selectors.filter(function(selector) {
        return $(selector).filter(function() {
            var onclick = $(this).attr('onclick');
            var click_event_handled = $(this).attr('click_handled');
            return onclick || click_event_handled;

        }).length > 0;
    });
    if(matched_selectors.length == selectors.length) {
        callback();
    }
    else {

        var remaining_selectors = selectors.filter(function(selector) {
            return matched_selectors.indexOf(selector) == -1;
        });
        remaining_selectors.forEach(function(selector) {
            $(selector).on('click_event_handled', function() {

                matched_selectors.push(selector);
                if(matched_selectors.length == selectors.length) {
                    callback_proxy();
                }
            });

        onAttrChanged(remaining_selectors.join(','), 'onclick', function() {
            if(!$(this).attr('onclick'))
                return;
            var element = this;
            selectors.filter(function(selector) {
                return $(element).is(selector);
            }).forEach(function(selector) {
                matched_selectors.push(selector);
                if(matched_selectors.length == selectors.length) {
                    callback_proxy();
                }
            });
        });


        });
    }
}


onInputHasValue = function(selector, value, callback) {
    var element = $(selector).get(0)
    if($(element).val() == value)
        callback();
    else
    {
        var change_handler = function() {
            if($(this).val() == value)
            {
                $(this).off('change paste keyup input', change_handler);
                callback();
            }
        }
        $(element).on('change paste keyup input', change_handler);
    }
}

Element.prototype._addEventListener = Element.prototype.addEventListener;
Element.prototype.addEventListener = function(eventName, callback, useCapture) {
    this._addEventListener(eventName, callback, useCapture);
    if(eventName == 'click')
    {
        $(this).trigger('click_event_handled');
        $(this).attr('click_handled', true);
    }
};