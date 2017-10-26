# -*- coding: utf-8 -*-
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

from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst, Join, MapCompose


class TypeConverter:
    '''
    Es una clase de utilidad. Es un processor que puede usarse para definir los campos
    de los items. Sirver para realizar conversiones de tipo de los valores de los campos.
    Las subclases deben implementar el método convert.
    '''
    def convert(self, value):
        '''
        Modifica el tipo de un valor de entrada que se pasa como parámetro
        :param value:
        :return: Devuelve el valor de entrada con su tipo modificado.
        '''
        return value

    def __call__(self, values, loader_context = None):
        next_values = []
        for value in values:
            try:
                next_values.append(self.convert(value))
            except:
                pass
        return next_values

class ToFloat(TypeConverter):
    '''
    Sirve para formatear los campos de los items como valores flotantes
    '''
    def convert(self, value):
        return float(value)

class ToInt(TypeConverter):
    '''
    Sirve para formatear los campos de los items como valores enteros.
    '''
    def convert(self, value):
        return int(value)



class TripAdvisorHotelInfo(Item):
    name = Field(output_processor = TakeFirst(), mandatory = True)
    phone_number = Field(output_processor = TakeFirst(), mandatory = False)
    amenities = Field(output_processor = Join(separator = ', '), mandatory = False)
    id = Field(output_processor = TakeFirst(), mandatory = True)
    address = Field(input_processor = TakeFirst(), output_processor = Join(separator = ', '), mandatory = True)


class TripAdvisorHotelReview(Item):
    title = Field(output_processor = TakeFirst(), mandatory = True)
    rating = Field(input_processor = ToInt(), output_processor = TakeFirst(), mandatory = True)
    text = Field(output_processor = TakeFirst(), mandatory = True)
    hotel_id = Field(output_processor = TakeFirst(), mandatory = True)
    date = Field(output_processor = TakeFirst(), mandatory = True)

class TripAdvisorHotelDeals(Item):
    hotel_id = Field(output_processor = TakeFirst(), mandatory = True)
    provider_name = Field(output_processor = TakeFirst(), mandatory = True)
    price = Field(input_processor = ToFloat(), output_processor = TakeFirst(), mandatory = True)


class TripAdvisorHotelGeolocation(Item):
    hotel_id = Field(output_processor = TakeFirst(), mandatory = True)
    longitude = Field(input_processor = ToFloat(), output_processor = TakeFirst(), mandatory = True)
    latitude = Field(input_processor = ToFloat(), output_processor = TakeFirst(), mandatory = True)