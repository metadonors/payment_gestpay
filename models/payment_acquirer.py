# -*- coding: utf-8 -*-
# Copyright 2017 Metadonors Srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class PaymentAcquirerGestpay(models.Model):

    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('gestpay', 'GestPay (Banca Sella)')])

    gestpay_shoplogin = fields.Char(string='Shop Login', required_if_provider='gestpay', groups='base.group_user')
    gestpay_apikey = fields.Char(string='Shop Login', required_if_provider='gestpay', groups='base.group_user')
    
    def _get_feature_support(self):
        res = super(PaymentAcquirerGestpay, self)._get_feature_support()
        
        # TODO: Check if it is possible and viable to authorize cards with Gestpay Gateway
        #res['authorize'].append('gestpay')
        res['tokenize'].append('gestpay')
        return res


    @api.multi
    def gestpay_form_generate_values(self, tx_values):
        self.ensure_one()
        gestpay_tx_values = dict(tx_values)
        temp_gestpay_tx_values = {
            'company': self.company_id.name,
            'amount': tx_values['amount'],  # Mandatory
            'currency': tx_values['currency'].name,  # Mandatory anyway
            'currency_id': tx_values['currency'].id,  # same here
            'address_line1': tx_values.get('partner_address'),  # Any info of the partner is not mandatory
            'address_city': tx_values.get('partner_city'),
            'address_country': tx_values.get('partner_country') and tx_values.get('partner_country').name or '',
            'email': tx_values.get('partner_email'),
            'address_zip': tx_values.get('partner_zip'),
            'name': tx_values.get('partner_name'),
            'phone': tx_values.get('partner_phone'),
        }

        gestpay_tx_values.update(temp_gestpay_tx_values)
        return gestpay_tx_values
    
    @api.model
    def gestpay_s2s_form_process(self, data):
        payment_token = self.env['payment.token'].sudo().create({
            'cc_number': data['cc_number'],
            'cc_holder_name': data['cc_holder_name'],
            'cc_expiry': data['cc_expiry'],
            'cc_brand': data['cc_brand'],
            'cvc': data['cvc'],
            'acquirer_id': int(data['acquirer_id']),
            'partner_id': int(data['partner_id'])
        })
        return payment_token

    @api.multi
    def gestpay_s2s_form_validate(self, data):
        self.ensure_one()

        # mandatory fields
        for field_name in ["cc_number", "cvc", "cc_holder_name", "cc_expiry", "cc_brand"]:
            if not data.get(field_name):
                return False
        return True