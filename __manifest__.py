# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cancelacion cfdi',
    'version' : '11.0',
    'summary': 'Cancelacion cfdi',
    'sequence': 30,
    'description': """
    Cancelar  con el nuevo metodo en el PAC
    """,
    'category' : 'Tools',
    'website': 'http://zeval.com.mx/',
    'author': 'silvau',
    'depends' : ['l10n_mx_edi_stock'],
    'data': [
     'views/account_move_view.xml',
     'views/account_payment_view.xml',
     'views/stock_picking_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
