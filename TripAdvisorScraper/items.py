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

import scrapy
from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst, Join

class TripAdvisorHotelInfo(Item):
    name = Field(output_processor = TakeFirst())
    phone_number = Field(output_processor = TakeFirst())
    amenities = Field()
    id = Field(output_processor = TakeFirst())
    address = Field(input_processor = TakeFirst(), output_processor = Join(separator = ', '))


class TripAdvisorHotelReview(Item):
    title = Field(output_processor = TakeFirst(), mandatory = True)
    rating = Field(output_processor = TakeFirst(), mandatory = True)
    text = Field(output_processor = TakeFirst(), mandatory = True)
    hotel_id = Field(output_processor = TakeFirst(), mandatory = True)
    date = Field(output_processor = TakeFirst(), mandatory = True)

class TripAdvisorHotelDeals(Item):
    hotel_id = Field(output_processor = TakeFirst(), mandatory = True)
    provider_name = Field(output_processor = TakeFirst(), mandatory = True)
    price = Field(output_processor = TakeFirst(), mandatory = True)


class TripAdvisorHotelGeolocation(Item):
    hotel_id = Field(output_processor = TakeFirst())
    longitude = Field(output_processor = TakeFirst())
    latitude = Field(output_processor = TakeFirst())