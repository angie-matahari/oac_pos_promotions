# -*- coding: utf-8 -*-
{
    'name': "POS Promotions",

    'summary': """
        Allows one to construct POS Promotions for POS Orders""",

    'description': """
        Allows one to construct POS Promotions for POS Orders

        Promotions are automatically applied on orders based on products
        purchased and added to the receipt
    """,

    'author': "Angela Mathare",

    'category': 'Sales/Point of Sale',
    'version': '0.1',

    'depends': ['base', 'point_of_sale'],

    'data': [
        'security/ir.model.access.csv',
        'data/promotion_cron.xml',
        'views/pos_promotion_views.xml',
        'views/pos_promotion_templates.xml'
    ],
    'qweb': [
        'static/src/xml/OrderManagementScreen/OrderlineDetails.xml',
        'static/src/xml/ProductScreen/OrderLine.xml',
        'static/src/xml/ReceiptScreen/OrderReceipt.xml'
    ],
    'installable': True
}
