# -*- coding: utf-8 -*-
# Copyright 2017 Metadonors Srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class PaymentAcquirerGestpay(models.Model):

    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('gestpay', 'GestPay (Banca Sella)')])

    gestpay_shoplogin = fields.Char(string='Shop Login', required_if_provider='gestpay', groups='base.group_user')

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(PaymentAcquirerGestpay, self)._get_feature_support()
        res['tokenize'].append('gestpay')
        return res

    def gestpay_form_generate_values(self, values):
        data = {}
        _logger.error(values)
        data['amount'] = values['amount']
        data['transaction_id'] = values['reference']
        data['buyer_name'] = values['partner_name']
        data['buyer_email'] = values['partner_email']
        
        # TODO add csrf

        return data

    @api.multi
    def gestpay_get_form_action_url(self):
        self.ensure_one()
        return "/payment/gestpay/redirect"

    #################################
    ### S2S
    #################################

    def gestpay_s2s_form_process(self, data):
        values = {
            'cc_number': data.get('cc_number'),
            'cc_cvc': int(data.get('cc_cvc')),
            'cc_holder_name': data.get('cc_holder_name'),
            'cc_expiry': data.get('cc_expiry'),
            'cc_brand': data.get('cc_brand'),
            'acquirer_id': int(data.get('acquirer_id')),
            'partner_id': int(data.get('partner_id'))
        }
        pm_id = self.env['payment.token'].sudo().create(values)
        return pm_id
