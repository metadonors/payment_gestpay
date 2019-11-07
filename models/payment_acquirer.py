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
