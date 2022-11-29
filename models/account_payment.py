# -*- coding: utf-8 -*-
import base64
from suds.client import Client
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Account_Payment(models.Model):
    _inherit = 'account.payment'


    l10n_mx_edi_cfdi_motivo=fields.Selection([
        ('01','Comprobante emitido con errores con relación'),
        ('02','Comprobante emitido con errores sin relación'),
        ('03','No se llevó a cabo la operación'),
        ('04','Operación nominativa relacionada en la factura global'),
        ],
        string="Motivo Cancelacion", copy=False)
    l10n_mx_edi_cfdi_relacionado = fields.Many2one('account.payment', string='Cfdi Relacionado x Cancelación', domain=[('l10n_mx_edi_sat_status','in',['valid','undefined']),('l10n_mx_edi_cfdi_uuid','!=','')], copy=False)
    
