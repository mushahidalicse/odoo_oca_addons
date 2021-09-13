# -*- coding: utf-8 -*-
{
    'name': 'Purchase Order Api',
    'version': '12.0.1.0.0',
    'category': 'Purchase',
    'author': 'SIT & think digital',
    'website': 'http://sitco.odoo.com',
    'sequence': 0,
    'summary': 'Generate api for purchase order',
    'description': """""",
    'depends': [
        'purchase','purchase_request'
    ],
    'data': [
        'views/views.xml',
    ],
    'images': [
        # 'static/description/banner.png',
    ],
    'installable': True,
}
