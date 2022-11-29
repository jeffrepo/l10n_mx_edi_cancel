# -*- coding: utf-8 -*-
import base64
from zeep import Client
from zeep.transports import Transport
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Picking(models.Model):
    _inherit = 'stock.picking'

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





class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'


    def _l10n_mx_edi_finkok_cancel(self, move, credentials, cfdi):
        return self._l10n_mx_edi_finkok_cancel_service(move,move.l10n_mx_edi_cfdi_uuid, move.company_id, credentials)

    def _l10n_mx_edi_finkok_cancel_service(self, move, uuid, company, credentials):
       
        l10n_mx_edi_cfdi_motivo = move.move_type=='entry' and move.payment_id.l10n_mx_edi_cfdi_motivo or move.l10n_mx_edi_cfdi_motivo
        l10n_mx_edi_cfdi_relacionado = move.move_type=='entry' and move.payment_id.l10n_mx_edi_cfdi_relacionado or move.l10n_mx_edi_cfdi_relacionado
        if not l10n_mx_edi_cfdi_motivo:
            return {
                'errors': [_('No se puede cancelar sin motivo de cancelación.')],
            }


        certificates = move.company_id.l10n_mx_edi_certificate_ids
        certificate = certificates.sudo().get_valid_certificate()
        cer_pem = certificate.get_pem_cer(certificate.content)
        key_pem = certificate.get_pem_key(certificate.key, certificate.password)
        try:
            transport = Transport(timeout=20)
            client = Client(credentials['cancel_url'], transport=transport)
            invoice_obj = client.get_type('ns1:UUID')()
            invoice_obj.UUID = uuid
            if l10n_mx_edi_cfdi_motivo in ['01']:
                invoice_obj.FolioSustitucion=l10n_mx_edi_cfdi_relacionado.l10n_mx_edi_cfdi_uuid
            invoice_obj.Motivo=l10n_mx_edi_cfdi_motivo
            invoices_list = client.get_type('ns1:UUIDS')(invoice_obj)
            response = client.service.cancel(
                invoices_list,
                credentials['username'],
                credentials['password'],
                company.vat,
                cer_pem,
                key_pem,
            )
        except Exception as e:
            return {
                'errors': [_("The Finkok service failed to cancel with the following error: %s", str(e))],
            }

        if not getattr(response, 'Folios', None):
            code = getattr(response, 'CodEstatus', None)
            msg = _("Cancelling got an error") if code else _('A delay of 2 hours has to be respected before to cancel')
        else:
            code = getattr(response.Folios.Folio[0], 'EstatusUUID', None)
            cancelled = code in ('201', '202')  # cancelled or previously cancelled
            # no show code and response message if cancel was success
            code = '' if cancelled else code
            msg = '' if cancelled else _("Cancelling got an error")

        errors = []
        if code:
            errors.append(_("Code : %s") % code)
        if msg:
            errors.append(_("Message : %s") % msg)
        if errors:
            return {'errors': errors}

        return {'success': True}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
