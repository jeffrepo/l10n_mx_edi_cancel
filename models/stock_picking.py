# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Picking(models.Model):
    _inherit = 'stock.picking'


    l10n_mx_edi_cfdi_motivo=fields.Selection([
        ('01','Comprobante emitido con errores con relación'),
        ('02','Comprobante emitido con errores sin relación'),
        ('03','No se llevó a cabo la operación'),
        ('04','Operación nominativa relacionada en la factura global'),
        ],
        string="Motivo Cancelacion", copy=False)
    l10n_mx_edi_cfdi_relacionado = fields.Many2one('account.move', string='Cfdi Relacionado x Cancelación', domain=[('l10n_mx_edi_sat_status','in',['valid','undefined']),('l10n_mx_edi_cfdi_uuid','!=','')], copy=False)


    def l10n_mx_edi_action_cancel_delivery_guide(self):
        for record in self:
            pac_name = record.company_id.l10n_mx_edi_pac
            credentials = getattr(self.env['account.edi.format'], '_l10n_mx_edi_get_%s_credentials_company' % pac_name)(record.company_id)
            if credentials.get('errors'):
                record.l10n_mx_edi_error = '\n'.join(credentials['errors'])
                continue

            cfdi_str = record._l10n_mx_edi_get_signed_cfdi_data()
            res = getattr(self.env['account.edi.format'], '_l10n_mx_edi_%s_cancel_service' % pac_name)(record, record.l10n_mx_edi_cfdi_uuid, record.company_id, credentials)
            if res.get('errors'):
                record.l10n_mx_edi_error = '\n'.join(res['errors'])
                continue

            # == Chatter ==
            message = _("The CFDI Delivery Guide has been cancelled.")
            record._message_log(body=message)
            origin = '04|' + record.l10n_mx_edi_cfdi_uuid
            record.write({'l10n_mx_edi_cfdi_uuid': False, 'l10n_mx_edi_error': False, 'l10n_mx_edi_status': 'cancelled', 'l10n_mx_edi_origin': origin})

