# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_mx_edi_cfdi_motivo=fields.Selection([
        ('01','Comprobante emitido con errores con relación'),
        ('02','Comprobante emitido con errores sin relación'),
        ('03','No se llevó a cabo la operación'),
        ('04','Operación nominativa relacionada en la factura global'),
        ],
        string="Motivo Cancelacion", copy=False)
    l10n_mx_edi_cfdi_relacionado = fields.Many2one('account.move', string='Cfdi Relacionado x Cancelación', domain=[('l10n_mx_edi_sat_status','in',['valid','undefined']),('l10n_mx_edi_cfdi_uuid','!=','')], copy=False)


