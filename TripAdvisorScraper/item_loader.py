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
SOFTWARE
'''

from scrapy.loader import ItemLoader as ScrapyItemLoader

class ItemLoader(ScrapyItemLoader):
    '''
    Esta clase es un wrapper sobre la clase ItemLoader de scrapy.
    Tiene una funcionalidad añadida: Comprueba al calcular finalmente los valores de
    los campos del item, si están presentes o no. Si algún campo no está presente y se ha
    marcado como obligatorio, se genera una excepción al cargar el item (de tipo ValueError)
    Los campos pueden marcarse como obligatorios pasandoles el atributo "mandatory" a True en
    la declaración del mismo (clase Item)
    '''
    def __init__(self, *args, **kwargs):
        '''
        Inicializa la instancia.
        :param args:
        :param kwargs:
        '''
        super().__init__(*args, **kwargs)


    def load_item(self):
        item = super().load_item()

        for field_name in item.fields:
            field = item.fields[field_name]
            if 'mandatory' in field and field['mandatory']:
                if item.get(field_name) is None:
                    raise ValueError('Missing attribute "{}" on item'.format(field_name))
        return item